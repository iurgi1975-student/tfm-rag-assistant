```mermaid
sequenceDiagram
    participant User as 👤 Usuario
    participant UI as Interface Layer<br/>gradio_chat.py<br/>ChatInterface
    participant ChatSvc as Application Layer<br/>chat_service.py<br/>ChatService
    participant RAGSvc as Application Layer<br/>rag_service.py<br/>RAGService
    participant VectorRepo as Domain<br/>VectorStoreRepository<br/>(Interface)
    participant ChromaDB as Infrastructure<br/>chroma_store.py<br/>ChromaStore
    participant LLMRepo as Domain<br/>LLMRepository<br/>(Interface)
    participant LLM as Infrastructure<br/>google_gemini_llm.py<br/>GoogleGeminiLLM
    participant ChatRepo as Domain<br/>ChatHistoryRepository<br/>(Interface)
    participant SQLite as Infrastructure<br/>sqlite_chat_repository.py<br/>SQLiteChatRepository
    participant Mapper as Infrastructure<br/>mappers.py<br/>ChatMessageMapper

    User->>UI: Click Submit Button
    Note over UI: submit_btn.click evento
    UI->>UI: submit_message(message, history)
    UI->>UI: chat_response(message, history)
    
    UI->>ChatSvc: chat(message, stream=False, use_rag=True)
    
    alt use_rag=True
        ChatSvc->>RAGSvc: get_context(message)
        RAGSvc->>VectorRepo: search(query, k=5)
        VectorRepo->>ChromaDB: search(query, k)
        Note over ChromaDB: Busca en ChromaDB<br/>vectores similares
        ChromaDB-->>VectorRepo: List[SearchResult]
        VectorRepo-->>RAGSvc: List[SearchResult]
        RAGSvc-->>ChatSvc: context (str)
    end
    
    Note over ChatSvc: Construye system_prompt<br/>con contexto RAG
    
    ChatSvc->>ChatSvc: _get_trimmed_history()
    Note over ChatSvc: Obtiene últimos N mensajes<br/>de self._chat_history
    
    ChatSvc->>ChatSvc: Construye messages[]<br/>[SYSTEM, ...history, USER]
    
    ChatSvc->>LLMRepo: invoke(messages)
    LLMRepo->>LLM: invoke(messages)
    Note over LLM: Llamada a Gemini API
    LLM-->>LLMRepo: response_text (str)
    LLMRepo-->>ChatSvc: response_text
    
    Note over ChatSvc: Crea ChatMessage(USER)<br/>Crea ChatMessage(ASSISTANT)
    
    ChatSvc->>ChatSvc: _chat_history.append(user_msg)
    ChatSvc->>ChatSvc: _chat_history.append(assistant_msg)
    
    ChatSvc->>ChatRepo: save_message(session_id, user_msg)
    ChatRepo->>SQLite: save_message(session_id, user_msg)
    SQLite->>Mapper: to_persistence(user_msg)
    Mapper-->>SQLite: (role, content, timestamp)
    Note over SQLite: INSERT INTO chat_messages
    SQLite-->>ChatRepo: ✓
    ChatRepo-->>ChatSvc: ✓
    
    ChatSvc->>ChatRepo: save_message(session_id, assistant_msg)
    ChatRepo->>SQLite: save_message(session_id, assistant_msg)
    SQLite->>Mapper: to_persistence(assistant_msg)
    Mapper-->>SQLite: (role, content, timestamp)
    Note over SQLite: INSERT INTO chat_messages
    SQLite-->>ChatRepo: ✓
    ChatRepo-->>ChatSvc: ✓
    
    ChatSvc-->>UI: response_text
    
    Note over UI: history.append(user_msg)<br/>history.append(assistant_msg)
    
    UI-->>User: Muestra respuesta en chat
    