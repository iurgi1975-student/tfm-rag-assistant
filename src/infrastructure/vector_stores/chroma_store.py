"""ChromaVectorStore - Implementation of VectorStoreRepository using ChromaDB.

This is the concrete implementation that ChromaDB for persistent vector storage.
It implements the VectorStoreRepository interface from the domain layer.
"""

from typing import List, Optional
from pathlib import Path
import chromadb

from ...domain.repositories import VectorStoreRepository
from ...domain.models import Document, DocumentChunk, ImageContent, SearchResult
from .clip_embeddings import CLIPEmbeddings


class ChromaVectorStore(VectorStoreRepository):
    """ChromaDB implementation of VectorStoreRepository.
    
    Stores vectors persistently using ChromaDB with cosine similarity search.
    Documents are automatically split into chunks for search.
    """
    
    def __init__(
        self,
        persist_dir: str = "./chroma_db",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        use_multimodal: bool = False
    ):
        """Initialize ChromaDB vector store.
        
        Args:
            persist_dir: Directory where Chroma data is stored.
            embedding_model: CLIP model name (default: clip-ViT-B-32).
            use_multimodal: If True, create a separate image collection.
        """
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.use_multimodal = use_multimodal
        
        # Initialize embeddings: CLIP for multimodal, sentence-transformers for text-only
        if use_multimodal:
            self.embeddings = CLIPEmbeddings(model_name=embedding_model)
        else:
            from langchain_huggingface import HuggingFaceEmbeddings
            self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
        
        # Initialize Chroma persistent client
        self.chroma_client = chromadb.PersistentClient(path=str(self.persist_dir))
        
        # Text collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )

        # Image collection (only when multimodal is enabled)
        self.image_collection = None
        if use_multimodal:
            self.image_collection = self.chroma_client.get_or_create_collection(
                name="images",
                metadata={"hnsw:space": "cosine"}
            )
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to Chroma.
        
        Documents are split into chunks and each chunk is embedded.
        
        Args:
            documents: List of Document objects to add.
        """
        if not documents:
            return
        
        # Collect all chunks from all documents
        all_chunks = []
        for doc in documents:
            all_chunks.extend(doc.chunks)
        
        if not all_chunks:
            return
        
        # Extract texts and create embeddings
        texts = [chunk.content for chunk in all_chunks]
        embeddings_list = self.embeddings.embed_documents(texts)
        
        # Prepare data for Chroma
        ids = [chunk.id for chunk in all_chunks]
        metadatas = [chunk.metadata for chunk in all_chunks]
        
        # Add to Chroma
        self.collection.add(
            ids=ids,
            embeddings=embeddings_list,
            metadatas=metadatas,
            documents=texts
        )
    
    def similarity_search(self, query: str, k: int = 4) -> List[SearchResult]:
        """Search for similar documents.
        
        Args:
            query: Search query text.
            k: Number of top results to return.
            
        Returns:
            List of SearchResult objects ranked by similarity.
        """
        if self.collection.count() == 0:
            return []
        
        # Embed the query
        query_embedding = self.embeddings.embed_query(query)
        
        # Search in Chroma
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"]
        )
        
        # Convert to SearchResult objects
        search_results = []
        for i, text in enumerate(results["documents"][0]):
            distance = results["distances"][0][i]
            similarity_score = 1 - distance  # Convert distance to similarity
            metadata = results["metadatas"][0][i] if results["metadatas"][0] else {}
            
            # Create DocumentChunk
            chunk = DocumentChunk(
                id=results["ids"][0][i],
                content=text,
                document_id=metadata.get("document_id", "unknown"),
                chunk_index=metadata.get("chunk_index", 0),
                metadata=metadata
            )
            
            # Create SearchResult
            result = SearchResult(
                chunk=chunk,
                similarity_score=similarity_score,
                rank=i + 1
            )
            search_results.append(result)
        
        return search_results
    
    def add_images(self, images: List[ImageContent], document_id: str) -> None:
        """Add image embeddings to the image collection.

        Args:
            images: List of ImageContent objects with image_path set.
            document_id: ID of the parent document.
        """
        if not self.use_multimodal or self.image_collection is None:
            return
        if not images:
            return

        valid = [img for img in images if img.image_path and Path(img.image_path).exists()]
        if not valid:
            return

        paths = [img.image_path for img in valid]
        embeddings_list = self.embeddings.embed_images(paths)
        ids = [img.id for img in valid]
        metadatas = [
            {
                **img.metadata,
                "document_id": document_id,
                "image_path": img.image_path,
                "image_format": img.image_format,
                "extracted_text": img.extracted_text,
                "thumbnail_path": img.thumbnail_path or "",
            }
            for img in valid
        ]
        documents = [img.extracted_text or img.image_path for img in valid]

        self.image_collection.add(
            ids=ids,
            embeddings=embeddings_list,
            metadatas=metadatas,
            documents=documents
        )

    def search_images(self, query: str, k: int = 4) -> List[SearchResult]:
        """Search the image collection using a text query.

        Args:
            query: Text query to search for similar images.
            k: Number of results to return.

        Returns:
            List of SearchResult objects whose chunk.image_content is set.
        """
        if not self.use_multimodal or self.image_collection is None:
            return []
        if self.image_collection.count() == 0:
            return []

        query_embedding = self.embeddings.embed_query(query)
        results = self.image_collection.query(
            query_embeddings=[query_embedding],
            n_results=min(k, self.image_collection.count()),
            include=["documents", "metadatas", "distances"]
        )

        search_results = []
        for i, doc_text in enumerate(results["documents"][0]):
            distance = results["distances"][0][i]
            similarity_score = 1 - distance
            metadata = results["metadatas"][0][i] if results["metadatas"][0] else {}

            image_content = ImageContent(
                id=results["ids"][0][i],
                image_path=metadata.get("image_path", ""),
                image_format=metadata.get("image_format", "png"),
                thumbnail_path=metadata.get("thumbnail_path") or None,
                extracted_text=metadata.get("extracted_text", ""),
                metadata=metadata,
            )
            chunk = DocumentChunk(
                id=results["ids"][0][i],
                content=doc_text,
                document_id=metadata.get("document_id", "unknown"),
                chunk_index=i,
                content_type="image",
                image_content=image_content,
                metadata=metadata,
            )
            search_results.append(SearchResult(chunk=chunk, similarity_score=similarity_score, rank=i + 1))

        return search_results

    def search_hybrid(
        self,
        query: str,
        k_text: int = 4,
        k_images: int = 4
    ) -> List[SearchResult]:
        """Combined text + image search, ranked by similarity score.

        Args:
            query: Text query.
            k_text: Number of text results.
            k_images: Number of image results.

        Returns:
            Merged and re-ranked list of SearchResult objects.
        """
        text_results = self.similarity_search(query, k=k_text)
        image_results = self.search_images(query, k=k_images)

        combined = text_results + image_results
        combined.sort(key=lambda r: r.similarity_score, reverse=True)

        # Re-rank
        for i, result in enumerate(combined):
            result.rank = i + 1

        return combined

    def clear(self) -> None:
        """Clear all documents from the collection."""
        self.chroma_client.delete_collection(name="documents")
        self.collection = self.chroma_client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        if self.use_multimodal and self.image_collection is not None:
            self.chroma_client.delete_collection(name="images")
            self.image_collection = self.chroma_client.get_or_create_collection(
                name="images",
                metadata={"hnsw:space": "cosine"}
            )
    
    def get_document_count(self) -> int:
        """Get number of documents in the store.
        
        Returns:
            Count of documents.
        """
        try:
            return self.collection.count()
        except Exception:
            # If collection doesn't exist or is empty, return 0
            return 0
    
    def __len__(self) -> int:
        """Return the number of documents via len() operator."""
        return self.get_document_count()
