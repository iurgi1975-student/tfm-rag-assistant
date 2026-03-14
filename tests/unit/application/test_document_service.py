"""
Tests para DocumentService
Aquí probamos la lógica de negocio para gestionar documentos
"""
import pytest
from unittest.mock import Mock
from src.application.services.document_service import DocumentService
from src.domain.models.document import DocumentChunk


class TestDocumentService:
    """Tests para el servicio de documentos"""
    
    @pytest.fixture
    def service(self, mock_vector_repository, mock_document_processor):
        """Crear instancia del servicio con mocks"""
        return DocumentService(
            vector_repository=mock_vector_repository,
            document_processor=mock_document_processor
        )
    
    def test_ingest_document_success(self, service, mock_document_processor, mock_vector_repository, sample_document):
        """Test: Ingerir documento exitosamente"""
        # Configuramos el mock para que devuelva un documento
        mock_document_processor.load_document.return_value = [sample_document]
        
        # Ejecutamos la ingestión (pero necesitamos un archivo real o mockearlo)
        # Como el servicio valida que el archivo existe, saltaremos este test o crearemos uno temporal
        import tempfile
        import os
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Test content")
            temp_file = f.name
        
        try:
            result = service.ingest_document(temp_file)
            
            # Verificaciones
            assert result["chunks"] == 1
            
            # Verificamos que se llamaron los métodos correctos
            mock_document_processor.load_document.assert_called_once_with(temp_file)
            mock_vector_repository.add_documents.assert_called_once()
        finally:
            # Limpiar archivo temporal
            os.unlink(temp_file)
    
    def test_ingest_document_file_not_found(self, service, mock_document_processor):
        """Test: Error al ingerir documento que no existe"""
        # El servicio valida que el archivo existe antes de procesarlo
        # Ejecutamos con un archivo que no existe
        with pytest.raises(FileNotFoundError, match="File not found"):
            service.ingest_document("noexiste.txt")
    
    def test_ingest_text_success(self, service, mock_document_processor, mock_vector_repository, sample_document):
        """Test: Ingerir texto directamente"""
        # Configuramos el mock - devuelve lista de documentos
        documents_list = [sample_document]
        mock_document_processor.process_text_input.return_value = documents_list
        
        # Ejecutamos
        result = service.ingest_text("Texto de prueba")
        
        # Verificaciones
        assert result == 1
        
        mock_document_processor.process_text_input.assert_called_once()
        mock_vector_repository.add_documents.assert_called_once_with(documents_list)
    
    def test_clear_knowledge_base(self, service, mock_vector_repository):
        """Test: Limpiar la base de conocimiento"""
        service.clear_knowledge_base()
        
        # Verificamos que se llamó al método clear
        mock_vector_repository.clear.assert_called_once()
    
    def test_get_document_stats(self, service, mock_vector_repository):
        """Test: Obtener estadísticas de documentos"""
        # Configuramos el mock para devolver count
        mock_vector_repository.get_document_count.return_value = 10
        
        # Obtenemos las estadísticas
        stats = service.get_document_stats()
        
        # Verificaciones
        assert stats["total_documents"] == 10
        assert stats["status"] == "ready"
        mock_vector_repository.get_document_count.assert_called_once()
