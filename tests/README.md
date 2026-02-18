# Tests Unitarios - RAG AI Assistant

## 📋 Resumen

Este proyecto tiene **27 tests unitarios** que validan toda la arquitectura DDD:

- ✅ **Domain Models** (8 tests): Document, DocumentChunk, ChatMessage, SearchResult
- ✅ **Application Services** (19 tests): DocumentService, RAGService, ChatService

## 🚀 Cómo ejecutar los tests

### Instalar dependencias
```bash
pip install pytest pytest-cov pytest-mock
```

### Ejecutar todos los tests
```bash
pytest tests/
```

### Ejecutar tests con output detallado
```bash
pytest tests/ -v
```

### Ejecutar solo tests de un archivo
```bash
pytest tests/unit/domain/test_models.py -v
pytest tests/unit/application/test_chat_service.py -v
```

### Ejecutar con cobertura (coverage)
```bash
pytest tests/ --cov=src --cov-report=term
```

## 📁 Estructura de Tests

```
tests/
├── conftest.py                          # Fixtures compartidas (mocks y datos de ejemplo)
├── unit/
│   ├── domain/
│   │   └── test_models.py              # Tests de modelos del dominio
│   └── application/
│       ├── test_document_service.py     # Tests del servicio de documentos
│       ├── test_rag_service.py          # Tests del servicio RAG
│       └── test_chat_service.py         # Tests del servicio de chat
```

## 🧪 ¿Qué son los tests unitarios?

Los **tests unitarios** son pequeñas pruebas automáticas que verifican que cada pieza de código funciona correctamente **de forma aislada**.

### Ventajas:
- ✅ Detectan bugs antes de que lleguen a producción
- ✅ Documentan cómo usar el código
- ✅ Facilitan refactorizar sin miedo a romper cosas
- ✅ Aumentan la confianza en el código

## 📖 Cómo funcionan los tests

### 1. **Fixtures** (en `conftest.py`)
Son datos y objetos de ejemplo que se reutilizan en múltiples tests:

```python
@pytest.fixture
def sample_document():
    """Documento de ejemplo para tests"""
    return Document(
        id="doc-123",
        title="test.txt",
        content="Contenido de prueba"
    )
```

### 2. **Mocks**
Son "objetos falsos" que simulan componentes externos (LLM, Base de datos, etc.):

```python
@pytest.fixture
def mock_llm_repository():
    """Mock del LLM - devuelve respuestas predefinidas"""
    mock = Mock()
    mock.invoke = Mock(return_value="Respuesta simulada")
    return mock
```

**¿Por qué usar mocks?**
- No necesitamos Ollama corriendo para ejecutar tests
- Los tests son rápidos (milisegundos en lugar de segundos)
- Podemos controlar exactamente qué devuelve cada componente

### 3. **Assertions**
Son comprobaciones que verifican que el código funciona como esperamos:

```python
def test_create_document():
    doc = Document(id="123", title="test.txt", ...)
    
    # Verificamos que se creó correctamente
    assert doc.id == "123"
    assert doc.title == "test.txt"
```

## 📝 Ejemplos de Tests

### Test Simple: Validar un Modelo
```python
def test_create_user_message():
    """Test: Crear mensaje de usuario"""
    msg = ChatMessage(
        role=MessageRole.USER,
        content="Hola"
    )
    
    assert msg.role == MessageRole.USER
    assert msg.content == "Hola"
```

### Test con Mock: Servicio de Chat
```python
def test_chat_without_rag(mock_llm_repository):
    """Test: Chat sin usar RAG"""
    # Configuramos el mock para devolver una respuesta
    mock_llm_repository.invoke.return_value = "Respuesta simulada"
    
    # Creamos el servicio con el mock
    service = ChatService(llm=mock_llm_repository, rag_service=None)
    
    # Ejecutamos el chat
    response = service.chat(message="Hola", use_rag=False)
    
    # Verificamos que funciona
    assert response == "Respuesta simulada"
    assert mock_llm_repository.invoke.called
```

### Test de Validación: Detectar Errores
```python
def test_message_validation_empty_content():
    """Test: No permitir mensajes vacíos"""
    with pytest.raises(ValueError, match="Message content cannot be empty"):
        ChatMessage(role=MessageRole.USER, content="")
```

## 🎯 Cobertura de Tests

Los tests cubren:

### ✅ Domain Layer (Capa de Dominio)
- **Document**: Creación, validación de atributos
- **DocumentChunk**: Creación con chunk_index, metadata
- **ChatMessage**: Validación de contenido, roles, conversión dict
- **SearchResult**: Creación, validación de scores

### ✅ Application Layer (Capa de Aplicación)

**DocumentService:**
- ✅ Ingerir documento desde archivo
- ✅ Ingerir texto directo
- ✅ Manejo de errores (archivo no existe)
- ✅ Limpiar base de conocimiento
- ✅ Obtener estadísticas

**RAGService:**
- ✅ Búsqueda semántica
- ✅ Filtrado por score mínimo
- ✅ Parámetros por defecto
- ✅ Conversión a contexto de texto

**ChatService:**
- ✅ Chat sin RAG (solo LLM)
- ✅ Chat con RAG (LLM + contexto)
- ✅ Streaming de respuestas
- ✅ Gestión de historial
- ✅ Límite de memoria (memory window)

## 🔍 Interpretando los Resultados

### Salida Exitosa ✅
```bash
tests/unit/domain/test_models.py::TestDocument::test_create_document PASSED
tests/unit/application/test_chat_service.py::TestChatService::test_chat_with_rag PASSED

======================== 27 passed in 0.47s ========================
```

### Salida con Fallos ❌
```bash
FAILED tests/unit/domain/test_models.py::TestDocument::test_create_document
E       AssertionError: assert 'test.pdf' == 'test.txt'
E       + where 'test.pdf' = doc.title

======================== 1 failed, 26 passed in 0.5s ========================
```

## 🛠️ Debugging de Tests

### Ver más detalles de fallos
```bash
pytest tests/ -v --tb=short
```

### Ejecutar solo un test específico
```bash
pytest tests/unit/domain/test_models.py::TestChatMessage::test_create_user_message -v
```

### Ver prints en los tests
```bash
pytest tests/ -s
```

## 💡 Conceptos Clave

### AAA Pattern (Arrange-Act-Assert)
Todos nuestros tests siguen este patrón:

```python
def test_example():
    # ARRANGE: Preparar datos y mocks
    mock_llm = Mock()
    mock_llm.invoke.return_value = "Respuesta"
    service = ChatService(llm=mock_llm)
    
    # ACT: Ejecutar la acción a probar
    response = service.chat("Hola")
    
    # ASSERT: Verificar el resultado
    assert response == "Respuesta"
    assert mock_llm.invoke.called
```

### Test Isolation (Aislamiento)
Cada test es independiente:
- No dependen de otros tests
- No modifican estado compartido
- Se pueden ejecutar en cualquier orden

### Mocking vs Integration Tests
- **Unit Tests** (los que tenemos): Usan mocks, son rápidos, prueban lógica
- **Integration Tests** (futuro): Usan componentes reales, son lentos, prueban integración


¡Los tests son tu red de seguridad! 🛡️ Úsalos con frecuencia para desarrollar con confianza.
