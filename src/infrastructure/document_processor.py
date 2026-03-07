"""
Document processing and ingestion for RAG system.
"""
from typing import List, Optional
from pathlib import Path
import uuid

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document as LangChainDocument

from ..domain.models import Document, DocumentChunk
from .mappers import DocumentMapper
from .cad_image_processor import CADImageProcessor


class DocumentProcessor:
    """Process and prepare documents for RAG ingestion."""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        cad_processor: Optional[CADImageProcessor] = None
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.cad_processor = cad_processor or CADImageProcessor()
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
        elif file_extension == '.dxf':
            return self._load_dxf(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    def _load_pdf(self, file_path: str) -> List[Document]:
        """Load PDF, extract text chunks and embedded images.
        
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

        # Extract images from PDF
        images = self.cad_processor.extract_from_pdf(file_path)
        document.images = images

        # Create an image-type chunk for each extracted image
        for img in images:
            chunk = DocumentChunk(
                id=str(uuid.uuid4()),
                content=img.extracted_text or f"[Image from {Path(file_path).name}, page {img.metadata.get('page', '?')}]",
                document_id=document.id,
                chunk_index=len(document.chunks),
                content_type="image",
                image_content=img,
                metadata={**img.metadata, "document_id": document.id},
            )
            document.chunks.append(chunk)
        
        return [document]

    def _load_dxf(self, file_path: str) -> List[Document]:
        """Convert a DXF file to an image and wrap it in a Document.

        Args:
            file_path: Path to DXF file.

        Returns:
            List with a single Document object (image chunk only).
        """
        image_content = self.cad_processor.convert_dxf_to_image(file_path)

        doc_id = str(uuid.uuid4())
        title = Path(file_path).stem
        chunks = []

        if image_content:
            chunk = DocumentChunk(
                id=str(uuid.uuid4()),
                content=image_content.extracted_text or f"[DXF drawing: {title}]",
                document_id=doc_id,
                chunk_index=0,
                content_type="image",
                image_content=image_content,
                metadata={"source": file_path, "document_id": doc_id},
            )
            chunks.append(chunk)

        document = Document(
            id=doc_id,
            title=title,
            content=image_content.extracted_text if image_content else "",
            source_type="dxf",
            source_path=str(file_path),
            chunks=chunks,
            images=[image_content] if image_content else [],
            metadata={"filename": Path(file_path).name},
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
