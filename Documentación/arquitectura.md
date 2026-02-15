# 🏗️ Arquitectura del Proyecto

> **Patrón**: Domain-Driven Design (DDD) con Clean Architecture  
> Ver documentación completa en: [`README.md`](../README.md)

---

## 📂 Estructura del Proyecto

```
module-5/
├── app.py                          # 🚀 Entry point de la aplicación
├── requirements.txt                # 📦 Dependencias Python
├── pyproject.toml                  # ⚙️ Configuración de pytest y coverage
├── docker-compose.yml              # 🐳 Orquestación de contenedores
├── Dockerfile                      # 🐳 Imagen Docker de producción
├── .env / .env.example             # 🔐 Variables de entorno
│
├── src/                            # 📁 Código fuente principal
│   │
│   ├── domain/                     # 🎯 CAPA DE DOMINIO (Core Business Logic)
│   │   ├── models/                 # Entidades y DTOs (Pydantic)
│   │   │   ├── chat_message.py    # Mensaje de chat (usuario/asistente)
│   │   │   ├── document.py        # Documento con metadata
│   │   │   └── search_result.py   # Resultado de búsqueda vectorial
│   │   │
│   │   └── repositories/           # INTERFACES (contratos abstractos)
│   │       ├── vector_store_repository.py    # Contrato para BD vectorial
│   │       ├── llm_repository.py             # Contrato para LLMs
│   │       └── chat_history_repository.py    # Contrato para persistencia de chat
│   │
│   ├── infrastructure/             # 🔧 CAPA DE INFRAESTRUCTURA (Implementaciones)
│   │   ├── llm/                    # Implementaciones de modelos LLM
│   │   │   ├── ollama_llm.py      # LLM local (Ollama)
│   │   │   └── google_gemini_llm.py # LLM cloud (Google Gemini)
│   │   │
│   │   ├── vector_stores/          # Implementaciones de bases vectoriales
│   │   │   └── chroma_store.py    # ChromaDB con embeddings
│   │   │
│   │   ├── persistence/            # Persistencia de datos
│   │   │   └── sqlite_chat_repository.py # Historial de chat en SQLite
│   │   │
│   │   ├── document_processor.py  # Procesamiento y chunking de PDFs
│   │   └── mappers.py             # Transformaciones entre capas
│   │
│   ├── application/                # 💼 CAPA DE APLICACIÓN (Casos de uso)
│   │   ├── container.py           # ⚡ Dependency Injection Container
│   │   │
│   │   └── services/              # Servicios de lógica de negocio
│   │       ├── document_service.py # Gestión de documentos (carga, limpieza)
│   │       ├── rag_service.py     # Lógica RAG (búsqueda + generación)
│   │       └── chat_service.py    # Gestión de conversaciones
│   │
│   └── interface/                 # 🖥️ CAPA DE INTERFAZ (Adaptadores externos)
│       └── gradio_chat.py         # UI web interactiva con Gradio
│
├── tests/                         # 🧪 Suite de pruebas (27 tests)
│   ├── conftest.py               # Fixtures compartidos
│   ├── unit/                     # Tests unitarios
│   │   ├── domain/              # Tests de modelos
│   │   │   └── test_models.py
│   │   └── application/         # Tests de servicios
│   │       ├── test_chat_service.py
│   │       ├── test_document_service.py
│   │       └── test_rag_service.py
│   │
│   ├── COVERAGE_REPORT.md        # Reporte de cobertura
│   ├── GUIA_RAPIDA.md           # Guía rápida de tests
│   └── README.md                 # Documentación de tests
│
├── Documentación/                 # 📚 Documentación del proyecto
│   ├── arquitectura.md           # 👈 Este archivo
│   ├── diagrama_de_secuencia.md # Diagramas de flujo
│   ├── esquema.md               # Esquemas adicionales
│   ├── DOCKER_DEPLOYMENT.md      # Guía de despliegue Docker
│   ├── CLOUDRUN_DEPLOYMENT.md    # Guía de despliegue Cloud Run
│   └── LOGIN_GUIDE.md           # Guía de autenticación
│
├── data/                          # 💾 Datos persistentes
│   └── chat_history.db           # Base de datos SQLite
│
├── chroma_db/                     # 🗄️ Base de datos vectorial ChromaDB
│
├── logs/                          # 📋 Logs de la aplicación
│
└── venv/                          # 🐍 Entorno virtual Python
```

---

## 📊 Diagrama de Capas DDD

```
┌─────────────────────────────────────┐
│     Interface Layer (Gradio)        │
│         gradio_chat.py              │
└──────────────┬──────────────────────┘
               │ usa servicios
┌──────────────▼──────────────────────┐
│    Application Layer (Services)     │
│  Chat, Document, RAG + Container    │
└──────────────┬──────────────────────┘
               │ usa interfaces
┌──────────────▼──────────────────────┐
│     Domain Layer (Core)             │
│  Models + Repository Interfaces     │
└──────────────▲──────────────────────┘
               │ implementa
┌──────────────┴──────────────────────┐
│  Infrastructure Layer (Tech)        │
│  LLM, VectorStore, Persistence      │
└─────────────────────────────────────┘
```

**Flujo de dependencias**: Interface → Application → Domain ← Infrastructure


---

**Última actualización**: Febrero 15, 2026