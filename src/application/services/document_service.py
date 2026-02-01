"""
Document Service - Orchestrates document management operations.
"""
from typing import List, Optional
from pathlib import Path

from ...domain.models import Document
from ...domain.repositories import VectorStoreRepository
from ...infrastructure.document_processor import DocumentProcessor


class DocumentService:
    """Service for managing document ingestion and lifecycle."""
    
    def __init__(
        self, 
        vector_repository: VectorStoreRepository,
        document_processor: DocumentProcessor
    ):
        """Initialize the document service.
        
        Args:
            vector_repository: Repository for vector storage operations.
            document_processor: Processor for loading and chunking documents.
        """
        self._repository = vector_repository
        self._processor = document_processor
    
    def ingest_document(self, file_path: str) -> int:
        """Load and add a document to the knowledge base.
        
        Args:
            file_path: Path to the document file.
            
        Returns:
            Number of documents added (typically 1).
            
        Raises:
            ValueError: If file type is unsupported.
            FileNotFoundError: If file doesn't exist.
        """
        # Validate file exists
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Load and process document
        documents = self._processor.load_document(file_path)
        
        # Add to repository
        self._repository.add_documents(documents)
        
        return len(documents)
    
    def ingest_text(self, text: str, source: str = "text_input") -> int:
        """Process and add raw text to the knowledge base.
        
        Args:
            text: Raw text to process.
            source: Source identifier for the text.
            
        Returns:
            Number of documents added (typically 1).
        """
        # Process text into document
        documents = self._processor.process_text_input(text, source)
        
        # Add to repository
        self._repository.add_documents(documents)
        
        return len(documents)
    
    def clear_knowledge_base(self) -> None:
        """Clear all documents from the knowledge base."""
        self._repository.clear()
    
    def get_document_count(self) -> int:
        """Get the total number of documents in the knowledge base.
        
        Returns:
            Number of documents stored.
        """
        return self._repository.get_document_count()
    
    def get_document_stats(self) -> dict:
        """Get statistics about the document collection.
        
        Returns:
            Dictionary with stats like count, total chunks, etc.
        """
        count = self._repository.get_document_count()
        
        return {
            "total_documents": count,
            "status": "ready" if count > 0 else "empty"
        }
    
    def list_document_ids(self) -> List[str]:
        """Get list of all document IDs in the knowledge base.
        
        Returns:
            List of document IDs.
        """
        # This would require extending the repository interface
        # For now, return empty list as placeholder
        return []
