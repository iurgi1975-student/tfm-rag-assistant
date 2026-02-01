"""
RAG Service - Orchestrates retrieval-augmented generation operations.
"""
from typing import List

from ...domain.models import SearchResult
from ...domain.repositories import VectorStoreRepository


class RAGService:
    """Service for RAG retrieval and context generation."""
    
    def __init__(
        self, 
        vector_repository: VectorStoreRepository,
        min_score: float = 0.3,
        default_k: int = 4
    ):
        """Initialize the RAG service.
        
        Args:
            vector_repository: Repository for vector search operations.
            min_score: Minimum similarity score for results.
            default_k: Default number of results to retrieve.
        """
        self._repository = vector_repository
        self._min_score = min_score
        self._default_k = default_k
    
    def search(
        self, 
        query: str, 
        k: int = None,
        min_score: float = None
    ) -> List[SearchResult]:
        """Search for relevant documents.
        
        Args:
            query: Search query text.
            k: Number of results to return. Uses default if None.
            min_score: Minimum similarity score. Uses default if None.
            
        Returns:
            List of search results.
        """
        k = k or self._default_k
        min_score = min_score or self._min_score
        
        # Search in repository
        results = self._repository.search(query, k=k)
        
        # Filter by score
        filtered_results = [
            result for result in results 
            if result.score >= min_score
        ]
        
        return filtered_results
    
    def get_context(
        self, 
        query: str, 
        max_tokens: int = 2000,
        k: int = None
    ) -> str:
        """Get formatted context for RAG from relevant documents.
        
        Args:
            query: Query to search for relevant context.
            max_tokens: Maximum token length for context.
            k: Number of documents to retrieve.
            
        Returns:
            Formatted context string.
        """
        # Get relevant documents
        results = self.search(query, k=k)
        
        if not results:
            return "No relevant documents found in the knowledge base."
        
        # Format context
        context_parts = []
        current_tokens = 0
        
        for i, result in enumerate(results, 1):
            # Estimate tokens (rough: ~4 chars per token)
            chunk_tokens = len(result.content) // 4
            
            if current_tokens + chunk_tokens > max_tokens:
                break
            
            context_parts.append(
                f"[Document {i}] (Relevance: {result.score:.2f})\n"
                f"Source: {result.metadata.get('source', 'Unknown')}\n"
                f"{result.content}\n"
            )
            current_tokens += chunk_tokens
        
        if not context_parts:
            return "No relevant documents found within token limit."
        
        return "\n---\n".join(context_parts)
    
    def get_relevant_sources(self, query: str, k: int = None) -> List[str]:
        """Get list of relevant source documents for a query.
        
        Args:
            query: Search query.
            k: Number of results to check.
            
        Returns:
            List of unique source paths/names.
        """
        results = self.search(query, k=k)
        
        sources = set()
        for result in results:
            source = result.metadata.get('source') or result.metadata.get('filename')
            if source:
                sources.add(source)
        
        return list(sources)
