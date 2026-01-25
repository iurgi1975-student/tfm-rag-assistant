"""
Vector store implementation using ChromaDB for RAG system.

ChromaDB provides persistent vector storage with automatic embeddings.
Data is saved to disk for long-term persistence.
"""
import os
from pathlib import Path
from typing import List, Optional, Tuple
import logging

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
import chromadb

logger = logging.getLogger(__name__)


class ChromaVectorStore:
    """Wrapper around ChromaDB for document retrieval with persistent storage."""
    
    def __init__(
        self,
        persist_dir: str = "./chroma_db",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        api_key: Optional[str] = None
    ):
        """Initialize the Chroma vector store with persistent storage.
        
        Args:
            persist_dir: Directory where Chroma data will be stored.
            embedding_model: HuggingFace embedding model name.
            api_key: Optional API key (for future compatibility).
        """
        # Set the API key in environment if provided
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        
        # Create persist directory if it doesn't exist
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
        
        # Initialize Chroma client with persistent storage
        self.chroma_client = chromadb.PersistentClient(path=str(self.persist_dir))
        
        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"ChromaVectorStore initialized with persist_dir={persist_dir}")
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the Chroma vector store.
        
        Args:
            documents: List of LangChain Document objects to add.
        """
        if not documents:
            logger.warning("No documents provided to add_documents()")
            return
        
        # Embed documents
        texts = [doc.page_content for doc in documents]
        embeddings = self.embeddings.embed_documents(texts)
        
        # Create metadata
        metadatas = [doc.metadata for doc in documents]
        ids = [
            f"doc_{i}_{hash(doc.page_content) % 10000}"
            for i, doc in enumerate(documents)
        ]
        
        # Add to Chroma
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=texts
        )
        
        logger.info(f"Added {len(documents)} documents to Chroma")
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Search for similar documents.
        
        Args:
            query: The search query string.
            k: Number of results to return.
            
        Returns:
            List of Document objects ranked by similarity.
        """
        if self.collection.count() == 0:
            logger.warning("Vector store is empty")
            return []
        
        # Embed query
        query_embedding = self.embeddings.embed_query(query)
        
        # Search in Chroma
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )
        
        # Convert back to Document objects
        documents = []
        for i, doc_text in enumerate(results["documents"][0]):
            metadata = results["metadatas"][0][i] if results["metadatas"][0] else {}
            documents.append(Document(
                page_content=doc_text,
                metadata=metadata
            ))
        
        return documents
    
    def similarity_search_with_score(self, query: str, k: int = 4) -> List[Tuple[Document, float]]:
        """Search for similar documents with relevance scores.
        
        Args:
            query: The search query string.
            k: Number of results to return.
            
        Returns:
            List of tuples (Document, score) where score is between 0 and 1.
        """
        if self.collection.count() == 0:
            logger.warning("Vector store is empty")
            return []
        
        # Embed query
        query_embedding = self.embeddings.embed_query(query)
        
        # Search in Chroma
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"]
        )
        
        # Convert distances to similarity scores (0-1 range)
        documents_with_scores = []
        for i, doc_text in enumerate(results["documents"][0]):
            distance = results["distances"][0][i]
            # Convert distance to similarity (1 - distance)
            similarity = 1 - distance
            metadata = results["metadatas"][0][i] if results["metadatas"][0] else {}
            
            documents_with_scores.append((
                Document(page_content=doc_text, metadata=metadata),
                similarity
            ))
        
        return documents_with_scores
    
    def clear(self) -> None:
        """Clear all documents from the vector store."""
        # Delete and recreate collection
        self.chroma_client.delete_collection(name="documents")
        self.collection = self.chroma_client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        logger.info("Cleared Chroma vector store")
    
    def get_document_count(self) -> int:
        """Get the number of documents in the store."""
        return self.collection.count()
    
    def __len__(self) -> int:
        """Return the number of documents in the store."""
        return self.get_document_count()


class RAGRetriever:
    """RAG retriever that combines vector search with relevance filtering."""
    
    def __init__(self, vector_store: ChromaVectorStore, min_score: float = 0.3):
        """Initialize the RAG retriever.
        
        Args:
            vector_store: The vector store to retrieve from
            min_score: Minimum similarity score (0-1, higher is more similar for cosine similarity)
        """
        self.vector_store = vector_store
        self.min_score = min_score
    
    def retrieve(self, query: str, k: int = 4) -> List[Document]:
        """Retrieve relevant documents for a query."""
        # Get documents with scores
        docs_with_scores = self.vector_store.similarity_search_with_score(query, k=k)
        
        # Filter by minimum score (higher scores are better in cosine similarity)
        filtered_docs = [
            doc for doc, score in docs_with_scores 
            if score >= self.min_score
        ]
        
        return filtered_docs if filtered_docs else [doc for doc, _ in docs_with_scores[:k//2]]
    
    def get_context(self, query: str, max_tokens: int = 2000) -> str:
        """Get context string for the query, respecting token limits."""
        relevant_docs = self.retrieve(query)
        
        context_parts = []
        current_length = 0
        
        for doc in relevant_docs:
            content = doc.page_content
            # Rough token estimation (1 token ≈ 4 characters)
            content_tokens = len(content) // 4
            
            if current_length + content_tokens > max_tokens:
                # Truncate the last document if needed
                remaining_tokens = max_tokens - current_length
                remaining_chars = remaining_tokens * 4
                content = content[:remaining_chars] + "..."
                context_parts.append(content)
                break
            
            context_parts.append(content)
            current_length += content_tokens
        
        return "\n\n---\n\n".join(context_parts)
