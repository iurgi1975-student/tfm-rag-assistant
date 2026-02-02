"""
Tests para RAGService
Aquí probamos la búsqueda semántica y recuperación de contexto
"""
import pytest
from src.application.services.rag_service import RAGService
from src.domain.models.search_result import SearchResult


class TestRAGService:
    """Tests para el servicio RAG"""
    
    @pytest.fixture
    def service(self, mock_vector_repository):
        """Crear instancia del servicio con mock"""
        return RAGService(vector_repository=mock_vector_repository)
    
    def test_search_returns_results(self, service, mock_vector_repository, sample_search_results):
        """Test: Búsqueda devuelve resultados"""
        # Configuramos el mock para devolver resultados
        mock_vector_repository.similarity_search.return_value = sample_search_results
        
        # Ejecutamos búsqueda
        results = service.search(query="test query", k=2)
        
        # Verificaciones
        assert len(results) == 2
        assert results[0].similarity_score == 0.95
        assert results[1].similarity_score == 0.85
        
        # Verificamos que se llamó con los parámetros correctos
        mock_vector_repository.similarity_search.assert_called_once_with(
            "test query",
            k=2
        )
    
    def test_search_with_min_score_filter(self, service, mock_vector_repository, sample_chunks):
        """Test: Filtrar resultados por score mínimo"""
        # Creamos resultados con diferentes scores
        all_results = [
            SearchResult(chunk=sample_chunks[0], similarity_score=0.95, rank=1),
            SearchResult(chunk=sample_chunks[1], similarity_score=0.50, rank=2),
            SearchResult(chunk=sample_chunks[2], similarity_score=0.20, rank=3)
        ]
        mock_vector_repository.similarity_search.return_value = all_results
        
        # Buscamos con score mínimo de 0.4
        results = service.search(query="test", min_score=0.4)
        
        # Solo deberían pasar los 2 primeros resultados
        assert len(results) == 2
        assert all(r.similarity_score >= 0.4 for r in results)
    
    def test_search_empty_query(self, service, mock_vector_repository):
        """Test: Búsqueda con query vacío"""
        # Configuramos el mock para devolver lista vacía
        mock_vector_repository.similarity_search.return_value = []
        
        results = service.search(query="", k=5)
        
        # Debe devolver una lista (aunque esté vacía)
        assert isinstance(results, list)
    
    def test_get_context_from_results(self, service, mock_vector_repository, sample_search_results):
        """Test: Convertir búsqueda en contexto de texto"""
        # Configuramos el mock para devolver resultados
        mock_vector_repository.similarity_search.return_value = sample_search_results
        
        context = service.get_context("test query")
        
        # Verificamos que devuelve un string
        assert isinstance(context, str)
        assert len(context) > 0
    
    def test_get_context_empty_results(self, service, mock_vector_repository):
        """Test: Contexto cuando no hay resultados"""
        # Configuramos para que no haya resultados
        mock_vector_repository.similarity_search.return_value = []
        
        context = service.get_context("query sin resultados")
        
        # Debería devolver un mensaje indicando que no hay documentos
        assert "No relevant documents" in context or context == ""
    
    def test_search_with_default_parameters(self, service, mock_vector_repository):
        """Test: Búsqueda con parámetros por defecto"""
        mock_vector_repository.similarity_search.return_value = []
        
        # Búsqueda sin especificar k ni min_score
        service.search(query="test")
        
        # Debe usar los valores por defecto (k=4, min_score=0.0)
        mock_vector_repository.similarity_search.assert_called_once_with(
            "test",
            k=4  # default_k en el constructor
        )
