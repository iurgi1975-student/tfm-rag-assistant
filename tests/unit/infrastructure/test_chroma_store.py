"""
Tests para ChromaVectorStore - get_all_document_names()
Probamos la funcionalidad de obtener lista de documentos únicos
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from src.infrastructure.vector_stores.chroma_store import ChromaVectorStore
from src.domain.models.document import Document, DocumentChunk


class TestChromaVectorStoreDocumentNames:
    """Tests para el método get_all_document_names() de ChromaVectorStore"""
    
    @pytest.fixture
    def mock_chroma_client(self):
        """Mock del cliente de ChromaDB"""
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        return mock_client, mock_collection
    
    @pytest.fixture
    def chroma_store(self, mock_chroma_client):
        """Crear instancia de ChromaVectorStore con mocks"""
        mock_client, mock_collection = mock_chroma_client
        
        with patch('src.infrastructure.vector_stores.chroma_store.chromadb.PersistentClient', return_value=mock_client):
            with patch('src.infrastructure.vector_stores.chroma_store.HuggingFaceEmbeddings'):
                store = ChromaVectorStore(persist_dir="./test_db")
                store.collection = mock_collection
                return store
    
    def test_get_all_document_names_empty_collection(self, chroma_store, mock_chroma_client):
        """Test: Lista vacía cuando no hay documentos"""
        _, mock_collection = mock_chroma_client
        mock_collection.count.return_value = 0
        
        result = chroma_store.get_all_document_names()
        
        assert result == []
        mock_collection.count.assert_called_once()
    
    def test_get_all_document_names_only_pdfs(self, chroma_store, mock_chroma_client):
        """Test: Lista de PDFs únicos"""
        _, mock_collection = mock_chroma_client
        mock_collection.count.return_value = 5
        
        # Simular metadata de chunks de diferentes PDFs
        mock_collection.get.return_value = {
            "metadatas": [
                {"filename": "document1.pdf", "page": 1},
                {"filename": "document1.pdf", "page": 2},  # Duplicado
                {"filename": "document2.pdf", "page": 1},
                {"filename": "document3.pdf", "page": 1},
                {"filename": "document2.pdf", "page": 2},  # Duplicado
            ]
        }
        
        result = chroma_store.get_all_document_names()
        
        # Debería devolver solo nombres únicos, ordenados
        assert result == ["document1.pdf", "document2.pdf", "document3.pdf"]
        mock_collection.get.assert_called_once_with(include=["metadatas"])
    
    def test_get_all_document_names_with_paths(self, chroma_store, mock_chroma_client):
        """Test: Extrae nombres de archivo de paths completos"""
        _, mock_collection = mock_chroma_client
        mock_collection.count.return_value = 3
        
        # Simular metadata con paths completos (Windows y Unix)
        mock_collection.get.return_value = {
            "metadatas": [
                {"source": "C:\\Users\\Documents\\file1.pdf", "page": 1},
                {"source": "/home/user/documents/file2.pdf", "page": 1},
                {"filename": "file3.pdf", "page": 1},
            ]
        }
        
        result = chroma_store.get_all_document_names()
        
        # Debería extraer solo los nombres de archivo
        assert result == ["file1.pdf", "file2.pdf", "file3.pdf"]
    
    def test_get_all_document_names_with_manual_inputs(self, chroma_store, mock_chroma_client):
        """Test: Incluye contador de inputs manuales"""
        _, mock_collection = mock_chroma_client
        mock_collection.count.return_value = 5
        
        # Simular mezcla de PDFs e inputs manuales
        mock_collection.get.return_value = {
            "metadatas": [
                {"filename": "document.pdf", "page": 1},
                {"source": "manual_input", "type": "text"},
                {"source": "text_input", "type": "text"},
                {"source": "manual_input", "type": "text"},
                {"filename": "report.pdf", "page": 1},
            ]
        }
        
        result = chroma_store.get_all_document_names()
        
        # Debería tener PDFs + resumen de inputs manuales
        assert len(result) == 3
        assert "document.pdf" in result
        assert "report.pdf" in result
        assert "📝 Manual text inputs (3 chunks)" in result
    
    def test_get_all_document_names_only_manual_inputs(self, chroma_store, mock_chroma_client):
        """Test: Solo inputs manuales sin PDFs"""
        _, mock_collection = mock_chroma_client
        mock_collection.count.return_value = 4
        
        mock_collection.get.return_value = {
            "metadatas": [
                {"source": "manual_input", "type": "text"},
                {"source": "text_input", "type": "text"},
                {"source": "manual_input", "type": "text"},
                {"source": "text_input", "type": "text"},
            ]
        }
        
        result = chroma_store.get_all_document_names()
        
        # Debería devolver solo el resumen de inputs manuales
        assert len(result) == 1
        assert result[0] == "📝 Manual text inputs (4 chunks)"
    
    def test_get_all_document_names_handles_none_values(self, chroma_store, mock_chroma_client):
        """Test: Maneja correctamente metadatos con valores None"""
        _, mock_collection = mock_chroma_client
        mock_collection.count.return_value = 3
        
        mock_collection.get.return_value = {
            "metadatas": [
                {"filename": "document.pdf"},
                {"filename": None, "source": None},  # No debería aparecer
                {},  # Metadata vacío
            ]
        }
        
        result = chroma_store.get_all_document_names()
        
        # Solo debería devolver el documento válido
        assert result == ["document.pdf"]
    
    def test_get_all_document_names_handles_exception(self, chroma_store, mock_chroma_client):
        """Test: Retorna lista vacía en caso de excepción"""
        _, mock_collection = mock_chroma_client
        mock_collection.count.side_effect = Exception("Database error")
        
        result = chroma_store.get_all_document_names()
        
        # Debería retornar lista vacía sin propagar la excepción
        assert result == []
    
    def test_get_all_document_names_no_metadatas_in_response(self, chroma_store, mock_chroma_client):
        """Test: Maneja respuesta sin metadatas"""
        _, mock_collection = mock_chroma_client
        mock_collection.count.return_value = 1
        mock_collection.get.return_value = {}  # Sin metadatas
        
        result = chroma_store.get_all_document_names()
        
        assert result == []
    
    def test_get_all_document_names_mixed_source_and_filename(self, chroma_store, mock_chroma_client):
        """Test: Prioriza 'filename' sobre 'source' cuando ambos existen"""
        _, mock_collection = mock_chroma_client
        mock_collection.count.return_value = 2
        
        mock_collection.get.return_value = {
            "metadatas": [
                {"filename": "doc1.pdf", "source": "/path/to/doc1.pdf"},  # Usa filename
                {"source": "doc2.pdf"},  # Usa source
            ]
        }
        
        result = chroma_store.get_all_document_names()
        
        # Ambos deberían aparecer
        assert sorted(result) == ["doc1.pdf", "doc2.pdf"]
    
    def test_get_all_document_names_deduplication(self, chroma_store, mock_chroma_client):
        """Test: Elimina duplicados correctamente"""
        _, mock_collection = mock_chroma_client
        mock_collection.count.return_value = 10
        
        mock_collection.get.return_value = {
            "metadatas": [
                {"filename": "same.pdf", "page": 1},
                {"filename": "same.pdf", "page": 2},
                {"filename": "same.pdf", "page": 3},
                {"source": "C:\\path\\same.pdf"},  # Mismo archivo con path
                {"filename": "different.pdf", "page": 1},
                {"filename": "different.pdf", "page": 2},
            ]
        }
        
        result = chroma_store.get_all_document_names()
        
        # Solo deberían aparecer 2 documentos únicos
        assert len(result) == 2
        assert "same.pdf" in result
        assert "different.pdf" in result
