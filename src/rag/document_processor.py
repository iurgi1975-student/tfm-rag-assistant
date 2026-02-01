"""
Document processing and ingestion for RAG system.
"""
from typing import List
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document as LangChainDocument

from ..domain.models import Document
from ..infrastructure.mappers import DocumentMapper


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
        self.mapper = DocumentMapper()
    
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
        loader = PyPDFLoader(file_path)
        langchain_docs = loader.load()
        langchain_chunks = self.text_splitter.split_documents(langchain_docs)
        
        document = self.mapper.langchain_to_domain(
            langchain_docs=langchain_docs,
            langchain_chunks=langchain_chunks,
            title=Path(file_path).stem,
            source_type="pdf",
            source_path=str(file_path),
            additional_metadata={"filename": Path(file_path).name}
        )
        
        return [document]
    
    def process_text_input(self, text: str, source: str = "text_input") -> List[Document]:
        """Process raw text input.
        
        Args:
            text: Raw text to process.
            source: Source identifier.
            
        Returns:
            List with a single Document object.
        """
        langchain_doc = LangChainDocument(
            page_content=text,
            metadata={"source": source, "type": "text"}
        )
        
        langchain_chunks = self.text_splitter.split_documents([langchain_doc])
        
        document = self.mapper.langchain_to_domain(
            langchain_docs=[langchain_doc],
            langchain_chunks=langchain_chunks,
            title=source,
            source_type="text",
            source_path=None,
            additional_metadata={"source": source}
        )
        
        return [document]
        