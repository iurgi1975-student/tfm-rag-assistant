"""
Document processing and ingestion for RAG system.
"""
from typing import List
from pathlib import Path
from datetime import datetime
import uuid

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..domain.models import Document, DocumentChunk


class DocumentProcessor:
    """Process and prepare documents for RAG ingestion."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
    
    def load_document(self, file_path: str) -> List[Document]:
        """Load a document based on its file extension.
        
        Args:
            file_path: Path to the document file.
            
        Returns:
            List with a single Document object containing chunks.
        """
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.pdf':
            return self._load_pdf(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    def _load_pdf(self, file_path: str) -> List[Document]:
        """Load PDF and convert to our Document model.
        
        Args:
            file_path: Path to PDF file.
            
        Returns:
            List with a single Document object.
        """
        # Load PDF using LangChain
        loader = PyPDFLoader(file_path)
        langchain_docs = loader.load()
        
        # Combine all pages into one text
        full_text = "\n".join([doc.page_content for doc in langchain_docs])
        
        # Split into chunks
        langchain_chunks = self.text_splitter.split_documents(langchain_docs)
        
        # Create our Document model
        doc_id = f"doc_{uuid.uuid4().hex[:12]}"
        document = Document(
            id=doc_id,
            title=Path(file_path).stem,
            content=full_text,
            source_type="pdf",
            source_path=str(file_path),
            metadata={"filename": Path(file_path).name}
        )
        
        # Convert LangChain chunks to our DocumentChunk model
        for chunk_index, chunk in enumerate(langchain_chunks):
            doc_chunk = DocumentChunk(
                id=f"{doc_id}_chunk_{chunk_index}",
                content=chunk.page_content,
                document_id=doc_id,
                chunk_index=chunk_index,
                metadata=chunk.metadata
            )
            document.chunks.append(doc_chunk)
        
        return [document]
    
    def process_text_input(self, text: str, source: str = "text_input") -> List[Document]:
        """Process raw text input.
        
        Args:
            text: Raw text to process.
            source: Source identifier.
            
        Returns:
            List with a single Document object.
        """
        # Create a fake LangChain document to split / es temporal para que pueda procesarlo
        from langchain_core.documents import Document as LangChainDocument
        
        langchain_doc = LangChainDocument(
            page_content=text,
            metadata={"source": source, "type": "text"}
        )
        
        # Split into chunks
        langchain_chunks = self.text_splitter.split_documents([langchain_doc])
        
        # Create our Document model
        doc_id = f"doc_{uuid.uuid4().hex[:12]}"
        document = Document(
            id=doc_id,
            title=source,
            content=text,
            source_type="text",
            source_path=None,
            metadata={"source": source}
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
        
        return [document]
