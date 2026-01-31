src/
├── core/                    # Configuración y utilidades
│   ├── config.py           # Variables de entorno, settings
│   └── logging.py          # Setup de logging centralizado
├── domain/                  # Reglas de negocio (independiente de tech)
│   ├── models/             # DTOs y entidades (Pydantic)
│   │   ├── document.py
│   │   ├── chat_message.py
│   │   └── search_result.py
│   └── repositories/        # INTERFACES (abstracciones)
│       └── vector_store_repository.py  # Contrato para cualquier BD vectorial
├── infrastructure/          # Implementaciones técnicas
│   ├── vector_stores/      # Implementaciones concretas
│   │   ├── chroma_store.py # ChromaDB
│   │   └── factory.py      # Factory pattern para crear stores
│   └── document_processor.py # Procesamiento de PDFs
├── application/             # Casos de uso y servicios
│   ├── services/           # Lógica de negocio
│   │   ├── document_service.py
│   │   ├── rag_service.py
│   │   └── chat_service.py (futuro)
│   └── use_cases/          # Opcional: comandos/queries
└── interface/               # Adaptadores externos
    ├── gradio_chat.py      # UI
    └── api/                # Futuro: REST API 