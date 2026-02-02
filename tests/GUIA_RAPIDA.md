# 🧪 Guía Rápida de Tests - RAG AI Assistant

## ✅ Estado Actual: 27/27 Tests Pasando

```
tests/unit/application/test_chat_service.py    ✅ 6 tests
tests/unit/application/test_document_service.py ✅ 5 tests  
tests/unit/application/test_rag_service.py      ✅ 6 tests
tests/unit/domain/test_models.py                ✅ 10 tests
─────────────────────────────────────────────────────────
TOTAL:                                          ✅ 27 tests
```

## 🚀 Comandos Básicos

```bash
# Ejecutar todos los tests
pytest tests/

# Solo tests de dominio
pytest tests/unit/domain/

# Solo tests de servicios
pytest tests/unit/application/

# Con detalles
pytest tests/ -v
```

## 📊 Resumen por Componente

### 🎯 Domain Models (10 tests)

| Modelo | Tests | Qué valida |
|--------|-------|------------|
| **Document** | 2 | Creación y atributos |
| **DocumentChunk** | 1 | Creación con índice |
| **ChatMessage** | 5 | Roles, validación, conversión |
| **SearchResult** | 2 | Scores y rankings |

### ⚙️ Application Services (17 tests)

| Servicio | Tests | Qué valida |
|----------|-------|------------|
| **DocumentService** | 5 | Ingestión, limpieza, stats |
| **RAGService** | 6 | Búsqueda, filtrado, contexto |
| **ChatService** | 6 | Chat, RAG, streaming, historial |

## 🔍 Ejemplos Prácticos

### Ejemplo 1: Test de Modelo Simple
```python
def test_create_user_message():
    """Verifica que podemos crear un mensaje de usuario"""
    msg = ChatMessage(
        role=MessageRole.USER,
        content="Hola"
    )
    assert msg.role == MessageRole.USER
    assert msg.content == "Hola"
```

**¿Qué hace?** Crea un mensaje y verifica que los datos son correctos.

### Ejemplo 2: Test con Mock
```python
def test_chat_without_rag(mock_llm_repository):
    """Verifica que el chat funciona sin RAG"""
    # 1. Configurar mock (simular LLM)
    mock_llm_repository.invoke.return_value = "Hola!"
    
    # 2. Crear servicio
    service = ChatService(llm=mock_llm_repository, rag_service=None)
    
    # 3. Ejecutar
    response = service.chat(message="Hola", use_rag=False)
    
    # 4. Verificar
    assert response == "Hola!"
```

**¿Qué hace?** Simula el LLM y verifica que ChatService lo usa correctamente.

### Ejemplo 3: Test de Validación
```python
def test_message_validation_empty_content():
    """Verifica que no se permiten mensajes vacíos"""
    with pytest.raises(ValueError):
        ChatMessage(role=MessageRole.USER, content="")
```

**¿Qué hace?** Verifica que el código detecta y rechaza datos inválidos.

## 🎓 Conceptos Clave

### ¿Qué es un Mock?
Un **mock** es un objeto "falso" que simula un componente real:

```python
# En vez de usar el LLM real (Ollama):
mock_llm = Mock()
mock_llm.invoke.return_value = "Respuesta simulada"

# Ventajas:
✅ Tests rápidos (milisegundos)
✅ No necesitas Ollama corriendo
✅ Controlas exactamente qué devuelve
```

### ¿Qué es un Fixture?
Un **fixture** es un dato reutilizable:

```python
@pytest.fixture
def sample_document():
    return Document(id="123", title="test.txt", ...)

# Uso en test:
def test_something(sample_document):  # ← pytest lo inyecta automáticamente
    assert sample_document.id == "123"
```

### Pattern AAA (Arrange-Act-Assert)
Todos los tests siguen esta estructura:

```python
def test_example():
    # ARRANGE (Preparar)
    service = ChatService(...)
    
    # ACT (Actuar)
    result = service.chat("Hola")
    
    # ASSERT (Verificar)
    assert result == "Respuesta esperada"
```

## 📁 Arquitectura de Tests

```
tests/
├── conftest.py              ← Fixtures compartidas (mocks, datos ejemplo)
└── unit/
    ├── domain/              ← Tests de modelos puros
    │   └── test_models.py
    └── application/         ← Tests de servicios (lógica de negocio)
        ├── test_document_service.py
        ├── test_rag_service.py
        └── test_chat_service.py
```

## 🛠️ Debugging

### Ver más información de fallos
```bash
pytest tests/ --tb=short
```

### Ejecutar un test específico
```bash
pytest tests/unit/domain/test_models.py::TestChatMessage::test_create_user_message
```

### Ver prints durante tests
```bash
pytest tests/ -s
```

## ✨ Buenas Prácticas

### ✅ DO (Hacer)
- Un test por funcionalidad
- Nombres descriptivos (`test_chat_with_rag` ✅)
- Tests independientes (no dependen entre sí)
- Usar mocks para dependencias externas

### ❌ DON'T (No hacer)
- Tests que dependen del orden de ejecución
- Tests lentos (más de 1 segundo)
- Tests que modifican archivos reales
- Nombres vagos (`test_1`, `test_cosa` ❌)

## 🎯 ¿Por qué hacer tests?

1. **Confianza**: Saber que tu código funciona
2. **Documentación**: Los tests muestran cómo usar el código
3. **Refactoring seguro**: Cambiar código sin miedo a romper cosas
4. **Bugs tempranos**: Detectar problemas antes de producción

## 📈 Próximos Pasos

1. ✅ **Tests Unitarios** (HECHO) - 27 tests con mocks
2. ⏳ **Integration Tests** - Con Ollama y ChromaDB reales
3. ⏳ **CI/CD** - GitHub Actions para ejecutar tests automáticamente
4. ⏳ **Coverage** - Medir qué % del código está testeado

## 💡 Tips para Aprender

### 1. Ejecuta los tests frecuentemente
```bash
# Cada vez que cambies código:
pytest tests/
```

### 2. Rompe algo intencionalmente
```python
# En ChatService, cambia algo:
def chat(self, message: str, ...):
    return "Siempre devuelvo esto"  # ← Romper el código

# Ejecuta tests y ve qué test falla
```

### 3. Crea tu propio test
```python
def test_mi_experimento():
    """Descripción de qué pruebo"""
    # Tu código aquí
    assert True
```

### 4. Lee los tests existentes
Los tests son **ejemplos vivos** de cómo usar el código.

---

**¡Los tests son tu mejor amigo al programar!** 🎉

Ejecuta `pytest tests/ -v` y observa cómo cada componente es validado automáticamente.
