"""
Chat Service - Orchestrates conversational AI operations.
"""
from typing import List, Union, Generator, Optional
from datetime import datetime

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, trim_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from .rag_service import RAGService


class ChatService:
    """Service for managing chat conversations with LLM."""
    
    def __init__(
        self,
        llm: ChatOllama,
        rag_service: RAGService,
        memory_window: int = 10,
        system_prompt_template: Optional[str] = None
    ):
        """Initialize the chat service.
        
        Args:
            llm: Language model instance.
            rag_service: Service for retrieving relevant context.
            memory_window: Number of recent messages to keep in history.
            system_prompt_template: Custom system prompt template.
        """
        self._llm = llm
        self._rag_service = rag_service
        self._memory_window = memory_window
        self._system_prompt_template = system_prompt_template or self._get_default_system_prompt()
        
        # Conversation history
        self._chat_history: List[Union[HumanMessage, AIMessage]] = []
    
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
        # Get context from RAG if enabled
        context = ""
        if use_rag:
            context = self._rag_service.get_context(message)
        
        # Create system prompt with context
        system_prompt = self._create_system_prompt(context)
        
        # Get trimmed chat history
        chat_history = self._get_trimmed_history()
        
        # Create prompt and chain
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
        
        chain = prompt | self._llm
        
        # Get response
        if stream:
            return self._handle_streaming(message, chain, chat_history)
        else:
            return self._handle_non_streaming(message, chain, chat_history)
    
    def clear_history(self) -> None:
        """Clear conversation history."""
        self._chat_history.clear()
    
    def get_history(self) -> List[Union[HumanMessage, AIMessage]]:
        """Get current conversation history.
        
        Returns:
            List of messages in history.
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
    
    def _get_trimmed_history(self) -> List[Union[HumanMessage, AIMessage]]:
        """Trim history to memory window."""
        return trim_messages(
            self._chat_history,
            token_counter=len,
            max_tokens=self._memory_window,
            strategy="last",
            start_on="human",
            include_system=False,
            allow_partial=False
        )
    
    def _handle_non_streaming(
        self, 
        message: str, 
        chain, 
        chat_history: List
    ) -> str:
        """Handle non-streaming response."""
        # Invoke chain
        response = chain.invoke({
            "input": message,
            "chat_history": chat_history
        })
        
        # Extract response text
        response_text = response.content
        
        # Update history
        self._chat_history.append(HumanMessage(content=message))
        self._chat_history.append(AIMessage(content=response_text))
        
        return response_text
    
    def _handle_streaming(
        self, 
        message: str, 
        chain, 
        chat_history: List
    ) -> Generator:
        """Handle streaming response."""
        def generate():
            full_response = ""
            
            for chunk in chain.stream({
                "input": message,
                "chat_history": chat_history
            }):
                if hasattr(chunk, 'content'):
                    chunk_text = chunk.content
                    full_response += chunk_text
                    yield chunk_text
            
            # Update history after streaming completes
            self._chat_history.append(HumanMessage(content=message))
            self._chat_history.append(AIMessage(content=full_response))
        
        return generate()
