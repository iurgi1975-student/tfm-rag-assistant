"""
Mappers for converting between external libraries and domain models.
"""
from typing import List
import uuid
from pathlib import Path

from langchain_core.documents import Document as LangChainDocument

from ..domain.models import Document, DocumentChunk


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
