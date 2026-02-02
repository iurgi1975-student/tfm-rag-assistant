"""
Dependency Injection Container - DDD Infrastructure
"""
import os
from pathlib import Path
from typing import Optional

from ..infrastructure.vector_stores.chroma_store import ChromaVectorStore
from ..infrastructure.document_processor import DocumentProcessor
from ..infrastructure.llm import OllamaLLM
from .services.document_service import DocumentService
from .services.rag_service import RAGService
from .services.chat_service import ChatService


class AppContainer:
    """Container for dependency injection."""
    
    def __init__(
        self,
        model_name: str = "llama3.2:3b",
        temperature: float = 0.7,
        chroma_dir: str = "./chroma_db",
        ollama_url: str = "http://localhost:11434",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        rag_top_k: int = 4,
        rag_min_score: float = 0.0,
        memory_window: int = 10
    ):
        """Initialize container with configuration.
        
        Args:
            model_name: Ollama model name.
            temperature: LLM temperature.
            chroma_dir: ChromaDB persistence directory.
            ollama_url: Ollama API base URL.
            chunk_size: Document chunk size.
            chunk_overlap: Overlap between chunks.
            rag_top_k: Number of documents to retrieve.
            rag_min_score: Minimum similarity score.
            memory_window: Chat history window size.
        """
        self.model_name = model_name
        self.temperature = temperature
        self.chroma_dir = chroma_dir
        self.ollama_url = ollama_url
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.rag_top_k = rag_top_k
        self.rag_min_score = rag_min_score
        self.memory_window = memory_window
        
        # Singleton instances
        self._vector_store: Optional[ChromaVectorStore] = None
        self._llm: Optional[OllamaLLM] = None
        self._document_processor: Optional[DocumentProcessor] = None
        self._document_service: Optional[DocumentService] = None
        self._rag_service: Optional[RAGService] = None
        self._chat_service: Optional[ChatService] = None
    
    @property
    def vector_store(self) -> ChromaVectorStore:
        """Get or create vector store instance."""
        if self._vector_store is None:
            print("💾 Initializing Vector Store...")
            self._vector_store = ChromaVectorStore(persist_dir=self.chroma_dir)
            print("✅ Vector Store initialized!")
        return self._vector_store
    
    @property
    def llm(self) -> OllamaLLM:
        """Get or create LLM instance."""
        if self._llm is None:
            print("🤖 Initializing LLM...")
            self._llm = OllamaLLM(
                model=self.model_name,
                base_url=self.ollama_url,
                temperature=self.temperature,
                max_tokens=4000
            )
            print(f"✅ LLM initialized! (Model: {self._llm.get_model_name()})")
        return self._llm
    
    @property
    def document_processor(self) -> DocumentProcessor:
        """Get or create document processor."""
        if self._document_processor is None:
            self._document_processor = DocumentProcessor(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
        return self._document_processor
    
    @property
    def document_service(self) -> DocumentService:
        """Get or create document service."""
        if self._document_service is None:
            print("📄 Initializing Document Service...")
            self._document_service = DocumentService(
                vector_repository=self.vector_store,
                document_processor=self.document_processor
            )
            print("✅ Document Service initialized!")
        return self._document_service
    
    @property
    def rag_service(self) -> RAGService:
        """Get or create RAG service."""
        if self._rag_service is None:
            print("🔍 Initializing RAG Service...")
            self._rag_service = RAGService(
                vector_repository=self.vector_store,
                min_score=self.rag_min_score,
                default_k=self.rag_top_k
            )
            print("✅ RAG Service initialized!")
        return self._rag_service
    
    @property
    def chat_service(self) -> ChatService:
        """Get or create chat service."""
        if self._chat_service is None:
            print("💬 Initializing Chat Service...")
            self._chat_service = ChatService(
                llm=self.llm,
                rag_service=self.rag_service,
                memory_window=self.memory_window
            )
            print("✅ Chat Service initialized!")
        return self._chat_service
    
    def reset(self):
        """Reset all singleton instances (useful for testing)."""
        self._vector_store = None
        self._llm = None
        self._document_processor = None
        self._document_service = None
        self._rag_service = None
        self._chat_service = None
