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
        min_score: float = 0.0,
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
        min_score = min_score if min_score is not None else self._min_score
        
        # Search in repository
        results = self._repository.similarity_search(query, k=k)
        
        # Filter by score only if min_score > 0
        if min_score > 0:
            results = [
                result for result in results 
                if result.similarity_score >= min_score
            ]
        
        return results
    
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
            chunk_tokens = len(result.chunk.content) // 4
            
            if current_tokens + chunk_tokens > max_tokens:
                break
            
            context_parts.append(
                f"[Document {i}] (Relevance: {result.similarity_score:.2f})\n"
                f"Source: {result.chunk.metadata.get('source', 'Unknown')}\n"
                f"{result.chunk.content}\n"
            )
            current_tokens += chunk_tokens
        
        if not context_parts:
            return "No relevant documents found within token limit."
        
        return "\n---\n".join(context_parts)
    
    def search_with_images(
        self,
        query: str,
        include_images: bool = True,
        k_text: int = None,
        k_images: int = 4,
        min_score: float = None,
    ) -> dict:
        """Search combining text and image results.

        Args:
            query: Search query text.
            include_images: Whether to include image results.
            k_text: Number of text results.
            k_images: Number of image results.
            min_score: Minimum similarity score.

        Returns:
            Dict with keys: 'text_results', 'image_results', 'combined'.
        """
        k_text = k_text or self._default_k
        min_score = min_score if min_score is not None else self._min_score

        if include_images:
            combined = self._repository.search_hybrid(query, k_text=k_text, k_images=k_images)
        else:
            combined = self._repository.similarity_search(query, k=k_text)

        if min_score > 0:
            combined = [r for r in combined if r.similarity_score >= min_score]

        text_results = [r for r in combined if r.chunk.content_type != "image"]
        image_results = [r for r in combined if r.chunk.content_type == "image"]

        return {
            "text_results": text_results,
            "image_results": image_results,
            "combined": combined,
        }

    def format_multimodal_context(self, results: dict, max_tokens: int = 2000) -> tuple:
        """Format combined text + image results into LLM context.

        Args:
            results: Dict returned by search_with_images().
            max_tokens: Max token budget for text context.

        Returns:
            Tuple (formatted_text: str, image_paths: List[str]).
        """
        context_parts = []
        current_tokens = 0

        for i, result in enumerate(results["text_results"], 1):
            chunk_tokens = len(result.chunk.content) // 4
            if current_tokens + chunk_tokens > max_tokens:
                break
            context_parts.append(
                f"[Document {i}] (Relevance: {result.similarity_score:.2f})\n"
                f"Source: {result.chunk.metadata.get('source', 'Unknown')}\n"
                f"{result.chunk.content}\n"
            )
            current_tokens += chunk_tokens

        for result in results["image_results"]:
            img = result.chunk.image_content
            if img and img.extracted_text:
                context_parts.append(
                    f"[Image] (Relevance: {result.similarity_score:.2f})\n"
                    f"Extracted text: {img.extracted_text}\n"
                )

        formatted_text = "\n---\n".join(context_parts) if context_parts else "No relevant documents found."

        image_paths = [
            r.chunk.image_content.image_path
            for r in results["image_results"]
            if r.chunk.image_content and r.chunk.image_content.image_path
        ]

        return formatted_text, image_paths

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
            source = result.chunk.metadata.get('source') or result.chunk.metadata.get('filename')
            if source:
                sources.add(source)
        
        return list(sources)
