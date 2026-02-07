"""
Mappers for converting between external libraries and domain models.
"""
from typing import List, Tuple, Optional
import uuid
from pathlib import Path
from datetime import datetime

from langchain_core.documents import Document as LangChainDocument

from ..domain.models import Document, DocumentChunk, ChatMessage, MessageRole


class DocumentMapper:
    """Maps between LangChain documents and domain models."""
    
    @staticmethod
    def langchain_to_domain(
        langchain_docs: List[LangChainDocument],
        langchain_chunks: List[LangChainDocument],
        title: str,
        source_type: str,
        source_path: str = None,
        additional_metadata: dict = None
    ) -> Document:
        """Convert LangChain documents to domain Document.
        
        Args:
            langchain_docs: Original LangChain documents (for full text).
            langchain_chunks: Split LangChain document chunks.
            title: Document title.
            source_type: Type of source (pdf, text, etc).
            source_path: Path to source file if applicable.
            additional_metadata: Additional metadata to include.
            
        Returns:
            Domain Document object with chunks.
        """
        # Combine all pages into full text
        full_text = "\n".join([doc.page_content for doc in langchain_docs])
        
        # Generate document ID
        doc_id = f"doc_{uuid.uuid4().hex[:12]}"
        
        # Prepare metadata
        metadata = additional_metadata or {}
        
        # Create domain document
        document = Document(
            id=doc_id,
            title=title,
            content=full_text,
            source_type=source_type,
            source_path=source_path,
            metadata=metadata
        )
        
        # Convert chunks
        for chunk_index, chunk in enumerate(langchain_chunks):
            doc_chunk = DocumentChunk(
                id=f"{doc_id}_chunk_{chunk_index}",
                content=chunk.page_content,
                document_id=doc_id,
                chunk_index=chunk_index,
                metadata=chunk.metadata
            )
            document.chunks.append(doc_chunk)
        
        return document


class ChatMessageMapper:
    """Maps between SQLite rows and ChatMessage domain models."""
    
    @staticmethod
    def to_domain(row: Tuple) -> Optional[ChatMessage]:
        """Convert SQLite row to ChatMessage domain object.
        
        Args:
            row: Tuple from SQLite query (role, content, timestamp).
            
        Returns:
            ChatMessage object or None if conversion fails.
        """
        try:
            return ChatMessage(
                role=MessageRole(row[0]),
                content=row[1],
                timestamp=datetime.fromisoformat(row[2]) if row[2] else None
            )
        except (ValueError, TypeError, IndexError) as e:
            print(f"Warning: Failed to convert row to ChatMessage: {e}")
            return None
    
    @staticmethod
    def to_persistence(message: ChatMessage) -> Tuple[str, str, str]:
        """Convert ChatMessage to SQLite tuple.
        
        Args:
            message: ChatMessage domain object.
            
        Returns:
            Tuple of (role, content, timestamp) for SQLite insert.
        """
        return (
            message.role.value,
            message.content,
            message.timestamp.isoformat() if message.timestamp else datetime.utcnow().isoformat()
        )
