"""SearchResult model.

Represents a search result from the vector store.
"""

from dataclasses import dataclass
from .document import DocumentChunk


@dataclass
class SearchResult:
    """A result from a vector similarity search.
    
    Attributes:
        chunk: The DocumentChunk that matched
        similarity_score: How relevant (0.0 to 1.0)
        rank: Position in results (1 = best)
    """
    chunk: DocumentChunk
    similarity_score: float
    rank: int
    
    def __repr__(self) -> str:
        return f"SearchResult(rank={self.rank}, score={self.similarity_score:.3f})"
