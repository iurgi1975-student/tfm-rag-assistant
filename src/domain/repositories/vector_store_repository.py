"""VectorStoreRepository - Abstract interface for vector storage.

Defines the contract that all vector store implementations must follow.
This is the key to Clean Architecture: domain doesn't depend on specific implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple
from ..models import Document, DocumentChunk, SearchResult


class VectorStoreRepository(ABC):
    """Abstract interface for vector store repositories.
    
    Any vector store (Chroma, Pinecone, Weaviate, etc.) must implement these methods.
    This ensures loose coupling and allows easy swapping of implementations.
    
    Example:
        # Instead of depending on ChromaVectorStore directly:
        # store = ChromaVectorStore()
        
        # We depend on the abstraction:
        # store: VectorStoreRepository = create_vector_store()
    """
    
    @abstractmethod
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the vector store.
        
        Args:
            documents: List of Document objects to add.
                      Each document will be split into chunks.
        """
        pass
    
    @abstractmethod
    def similarity_search(self, query: str, k: int = 4) -> List[SearchResult]:
        """Search for similar documents.
        
        Args:
            query: The search query text.
            k: Number of top results to return.
            
        Returns:
            List of SearchResult objects ranked by similarity.
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all documents from the store."""
        pass
    
    @abstractmethod
    def get_document_count(self) -> int:
        """Get total number of documents in the store.

        Returns:
            Integer count of documents.
        """
        pass

    @abstractmethod
    def add_images(self, images: List, document_id: str) -> None:
        """Add images to the vector store.

        Args:
            images: List of ImageContent objects to embed and store.
            document_id: ID of the parent document.
        """
        pass

    @abstractmethod
    def search_images(self, query: str, k: int = 4) -> List[SearchResult]:
        """Search for similar images using a text query.

        Args:
            query: The search query text.
            k: Number of top results to return.

        Returns:
            List of SearchResult objects ranked by similarity.
        """
        pass

    @abstractmethod
    def search_hybrid(self, query: str, k_text: int = 4, k_images: int = 2) -> List[SearchResult]:
        """Search over text and image collections combined.

        Merges text and image results, re-ranks by score, and returns the top
        (k_text + k_images) results.

        Args:
            query: The search query text.
            k_text: Number of text results to retrieve.
            k_images: Number of image results to retrieve.

        Returns:
            Merged and ranked list of SearchResult objects.
        """
        pass

    def __len__(self) -> int:
        """Return the number of documents via len() operator."""
        return self.get_document_count()
