"""Document and DocumentChunk models.

Represents documents and their chunks in the RAG system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid


@dataclass
class DocumentChunk:
    """A chunk of a document (piece of text for searching).
    
    Attributes:
        id: Unique identifier
        content: The text content
        document_id: ID of the parent document
        chunk_index: Position in the document
        metadata: Additional info (page number, section, etc.)
    """
    id: str
    content: str
    document_id: str
    chunk_index: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"DocumentChunk(id={self.id}, size={len(self.content)})"


@dataclass
class Document:
    """A document in the RAG system.
    
    Attributes:
        id: Unique identifier
        title: Human-readable title
        content: Full text content
        source_type: Type (pdf, text, etc.)
        source_path: Original file path
        chunks: List of DocumentChunk objects
        metadata: Additional info
        created_at: When ingested
    """
    id: str
    title: str
    content: str
    source_type: str = "text"
    source_path: Optional[str] = None
    chunks: List[DocumentChunk] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"Document(id={self.id}, title={self.title}, chunks={len(self.chunks)})"
