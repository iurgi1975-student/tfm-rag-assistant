# Plan de Implementación: RAG Multimodal para Planos Técnicos

**Arquitectura:** Clean Architecture / DDD  
**Objetivo:** Indexar y buscar imágenes técnicas (planos PDF, DXF, STEP) mediante embeddings CLIP y Gemini Vision

---

## Fase 0: Preparación

### 0.1 Git y Entorno
- [ ] Crear rama: `git checkout -b feature/multimodal-rag`
- [ ] Instalar dependencias: `torch`, `transformers`, `sentence-transformers`, `Pillow`, `PyMuPDF`
- [ ] Actualizar `requirements.txt` con nuevas dependencias
- [ ] Configurar `.env` con variables: `EMBEDDING_MODEL`, `USE_MULTIMODAL`, `ENABLE_VISION_LLM`

---

## Fase 1: Capa de Dominio (Domain Layer)

### 1.1 Extender Modelo Document
**Archivo:** `src/domain/models/document.py`
- [ ] Crear clase `ImageContent` con campos: `id`, `image_path`, `image_format`, `thumbnail_path`, `width`, `height`, `extracted_text`, `metadata`
- [ ] Extender `DocumentChunk` con: `content_type` ("text", "image", "multimodal"), `image_content`
- [ ] Extender `Document` con: `images: List[ImageContent]`, property `has_images`, property `image_count`
- [ ] Commit: `feat(domain): add ImageContent and multimodal support`

### 1.2 Extender VectorStoreRepository
**Archivo:** `src/domain/repositories/vector_store_repository.py`
- [ ] Añadir método abstracto: `add_images(images, document_id)`
- [ ] Añadir método abstracto: `search_images(query, k)`
- [ ] Añadir método abstracto: `search_hybrid(query, k_text, k_images)`
- [ ] Commit: `feat(domain): add multimodal methods to VectorStoreRepository`

### 1.3 Extender LLMRepository
**Archivo:** `src/domain/repositories/llm_repository.py`
- [ ] Añadir método abstracto: `invoke_with_images(messages, images)`
- [ ] Añadir método abstracto: `supports_vision() -> bool`
- [ ] Commit: `feat(domain): add vision methods to LLMRepository`

---

## Fase 2: Capa de Infraestructura (Infrastructure Layer)

### 2.1 Crear CLIPEmbeddings
**Archivo:** `src/infrastructure/vector_stores/clip_embeddings.py` (NUEVO)
- [ ] Clase `CLIPEmbeddings` con modelo CLIP local (sentence-transformers)
- [ ] Métodos: `embed_documents(texts)`, `embed_query(text)`, `embed_images(image_paths)`, `embed_image(path)`
- [ ] Auto-detección de device (CPU/CUDA)
- [ ] Dimensión: 512 para ViT-B-32
- [ ] Actualizar `__init__.py` para exportar
- [ ] Commit: `feat(infrastructure): add CLIPEmbeddings for multimodal embeddings`

### 2.2 Extender ChromaVectorStore
**Archivo:** `src/infrastructure/vector_stores/chroma_store.py`
- [ ] Reemplazar `HuggingFaceEmbeddings` por `CLIPEmbeddings`
- [ ] Cambiar `embedding_model` default a `"clip-ViT-B-32"`
- [ ] Añadir parámetro: `use_multimodal: bool = True`
- [ ] Crear colección adicional: `image_collection` (separada de texto)
- [ ] Implementar: `add_images()` - guarda imágenes en colección de imágenes
- [ ] Implementar: `search_images()` - busca en colección de imágenes
- [ ] Implementar: `search_hybrid()` - combina búsqueda texto + imágenes, rankea por score
- [ ] Commit: `feat(infrastructure): extend ChromaVectorStore with multimodal support`

### 2.3 Crear CADImageProcessor
**Archivo:** `src/infrastructure/cad_image_processor.py` (NUEVO)
- [ ] Clase `CADImageProcessor` para procesamiento de planos
- [ ] Método: `extract_from_pdf(pdf_path)` - extrae imágenes embebidas con PyMuPDF
- [ ] Método: `convert_dxf_to_image(dxf_path)` - renderiza DXF a PNG con ezdxf + matplotlib
- [ ] Método: `create_thumbnail(image_path, size)` - genera thumbnails
- [ ] Método auxiliar: `_extract_dxf_text()` - OCR básico de bloques de título
- [ ] Guardar imágenes en `./data/extracted_images/`
- [ ] Commit: `feat(infrastructure): add CADImageProcessor for PDF/DXF extraction`

### 2.4 Extender DocumentProcessor
**Archivo:** `src/infrastructure/document_processor.py`
- [ ] Inyectar `CADImageProcessor` en `__init__`
- [ ] Extender `load_document()` para soportar `.dxf` (además de `.pdf`)
- [ ] Modificar `_load_pdf()`: después de extraer texto, extraer imágenes con CAD processor
- [ ] Añadir imágenes extraídas a `document.images`
- [ ] Crear `DocumentChunk` tipo "image" por cada imagen
- [ ] Nuevo método: `_load_dxf()` - convierte DXF a imagen, crea documento con chunk imagen
- [ ] Commit: `feat(infrastructure): extend DocumentProcessor to extract images`

### 2.5 Extender GoogleGeminiLLM
**Archivo:** `src/infrastructure/llm/google_gemini_llm.py`
- [ ] Implementar: `supports_vision()` - retorna True para modelos Gemini 2.0+
- [ ] Implementar: `invoke_with_images(messages, images)`:
  - Cargar imágenes con PIL
  - Formatear prompt desde messages
  - Llamar a `model.generate_content([prompt] + images)`
  - Validar máximo 4 imágenes
- [ ] Commit: `feat(infrastructure): add vision support to GoogleGeminiLLM`

---

## Fase 3: Capa de Aplicación (Application Layer)

### 3.1 Extender DocumentService
**Archivo:** `src/application/services/document_service.py`
- [ ] Modificar `ingest_document()`:
  - Después de `add_documents()`, verificar si hay imágenes
  - Si `document.has_images`: llamar a `repository.add_images(document.images, document.id)`
  - Añadir log: "📸 Adding X images from {title}"
- [ ] Commit: `feat(application): extend DocumentService to handle images`

### 3.2 Extender RAGService
**Archivo:** `src/application/services/rag_service.py`
- [ ] Nuevo método: `search_with_images(query, include_images, k_text, k_images, min_score)`:
  - Llama a `repository.search_hybrid()` si `include_images=True`
  - Separa resultados en `text_results`, `image_results`, `combined`
  - Retorna diccionario con los tres tipos
- [ ] Nuevo método: `format_multimodal_context(results)`:
  - Formatea texto + referencias a imágenes
  - Retorna tuple: `(formatted_text, image_paths)`
- [ ] Commit: `feat(application): add multimodal search to RAGService`

### 3.3 Extender ChatService
**Archivo:** `src/application/services/chat_service.py`
- [ ] Modificar `chat()`:
  - Añadir parámetro: `max_context_images: int = 3`
  - Al usar RAG, llamar a `search_with_images()`
  - Formatear contexto multimodal con `format_multimodal_context()`
  - Si hay imágenes Y `llm.supports_vision()`:
    - Usar `llm.invoke_with_images()` en lugar de `invoke()`
    - Limitar imágenes a `max_context_images`
  - Si no hay soporte vision: solo usar texto
- [ ] Commit: `feat(application): add multimodal context to ChatService`

### 3.4 Actualizar Container
**Archivo:** `src/application/container.py`
- [ ] Añadir imports: `CADImageProcessor`
- [ ] Añadir parámetros `__init__`: `embedding_model`, `use_multimodal`, `max_context_images`
- [ ] Añadir property: `cad_processor` - instancia `CADImageProcessor()`
- [ ] Modificar property `vector_store`: pasar `embedding_model` y `use_multimodal` a `ChromaVectorStore`
- [ ] Modificar property `document_processor`: inyectar `cad_processor`
- [ ] Commit: `feat(application): add multimodal configuration to AppContainer`

---

## Fase 4: Capa de Interfaz (Interface Layer)

### 4.1 Extender Gradio
**Archivo:** `src/interface/gradio_chat.py`

#### 4.1.1 Extender carga de archivos
- [ ] Modificar `process_uploaded_files()`:
  - Aceptar extensiones: `.pdf`, `.dxf`, `.txt`
  - Contar y mostrar imágenes extraídas
  - Mensaje: "Added X documents, Y images"

#### 4.1.2 Nueva tab: Búsqueda Visual
- [ ] Dentro de `create_interface()`, añadir tab "🔍 Búsqueda Visual"
- [ ] Componentes:
  - Textbox: query de búsqueda
  - Checkbox: "Incluir imágenes"
  - Sliders: k_text (1-10), k_images (1-10)
  - Botón: "Buscar"
  - Output: Markdown con resultados
  - Gallery: imágenes encontradas
- [ ] Handler: `visual_search_handler(query, include_images, k_text, k_images)`:
  - Llama a `rag_service.search_with_images()`
  - Formatea resultados en markdown
  - Retorna texto + lista de paths de imágenes para gallery

#### 4.1.3 Mejorar tab de chat
- [ ] Indicador visual cuando se usa contexto multimodal
- [ ] Mostrar thumbnails de imágenes usadas en contexto (opcional)

- [ ] Commit: `feat(interface): add visual search tab to Gradio interface`

---

## Fase 5: Testing y Verificación

### 5.1 Tests Unitarios Domain
**Archivos:** `tests/unit/domain/test_image_content.py` (NUEVO)
- [ ] Test creación `ImageContent`
- [ ] Test properties de `Document` (`has_images`, `image_count`)
- [ ] Test `DocumentChunk` con `content_type="image"`

### 5.2 Tests Unitarios Infrastructure
**Archivos:** 
- `tests/unit/infrastructure/test_clip_embeddings.py` (NUEVO)
  - [ ] Test `embed_documents()` con textos
  - [ ] Test `embed_images()` con imágenes mock
  - [ ] Test dimensiones = 512
  - [ ] Test mismo espacio vectorial (cosine similarity texto-imagen)

- `tests/unit/infrastructure/test_cad_image_processor.py` (NUEVO)
  - [ ] Test `extract_from_pdf()` con PDF ejemplo
  - [ ] Test `convert_dxf_to_image()` con DXF ejemplo
  - [ ] Test `create_thumbnail()`

### 5.3 Tests Unitarios Application
- Extender `tests/unit/application/test_document_service.py`
  - [ ] Test `ingest_document()` con PDF que contiene imágenes
  - [ ] Verificar llamada a `add_images()`

- Extender `tests/unit/application/test_rag_service.py`
  - [ ] Test `search_with_images()`
  - [ ] Test `format_multimodal_context()`

### 5.4 Test End-to-End
- [ ] Ejecutar: `python app.py`
- [ ] Subir PDF con planos en "Document Management"
- [ ] Verificar log: "📸 Adding X images"
- [ ] Ir a tab "Búsqueda Visual", buscar keyword relevante
- [ ] Verificar resultados: texto + gallery de imágenes
- [ ] En chat, hacer pregunta sobre planos
- [ ] Verificar log: "👁️ Using vision LLM with X images"

---

## Fase 6: Finalización

### 6.1 Documentación
- [ ] Actualizar `README.md` con features multimodales
- [ ] Crear `Documentación/MULTIMODAL_RAG.md` con:
  - Casos de uso
  - Formatos soportados
  - Configuración
  - Limitaciones

### 6.2 Git
- [ ] Revisar todos los commits
- [ ] Asegurar que cada commit es atómico y tiene mensaje descriptivo
- [ ] Push rama: `git push origin feature/multimodal-rag`
- [ ] Crear PR si aplica

### 6.3 Merge a Main
- [ ] Revisar cambios
- [ ] Merge a main: `git checkout main && git merge feature/multimodal-rag`
- [ ] Tag release: `git tag v2.0.0-multimodal`

---

## Checklist de Verificación

### Funcionalidad Core
- [ ] CLIP descarga y funciona localmente
- [ ] Embeddings de texto generan 512 dimensiones
- [ ] Embeddings de imagen generan 512 dimensiones
- [ ] ChromaDB crea 2 colecciones (text + images)
- [ ] PDF extrae imágenes correctamente
- [ ] DXF convierte a PNG
- [ ] Búsqueda híbrida rankea correctamente
- [ ] Gemini Vision recibe y procesa imágenes

### Arquitectura
- [ ] Dominio no depende de infraestructura
- [ ] Inyección de dependencias funciona
- [ ] Backward compatibility: código sin imágenes sigue funcionando
- [ ] Separación de concerns respetada

### Performance
- [ ] Primera carga CLIP < 30 segundos
- [ ] Embedding de imagen < 3 segundos
- [ ] Búsqueda híbrida < 2 segundos
- [ ] Respuesta con vision < 10 segundos

---

## Próximos Pasos (Opcional)

### Features Adicionales
- [ ] **VisionService**: Comparación directa de 2-4 planos sin RAG
- [ ] **OCR avanzado**: EasyOCR para extraer texto técnico de planos
- [ ] **STEP support**: pythonOCC para renderizar modelos 3D
- [ ] **Cache de embeddings**: Persistir embeddings para no recalcular
- [ ] **Filtros avanzados**: Por tipo de plano, fecha, proyecto

### Optimizaciones
- [ ] Batch processing de múltiples archivos
- [ ] Compresión de imágenes grandes
- [ ] Modelos CLIP más grandes (ViT-L-14) para mejor calidad
- [ ] GPU acceleration si disponible

---

**Versión:** 1.0  
**Fecha:** 2026-02-22  
**Estimación:** 2-3 semanas para implementación completa