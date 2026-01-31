´´´mermaid
graph TD
    A["🚀 python app.py<br/><br/>Inicio del programa"] --> B["<b>app.py:51</b><br/>def main()"]
    
    B --> C["<b>app.py:52-60</b><br/>Parsear argumentos CLI"]
    C --> D["<b>app.py:62</b><br/>load_environment<br/>Carga variables .env"]
    D --> E["<b>app.py:68-75</b><br/>create_agent<br/>Crea RAGAgent"]
    
    E --> E1["<b>src/agent/rag_agent.py:24-53</b><br/>RAGAgent.__init__<br/>Inicializa LLM Ollama"]
    E1 --> E2["<b>src/rag/vector_store.py:23-45</b><br/>ChromaVectorStore.__init__<br/>Crea cliente Chroma<br/>Carga DB persistente<br/><br/>⚠️ AQUÍ SALTA TU BREAKPOINT"]
    E2 --> E3["<b>src/rag/vector_store.py:52</b><br/>RAGRetriever.__init__"]
    E3 --> E4["<b>src/rag/document_processor.py:11-17</b><br/>DocumentProcessor.__init__"]
    
    E4 --> F["<b>app.py:77-80</b><br/>ChatInterface creada"]
    F --> F1["<b>src/interface/gradio_chat.py:15-18</b><br/>ChatInterface.__init__"]
    F1 --> F2["<b>src/interface/gradio_chat.py:169</b><br/>create_interface<br/>Crea UI Gradio"]
    
    F2 --> G["<b>app.py:89-91</b><br/>Mostrar tips y URL"]
    G --> H["<b>app.py:95</b><br/>chat_interface.launch<br/>Inicia servidor Gradio"]
    H --> I["🌐 <b>http://0.0.0.0:7860</b><br/>Servidor corriendo"]
    
    I --> J{Usuario interactúa}
    
    J -->|Sube archivos| K["<b>src/interface/gradio_chat.py:26</b><br/>process_uploaded_files"]
    K --> K1["<b>src/rag/document_processor.py:28-30</b><br/>DocumentProcessor.load_document"]
    K1 --> K2["<b>src/rag/document_processor.py:38</b><br/>PyPDFLoader + split_documents"]
    K2 --> K3["<b>src/rag/vector_store.py:65</b><br/>add_documents<br/>Embeddings + Chroma"]
    
    J -->|Envía mensaje| L["<b>src/interface/gradio_chat.py:80</b><br/>chat_response"]
    L --> L1["<b>src/agent/rag_agent.py:127</b><br/>agent.chat"]
    L1 --> L2["<b>src/agent/rag_agent.py:109</b><br/>_get_relevant_context<br/>Busca en vector store"]
    L2 --> L3["<b>src/rag/vector_store.py:189</b><br/>RAGRetriever.get_context"]
    L3 --> L4["<b>src/rag/vector_store.py:160</b><br/>similarity_search_with_score<br/>Búsqueda en Chroma"]
    
    L4 --> L5["<b>src/agent/rag_agent.py:137-150</b><br/>LLM genera respuesta<br/>con contexto"]
    L5 --> L6["<b>src/interface/gradio_chat.py:88-95</b><br/>Respuesta al usuario"]
    
    J -->|Busca documentos| M["<b>src/interface/gradio_chat.py:101</b><br/>search_documents"]
    M --> M1["<b>src/agent/rag_agent.py:203</b><br/>agent.search_documents<br/>similarity_search"]
    
    J -->|Manejo KB| N["<b>src/interface/gradio_chat.py:55-67</b><br/>clear_knowledge_base<br/>clear_chat_history"]
    N --> N1["<b>src/agent/rag_agent.py:98-102</b><br/>clear_knowledge_base<br/>clear_conversation_history"]
    
    style A fill:#90EE90
    style B fill:#FFE4B5
    style E2 fill:#FF6B6B
    style I fill:#87CEEB
    style J fill:#FFD700
    
    classDef module fill:#E6F3FF
    classDef file fill:#FFF0E6
    
    class E1,F1,K1,L1,L3,M1,N1 module
    class E2,K3,L4 file
  ´´´