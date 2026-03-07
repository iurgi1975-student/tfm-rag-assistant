"""LLMRepository - Abstract interface for Language Models.

Defines the contract for any LLM implementation (Ollama, OpenAI, Anthropic, etc.).
"""

from abc import ABC, abstractmethod
from typing import List, Union, Generator, TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import ChatMessage


class LLMRepository(ABC):
    """Abstract interface for Language Model repositories.
    
    Any LLM provider (Ollama, OpenAI, Anthropic) must implement these methods.
    This ensures loose coupling and allows easy swapping of LLM implementations.
    """
    
    @abstractmethod
    def invoke(self, messages: List['ChatMessage']) -> str:
        """Generate a response for the given messages.
        
        Args:
            messages: List of ChatMessage from domain.
            
        Returns:
            Generated response text.
        """
        pass
    
    @abstractmethod
    def stream(self, messages: List['ChatMessage']) -> Generator[str, None, None]:
        """Stream a response for the given messages.
        
        Args:
            messages: List of ChatMessage from domain.
            
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

    def supports_vision(self) -> bool:
        """Return True if this LLM can process images.

        Defaults to False. Override in vision-capable implementations.
        """
        return False

    def invoke_with_images(self, messages: List['ChatMessage'], images: List[str]) -> str:
        """Generate a response using both text messages and images.

        Args:
            messages: List of ChatMessage from domain.
            images: List of image file paths to include in the prompt.

        Returns:
            Generated response text.

        Raises:
            NotImplementedError: If the implementation does not support vision.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support vision. "
            "Override invoke_with_images() and return True from supports_vision()."
        )
