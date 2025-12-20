"""
Vector store implementation using LangChain's built-in InMemoryVectorStore for RAG system.
"""
import os
from typing import List, Optional, Tuple

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore as LangChainInMemoryVectorStore


class InMemoryVectorStore:
    """Wrapper around LangChain's InMemoryVectorStore for document retrieval."""
    
    def __init__(self, embedding_model: str = "text-embedding-3-small", api_key: Optional[str] = None):
        """Initialize the vector store with an OpenAI embedding model."""
        import os
        
        # Set the API key in environment if provided
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        
        self.embedding_model = OpenAIEmbeddings(model=embedding_model)
        self.vector_store: Optional[LangChainInMemoryVectorStore] = None
        self.documents: List[Document] = []
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the vector store."""
        if not documents:
            return
        
        # Store documents
        self.documents.extend(documents)
        
        if self.vector_store is None:
            # Create new vector store
            self.vector_store = LangChainInMemoryVectorStore(self.embedding_model)
            self.vector_store.add_documents(documents)
        else:
            # Add to existing vector store
            self.vector_store.add_documents(documents)
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Search for similar documents."""
        if self.vector_store is None:
            return []
        
        return self.vector_store.similarity_search(query, k=k)
    
    def similarity_search_with_score(self, query: str, k: int = 4) -> List[Tuple[Document, float]]:
        """Search for similar documents with relevance scores."""
        if self.vector_store is None:
            return []
        
        return self.vector_store.similarity_search_with_score(query, k=k)
    
    def clear(self) -> None:
        """Clear all documents from the vector store."""
        if self.vector_store is not None:
            # Create a new empty vector store
            self.vector_store = LangChainInMemoryVectorStore(self.embedding_model)
        self.documents = []
    
    def get_document_count(self) -> int:
        """Get the number of documents in the store."""
        return len(self.documents)
    
    def __len__(self) -> int:
        """Return the number of documents in the store."""
        return self.get_document_count()


class RAGRetriever:
    """RAG retriever that combines vector search with relevance filtering."""
    
    def __init__(self, vector_store: InMemoryVectorStore, min_score: float = 0.3):
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
