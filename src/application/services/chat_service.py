"""
Chat Service - Orchestrates conversational AI operations.
"""
from typing import List, Union, Generator, Optional
from datetime import datetime

from ...domain.repositories import LLMRepository, ChatHistoryRepository
from ...domain.models import ChatMessage, MessageRole
from .rag_service import RAGService


class ChatService:
    """Service for managing chat conversations with LLM."""
    
    def __init__(
        self,
        llm: LLMRepository,
        rag_service: RAGService,
        chat_repository: Optional[ChatHistoryRepository] = None,
        session_id: str = "default",
        memory_window: int = 10,
        system_prompt_template: Optional[str] = None
    ):
        """Initialize the chat service.
        
        Args:
            llm: Language model repository instance.
            rag_service: Service for retrieving relevant context.
            chat_repository: Optional repository for persisting chat history.
            session_id: Unique identifier for the chat session.
            memory_window: Number of recent messages to keep in history.
            system_prompt_template: Custom system prompt template.
        """
        self._llm = llm
        self._rag_service = rag_service
        self._chat_repository = chat_repository
        self._session_id = session_id
        self._memory_window = memory_window
        self._system_prompt_template = system_prompt_template or self._get_default_system_prompt()
        
        # Load conversation history from persistence if available
        if self._chat_repository:
            try:
                self._chat_history: List[ChatMessage] = self._chat_repository.get_history(
                    session_id, 
                    limit=memory_window
                )
                if self._chat_history:
                    print(f"📚 Loaded {len(self._chat_history)} previous messages from chat history")
                    print(f"💡 Keeping last {memory_window} messages in memory to manage context size")
            except Exception as e:
                print(f"⚠️ Could not load chat history: {e}")
                self._chat_history: List[ChatMessage] = []
        else:
            self._chat_history: List[ChatMessage] = []
    
    def chat(
        self, 
        message: str, 
        stream: bool = False,
        use_rag: bool = True
    ) -> Union[str, Generator]:
        """Process a chat message and return response.
        
        Args:
            message: User message.
            stream: Whether to stream the response.
            use_rag: Whether to use RAG for context retrieval.
            
        Returns:
            Response string or generator for streaming.
        """
        # Get context from RAG if enabled and available
        context = ""
        if use_rag and self._rag_service:
            context = self._rag_service.get_context(message)
        elif use_rag and not self._rag_service:
            print("Warning: use_rag=True but no RAG service is configured. Continuing without context.")
        
        # Create system prompt with context
        system_prompt = self._create_system_prompt(context)
        
        # Get trimmed chat history
        chat_history = self._get_trimmed_history()
        
        # Build messages for LLM using domain ChatMessage
        messages = [
            ChatMessage(role=MessageRole.SYSTEM, content=system_prompt)
        ]
        messages.extend(chat_history)
        messages.append(ChatMessage(role=MessageRole.USER, content=message))
        
        # Get response
        if stream:
            return self._handle_streaming(message, messages)
        else:
            return self._handle_non_streaming(message, messages)
    
    def clear_history(self) -> None:
        """Clear conversation history (memory + persistence)."""
        self._chat_history.clear()
        
        # Also clear from database if repository is available
        if self._chat_repository:
            self._chat_repository.clear_history(self._session_id)
    
    def get_history(self) -> List[ChatMessage]:
        """Get current conversation history.
        
        Returns:
            List of ChatMessage in history.
        """
        return self._chat_history.copy()
    
    def _create_system_prompt(self, context: str) -> str:
        """Create system prompt with context."""
        return self._system_prompt_template.format(
            context=context,
            current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def _get_default_system_prompt(self) -> str:
        """Get default system prompt template."""
        return """You are a helpful AI assistant with access to a knowledge base of documents.
You can answer questions using both your general knowledge and information from the provided documents.

When answering questions:
1. If relevant information is available in the provided context, prioritize it
2. Clearly indicate when you're using information from the documents vs. your general knowledge
3. Be concise but thorough in your responses
4. If you cannot find relevant information in the documents, say so and provide what help you can from your general knowledge
5. Always be helpful, accurate, and honest about the limitations of your knowledge

Context from documents:
{context}

Current time: {current_time}"""
    
    def _get_trimmed_history(self) -> List[ChatMessage]:
        """Trim history to memory window."""
        # Simple trimming: keep last N messages
        if len(self._chat_history) > self._memory_window:
            return self._chat_history[-self._memory_window:]
        return self._chat_history
    
    def _handle_non_streaming(
        self, 
        message: str, 
        messages: List[ChatMessage]
    ) -> str:
        """Handle non-streaming response."""
        # Invoke LLM
        response_text = self._llm.invoke(messages)
        
        # Create message objects
        user_message = ChatMessage(role=MessageRole.USER, content=message)
        assistant_message = ChatMessage(role=MessageRole.ASSISTANT, content=response_text)
        
        # Update in-memory history
        self._chat_history.append(user_message)
        self._chat_history.append(assistant_message)
        
        # Persist to database if repository is available
        if self._chat_repository:
            self._chat_repository.save_message(self._session_id, user_message)
            self._chat_repository.save_message(self._session_id, assistant_message)
        
        return response_text
    
    def _handle_streaming(
        self, 
        message: str, 
        messages: List[ChatMessage]
    ) -> Generator:
        """Handle streaming response."""
        def generate():
            full_response = ""
            
            for chunk_text in self._llm.stream(messages):
                full_response += chunk_text
                yield chunk_text
            
            # Create message objects after streaming completes
            user_message = ChatMessage(role=MessageRole.USER, content=message)
            assistant_message = ChatMessage(role=MessageRole.ASSISTANT, content=full_response)
            
            # Update in-memory history
            self._chat_history.append(user_message)
            self._chat_history.append(assistant_message)
            
            # Persist to database if repository is available
            if self._chat_repository:
                self._chat_repository.save_message(self._session_id, user_message)
                self._chat_repository.save_message(self._session_id, assistant_message)
        
        return generate()
