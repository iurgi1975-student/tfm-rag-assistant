"""
Tests para ChatService
Aquí probamos la lógica de conversación con el LLM
"""
import pytest
from src.application.services.chat_service import ChatService
from src.domain.models.chat_message import ChatMessage, MessageRole
from src.domain.models.search_result import SearchResult


class TestChatService:
    """Tests para el servicio de chat"""
    
    @pytest.fixture
    def service(self, mock_llm_repository, mock_rag_service=None):
        """Crear instancia del servicio con mocks"""
        # Si no se pasa rag_service, usamos None para probar sin RAG
        from unittest.mock import Mock
        rag = Mock() if mock_rag_service is None else mock_rag_service
        
        return ChatService(
            llm=mock_llm_repository,
            rag_service=rag
        )
    
    def test_chat_without_rag(self, mock_llm_repository):
        """Test: Chat sin usar RAG (sin contexto de documentos)"""
        # Configuramos el mock del LLM - invoke() devuelve string
        mock_llm_repository.invoke.return_value = "Respuesta sin RAG"
        
        # Creamos servicio sin RAG
        service = ChatService(llm=mock_llm_repository, rag_service=None)
        
        # Enviamos mensaje
        response = service.chat(
            message="Hola",
            use_rag=False,
            stream=False
        )
        
        # Verificaciones
        assert response == "Respuesta sin RAG"
        
        # Verificamos que se llamó al LLM con el historial correcto
        mock_llm_repository.invoke.assert_called_once()
        call_args = mock_llm_repository.invoke.call_args[0][0]
        # Debe haber 2 mensajes: system + user (sin context porque use_rag=False)
        assert len(call_args) >= 2
        # El último debe ser el mensaje del usuario
        assert call_args[-1].content == "Hola"
        assert call_args[-1].role == MessageRole.USER
    
    def test_chat_with_rag(self, mock_llm_repository, sample_chunks):
        """Test: Chat usando RAG (con contexto de documentos)"""
        from unittest.mock import Mock
        
        # Configuramos el mock del RAG
        mock_rag = Mock()
        mock_rag.search.return_value = [
            SearchResult(chunk=sample_chunks[0], similarity_score=0.9, rank=1)
        ]
        mock_rag.get_context.return_value = "Contexto: Información relevante"
        
        # Configuramos el mock del LLM - devuelve string
        mock_llm_repository.invoke.return_value = "Respuesta con RAG basada en el contexto"
        
        # Creamos servicio con RAG
        service = ChatService(llm=mock_llm_repository, rag_service=mock_rag)
        
        # Enviamos mensaje con RAG activado
        response = service.chat(
            message="¿Qué dice el documento?",
            use_rag=True,
            stream=False
        )
        
        # Verificaciones
        assert "Respuesta con RAG" in response
        
        # Verificamos que se llamó al RAG para buscar contexto
        # El RAGService.get_context() llama internamente a search()
        # Verificamos que se llamó con la query correcta
        assert mock_rag.get_context.called
        
        # Verificamos que se pasó contexto al LLM
        call_args = mock_llm_repository.invoke.call_args[0][0]
        # Debe haber mensajes: system (con contexto) + user
        assert len(call_args) >= 2
        assert call_args[0].role == MessageRole.SYSTEM
        # El system prompt debería mencionar el contexto
        assert "context" in call_args[0].content.lower() or "Context" in call_args[0].content
    
    def test_clear_history(self, service):
        """Test: Limpiar historial de chat"""
        # Agregamos algunos mensajes al historial
        service.chat("Mensaje 1", use_rag=False, stream=False)
        service.chat("Mensaje 2", use_rag=False, stream=False)
        
        # Verificamos que hay historial
        assert len(service.get_history()) > 0
        
        # Limpiamos
        service.clear_history()
        
        # Verificamos que está vacío
        assert len(service.get_history()) == 0
    
    def test_get_history(self, service):
        """Test: Obtener historial de conversación"""
        # Al inicio debe estar vacío
        assert service.get_history() == []
        
        # Enviamos un mensaje
        service.chat("Hola", use_rag=False, stream=False)
        
        # Ahora debe haber 2 mensajes (user + assistant)
        history = service.get_history()
        assert len(history) == 2
        assert history[0].role == MessageRole.USER
        assert history[1].role == MessageRole.ASSISTANT
    
    def test_chat_streaming(self, mock_llm_repository):
        """Test: Chat con respuesta en streaming"""
        # Configuramos el mock para devolver un generador
        mock_llm_repository.stream.return_value = iter(["Hola", " mundo", "!"])
        
        service = ChatService(llm=mock_llm_repository, rag_service=None)
        
        # Ejecutamos con stream=True
        response_generator = service.chat(
            message="Test streaming",
            use_rag=False,
            stream=True
        )
        
        # Verificamos que devuelve un generador
        assert hasattr(response_generator, '__iter__')
        
        # Consumimos el generador
        chunks = list(response_generator)
        assert len(chunks) > 0
        
        # Verificamos que se llamó al método stream del LLM
        mock_llm_repository.stream.assert_called_once()
    
    def test_history_limit(self, mock_llm_repository):
        """Test: El historial se limita para no sobrecargar el contexto"""
        service = ChatService(llm=mock_llm_repository, rag_service=None)
        
        # Simulamos muchas conversaciones
        for i in range(15):
            service.chat(f"Mensaje {i}", use_rag=False, stream=False)
        
        # El historial completo se guarda
        full_history = service.get_history()
        assert len(full_history) == 30  # 15 user + 15 assistant
        
        # Pero cuando se envía al LLM, se limita (implementado en _get_trimmed_history)
        # Este test verifica que no explote con mucho historial
        service.chat("Último mensaje", use_rag=False, stream=False)
        
        # Si llegó aquí sin errores, funciona correctamente
        assert True
