"""Document and DocumentChunk models.

Represents documents and their chunks in the RAG system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid


@dataclass
class ImageContent:
    """An image extracted from a document.

    Attributes:
        id: Unique identifier
        image_path: Path to the stored image file
        image_format: Format of the image (png, jpg, etc.)
        thumbnail_path: Path to a smaller thumbnail version
        width: Image width in pixels
        height: Image height in pixels
        extracted_text: Text extracted from the image (OCR / title block)
        metadata: Additional info (page number, source, etc.)
    """
    id: str
    image_path: str
    image_format: str = "png"
    thumbnail_path: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    extracted_text: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"ImageContent(id={self.id}, format={self.image_format}, {self.width}x{self.height})"


@dataclass
class DocumentChunk:
    """A chunk of a document (piece of text or image for searching).

    Attributes:
        id: Unique identifier
        content: The text content (empty for pure-image chunks)
        document_id: ID of the parent document
        chunk_index: Position in the document
        content_type: Type of content: 'text', 'image' or 'multimodal'
        image_content: ImageContent object when content_type is 'image'
        metadata: Additional info (page number, section, etc.)
    """
    id: str
    content: str
    document_id: str
    chunk_index: int
    content_type: str = "text"          # 'text' | 'image' | 'multimodal'
    image_content: Optional[ImageContent] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __repr__(self) -> str:
        return f"DocumentChunk(id={self.id}, type={self.content_type}, size={len(self.content)})"


@dataclass
class Document:
    """A document in the RAG system.

    Attributes:
        id: Unique identifier
        title: Human-readable title
        content: Full text content
        source_type: Type (pdf, dxf, text, etc.)
        source_path: Original file path
        chunks: List of DocumentChunk objects
        images: List of ImageContent objects extracted from the document
        metadata: Additional info
        created_at: When ingested
    """
    id: str
    title: str
    content: str
    source_type: str = "text"
    source_path: Optional[str] = None
    chunks: List[DocumentChunk] = field(default_factory=list)
    images: List[ImageContent] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def has_images(self) -> bool:
        """Return True if this document contains extracted images."""
        return len(self.images) > 0

    @property
    def image_count(self) -> int:
        """Return the number of images in this document."""
        return len(self.images)

    def __repr__(self) -> str:
        return f"Document(id={self.id}, title={self.title}, chunks={len(self.chunks)}, images={self.image_count})"
