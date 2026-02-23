"""ChromaVectorStore - Implementation of VectorStoreRepository using ChromaDB.

This is the concrete implementation that ChromaDB for persistent vector storage.
It implements the VectorStoreRepository interface from the domain layer.
"""

from typing import List, Optional
from pathlib import Path
import chromadb
from langchain_huggingface import HuggingFaceEmbeddings

from ...domain.repositories import VectorStoreRepository
from ...domain.models import Document, DocumentChunk, SearchResult


class ChromaVectorStore(VectorStoreRepository):
    """ChromaDB implementation of VectorStoreRepository.
    
    Stores vectors persistently using ChromaDB with cosine similarity search.
    Documents are automatically split into chunks for search.
    """
    
    def __init__(
        self,
        persist_dir: str = "./chroma_db",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        """Initialize ChromaDB vector store.
        
        Args:
            persist_dir: Directory where Chroma data is stored.
            embedding_model: HuggingFace embedding model name.
        """
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
        
        # Initialize Chroma persistent client
        self.chroma_client = chromadb.PersistentClient(path=str(self.persist_dir))
        
        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="documents",
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
    
    def clear(self) -> None:
        """Clear all documents from the collection."""
        self.chroma_client.delete_collection(name="documents")
        self.collection = self.chroma_client.get_or_create_collection(
            name="documents",
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
    
    def get_all_document_names(self) -> List[str]:
        """Get list of all unique document names in the store.
        
        Returns:
            List of unique document filenames (PDFs) or sources.
            Includes manual text inputs with a counter.
        """
        try:
            if self.collection.count() == 0:
                return []
            
            # Get all metadata from the collection
            all_data = self.collection.get(include=["metadatas"])
            
            if not all_data or not all_data.get("metadatas"):
                return []
            
            # Extract unique document names and count manual inputs
            document_names = set()
            manual_input_count = 0
            
            for metadata in all_data["metadatas"]:
                # Try filename first (for PDFs), then source
                doc_name = metadata.get("filename") or metadata.get("source")
                
                if not doc_name:
                    continue
                
                # Count manual inputs separately
                if doc_name in ["text_input", "manual_input"]:
                    manual_input_count += 1
                else:
                    # Extract basename if it's a path
                    if "/" in doc_name or "\\" in doc_name:
                        doc_name = Path(doc_name).name
                    document_names.add(doc_name)
            
            # Build result list
            result = sorted(list(document_names))
            
            # Add manual inputs summary if any exist
            if manual_input_count > 0:
                # Count unique manual text chunks
                manual_chunks = sum(1 for m in all_data["metadatas"] 
                                   if m.get("source") in ["text_input", "manual_input"] 
                                   or m.get("filename") in ["text_input", "manual_input"])
                result.append(f"📝 Manual text inputs ({manual_chunks} chunks)")
            
            return result
            
        except Exception:
            return []
    
    def __len__(self) -> int:
        """Return the number of documents via len() operator."""
        return self.get_document_count()
