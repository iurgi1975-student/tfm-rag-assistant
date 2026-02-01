"""LLMRepository - Abstract interface for Language Models.

Defines the contract for any LLM implementation (Ollama, OpenAI, Anthropic, etc.).
"""

from abc import ABC, abstractmethod
from typing import List, Union, Generator
from langchain_core.messages import BaseMessage


class LLMRepository(ABC):
    """Abstract interface for Language Model repositories.
    
    Any LLM provider (Ollama, OpenAI, Anthropic) must implement these methods.
    This ensures loose coupling and allows easy swapping of LLM implementations.
    """
    
    @abstractmethod
    def invoke(self, messages: List[BaseMessage]) -> str:
        """Generate a response for the given messages.
        
        Args:
            messages: List of conversation messages.
            
        Returns:
            Generated response text.
        """
        pass
    
    @abstractmethod
    def stream(self, messages: List[BaseMessage]) -> Generator[str, None, None]:
        """Stream a response for the given messages.
        
        Args:
            messages: List of conversation messages.
            
        Yields:
            Chunks of the generated response.
        """
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get the name of the model being used.
        
        Returns:
            Model name string.
        """
        pass
