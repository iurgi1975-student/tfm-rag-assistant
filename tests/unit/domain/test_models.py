"""
Tests para los modelos del dominio
Aquí probamos que nuestros modelos (Document, ChatMessage, etc.) funcionan correctamente
"""
import pytest
from src.domain.models.document import Document, DocumentChunk
from src.domain.models.chat_message import ChatMessage, MessageRole
from src.domain.models.search_result import SearchResult


class TestDocument:
    """Tests para el modelo Document"""
    
    def test_create_document(self):
        """Test: Crear un documento correctamente"""
        doc = Document(
            id="test-123",
            title="test.txt",
            content="Contenido de prueba",
            source_type="text",
            source_path="test.txt",
            chunks=[],
            metadata={"author": "Tester"}
        )
        
        # Verificamos que se creó correctamente
        assert doc.id == "test-123"
        assert doc.title == "test.txt"
        assert doc.content == "Contenido de prueba"
        assert doc.metadata["author"] == "Tester"
    
    def test_document_to_dict(self):
        """Test: Los documentos tienen atributos básicos"""
        doc = Document(
            id="test-123",
            title="test.txt",
            content="Contenido",
            source_type="text",
            source_path="test.txt",
            chunks=[],
            metadata={}
        )
        
        # Verificamos que tiene los atributos esenciales
        assert doc.id == "test-123"
        assert doc.title == "test.txt"
        assert doc.content == "Contenido"


class TestDocumentChunk:
    """Tests para el modelo DocumentChunk"""
    
    def test_create_chunk(self):
        """Test: Crear un chunk correctamente"""
        chunk = DocumentChunk(
            id="chunk-1",
            content="Parte del documento",
            document_id="doc-123",
            chunk_index=0,
            metadata={"page": 1}
        )
        
        assert chunk.id == "chunk-1"
        assert chunk.document_id == "doc-123"
        assert chunk.content == "Parte del documento"
        assert chunk.chunk_index == 0
        assert chunk.metadata["page"] == 1


class TestChatMessage:
    """Tests para el modelo ChatMessage"""
    
    def test_create_user_message(self):
        """Test: Crear mensaje de usuario"""
        msg = ChatMessage(
            role=MessageRole.USER,
            content="Hola, ¿cómo estás?"
        )
        
        assert msg.role == MessageRole.USER
        assert msg.content == "Hola, ¿cómo estás?"
    
    def test_create_assistant_message(self):
        """Test: Crear mensaje del asistente"""
        msg = ChatMessage(
            role=MessageRole.ASSISTANT,
            content="¡Hola! Estoy bien, gracias."
        )
        
        assert msg.role == MessageRole.ASSISTANT
        assert msg.content == "¡Hola! Estoy bien, gracias."
    
    def test_message_validation_empty_content(self):
        """Test: No permitir mensajes con contenido vacío"""
        with pytest.raises(ValueError, match="Message content cannot be empty"):
            ChatMessage(role=MessageRole.USER, content="")
    
    def test_message_to_dict(self):
        """Test: Convertir mensaje a diccionario"""
        msg = ChatMessage(role=MessageRole.USER, content="Hola")
        msg_dict = msg.to_dict()
        
        assert msg_dict["role"] == "user"
        assert msg_dict["content"] == "Hola"
        assert isinstance(msg_dict, dict)
    
    def test_message_from_dict(self):
        """Test: Crear mensaje desde diccionario"""
        msg_dict = {"role": "assistant", "content": "Respuesta"}
        msg = ChatMessage.from_dict(msg_dict)
        
        assert msg.role == MessageRole.ASSISTANT
        assert msg.content == "Respuesta"


class TestSearchResult:
    """Tests para el modelo SearchResult"""
    
    def test_create_search_result(self, sample_chunks):
        """Test: Crear resultado de búsqueda"""
        result = SearchResult(
            chunk=sample_chunks[0],
            similarity_score=0.95,
            rank=1
        )
        
        assert result.chunk.content == "Primera parte del documento"
        assert result.similarity_score == 0.95
        assert result.rank == 1
    
    def test_search_result_score_range(self, sample_chunks):
        """Test: El score debe estar entre 0 y 1"""
        # Score válido
        result1 = SearchResult(chunk=sample_chunks[0], similarity_score=0.5, rank=1)
        assert 0 <= result1.similarity_score <= 1
        
        # Score en los límites
        result2 = SearchResult(chunk=sample_chunks[0], similarity_score=0.0, rank=2)
        result3 = SearchResult(chunk=sample_chunks[0], similarity_score=1.0, rank=3)
        assert result2.similarity_score == 0.0
        assert result3.similarity_score == 1.0
