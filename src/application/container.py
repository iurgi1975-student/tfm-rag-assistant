"""
Dependency Injection Container - DDD Infrastructure
"""
import os
from pathlib import Path
from typing import Optional

from ..infrastructure.vector_stores.chroma_store import ChromaVectorStore
from ..infrastructure.document_processor import DocumentProcessor
from ..infrastructure.llm import OllamaLLM, GoogleGeminiLLM
from ..infrastructure.persistence import SQLiteChatRepository
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
        google_api_key: Optional[str] = None,
        use_google: bool = False,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        rag_top_k: int = 4,
        rag_min_score: float = 0.0,
        memory_window: int = 10,
        enable_chat_persistence: bool = True,
        chat_db_path: str = "./data/chat_history.db",
        default_session_id: str = "main"
    ):
        """Initialize container with configuration.
        
        Args:
            model_name: Model name (Ollama or Google Gemini).
            temperature: LLM temperature.
            chroma_dir: ChromaDB persistence directory.
            ollama_url: Ollama API base URL.
            google_api_key: Google AI Studio API key.
            use_google: Use Google Gemini instead of Ollama.
            chunk_size: Document chunk size.
            chunk_overlap: Overlap between chunks.
            rag_top_k: Number of documents to retrieve.
            rag_min_score: Minimum similarity score.
            memory_window: Chat history window size.
            enable_chat_persistence: Enable SQLite chat history persistence.
            chat_db_path: Path to SQLite database for chat history.
            default_session_id: Default session identifier for chats.
        """
        self.model_name = model_name
        self.temperature = temperature
        self.chroma_dir = chroma_dir
        self.ollama_url = ollama_url
        self.google_api_key = google_api_key
        self.use_google = use_google
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.rag_top_k = rag_top_k
        self.rag_min_score = rag_min_score
        self.memory_window = memory_window
        self.enable_chat_persistence = enable_chat_persistence
        self.chat_db_path = chat_db_path
        self.default_session_id = default_session_id
        
        # Singleton instances
        self._vector_store: Optional[ChromaVectorStore] = None
        self._llm: Optional[OllamaLLM] = None
        self._document_processor: Optional[DocumentProcessor] = None
        self._chat_repository: Optional[SQLiteChatRepository] = None
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
    def llm(self):
        """Get or create LLM instance."""
        if self._llm is None:
            print("🤖 Initializing LLM...")
            if self.use_google:
                if not self.google_api_key:
                    raise ValueError("Google API key is required when use_google=True")
                print("   Using Google Gemini...")
                self._llm = GoogleGeminiLLM(
                    api_key=self.google_api_key,
                    model=self.model_name,
                    temperature=self.temperature,
                    max_tokens=4000
                )
            else:
                print("   Using Ollama...")
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
    def chat_repository(self) -> Optional[SQLiteChatRepository]:
        """Get or create chat history repository."""
        if self.enable_chat_persistence and self._chat_repository is None:
            print("💾 Initializing Chat Persistence (SQLite)...")
            self._chat_repository = SQLiteChatRepository(db_path=self.chat_db_path)
            print("✅ Chat Persistence initialized!")
        return self._chat_repository
    
    @property
    def chat_service(self) -> ChatService:
        """Get or create chat service."""
        if self._chat_service is None:
            print("💬 Initializing Chat Service...")
            self._chat_service = ChatService(
                llm=self.llm,
                rag_service=self.rag_service,
                chat_repository=self.chat_repository,
                session_id=self.default_session_id,
                memory_window=self.memory_window
            )
            print("✅ Chat Service initialized!")
        return self._chat_service
    
    def reset(self):
        """Reset all singleton instances (useful for testing)."""
        self._vector_store = None
        self._llm = None
        self._document_processor = None
        self._chat_repository = None
        self._document_service = None
        self._rag_service = None
        self._chat_service = None
