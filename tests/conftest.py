"""
Configuración compartida para todos los tests (fixtures de pytest)
"""
import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from src.domain.models.document import Document, DocumentChunk
from src.domain.models.search_result import SearchResult
from src.domain.models.chat_message import ChatMessage, MessageRole


# =============================================
# FIXTURES DE DATOS DE EJEMPLO
# =============================================

@pytest.fixture
def sample_document():
    """Documento de ejemplo para tests"""
    return Document(
        id="doc-123",
        title="test.txt",
        content="Este es un documento de prueba con contenido de ejemplo.",
        source_type="text",
        source_path="test.txt",
        chunks=[],
        metadata={"author": "Test User"}
    )


@pytest.fixture
def sample_chunks():
    """Chunks de documento de ejemplo"""
    return [
        DocumentChunk(
            id="chunk-1",
            content="Primera parte del documento",
            document_id="doc-123",
            chunk_index=0,
            metadata={"page": 1}
        ),
        DocumentChunk(
            id="chunk-2",
            content="Segunda parte del documento",
            document_id="doc-123",
            chunk_index=1,
            metadata={"page": 2}
        ),
        DocumentChunk(
            id="chunk-3",
            content="Tercera parte del documento",
            document_id="doc-123",
            chunk_index=2,
            metadata={"page": 3}
        )
    ]


@pytest.fixture
def sample_search_results(sample_chunks):
    """Resultados de búsqueda de ejemplo"""
    return [
        SearchResult(
            chunk=sample_chunks[0],
            similarity_score=0.95,
            rank=1
        ),
        SearchResult(
            chunk=sample_chunks[1],
            similarity_score=0.85,
            rank=2
        )
    ]


@pytest.fixture
def sample_chat_messages():
    """Historial de chat de ejemplo"""
    return [
        ChatMessage(role=MessageRole.USER, content="Hola, ¿cómo estás?"),
        ChatMessage(role=MessageRole.ASSISTANT, content="¡Hola! Estoy bien, gracias por preguntar.")
    ]


# =============================================
# MOCKS DE REPOSITORIOS
# =============================================

@pytest.fixture
def mock_vector_repository():
    """Mock del repositorio de vector store"""
    mock = Mock()
    mock.add_documents = Mock(return_value=None)
    mock.search = Mock(return_value=[])
    mock.clear = Mock(return_value=None)
    mock.get_collection_stats = Mock(return_value={"count": 0})
    return mock


@pytest.fixture
def mock_llm_repository():
    """Mock del repositorio de LLM"""
    mock = Mock()
    # invoke() devuelve un string, no un ChatMessage
    mock.invoke = Mock(return_value="Respuesta del LLM mockeado")
    mock.stream = Mock(return_value=iter(["Respuesta ", "en ", "streaming"]))
    return mock


@pytest.fixture
def mock_document_processor():
    """Mock del procesador de documentos"""
    mock = Mock()
    mock.process_file = Mock()
    mock.process_text = Mock()
    return mock
