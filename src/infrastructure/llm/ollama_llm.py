"""OllamaLLM - Ollama implementation of LLMRepository."""

from typing import List, Generator
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from ...domain.repositories.llm_repository import LLMRepository
from ...domain.models import ChatMessage, MessageRole


class OllamaLLM(LLMRepository):
    """Ollama LLM implementation.
    
    Wraps ChatOllama from langchain_ollama to provide a clean interface.
    """
    
    def __init__(
        self,
        model: str = "llama3.2:3b",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.7,
        max_tokens: int = 4000
    ):
        """Initialize Ollama LLM.
        
        Args:
            model: Model name (e.g., "llama3.2:3b").
            base_url: Ollama server URL.
            temperature: Sampling temperature (0.0 to 2.0).
            max_tokens: Maximum tokens in response.
        """
        self._model_name = model
        self._llm = ChatOllama(
            base_url=base_url,
            api_key="dummy",  # Not needed for local Ollama
            model=model,
            temperature=temperature,
            num_predict=max_tokens
        )
    
    def invoke(self, messages: List[ChatMessage]) -> str:
        """Generate a response for the given messages.
        
        Args:
            messages: List of ChatMessage from domain.
            
        Returns:
            Generated response text.
        """
        # Convert domain ChatMessage to LangChain messages
        langchain_messages = self._convert_to_langchain(messages)
        response = self._llm.invoke(langchain_messages)
        return str(response.content) if response.content else ""
    
    def stream(self, messages: List[ChatMessage]) -> Generator[str, None, None]:
        """Stream a response for the given messages.
        
        Args:
            messages: List of ChatMessage from domain.
            
        Yields:
            Chunks of the generated response.
        """
        # Convert domain ChatMessage to LangChain messages
        langchain_messages = self._convert_to_langchain(messages)
        for chunk in self._llm.stream(langchain_messages):
            content = str(chunk.content) if chunk.content else ""
            if content:
                yield content
    
    def get_model_name(self) -> str:
        """Get the name of the model being used.
        
        Returns:
            Model name string.
        """
        return self._model_name
    
    def _convert_to_langchain(self, messages: List[ChatMessage]) -> List:
        """Convert domain ChatMessage to LangChain messages.
        
        Args:
            messages: List of domain ChatMessage.
            
        Returns:
            List of LangChain message objects.
        """
        langchain_messages = []
        for msg in messages:
            if msg.role == MessageRole.USER:
                langchain_messages.append(HumanMessage(content=msg.content))
            elif msg.role == MessageRole.ASSISTANT:
                langchain_messages.append(AIMessage(content=msg.content))
            elif msg.role == MessageRole.SYSTEM:
                langchain_messages.append(SystemMessage(content=msg.content))
        return langchain_messages
