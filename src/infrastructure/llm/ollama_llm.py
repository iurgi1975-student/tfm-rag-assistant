"""OllamaLLM - Ollama implementation of LLMRepository."""

from typing import List, Generator
import base64
from pathlib import Path
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from ...domain.repositories.llm_repository import LLMRepository
from ...domain.models import ChatMessage, MessageRole

# Ollama models known to support vision (image input)
_VISION_MODELS = ("llava", "bakllava", "moondream", "llava-phi3", "minicpm-v")


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

    def supports_vision(self) -> bool:
        """Return True if the loaded Ollama model supports image input."""
        return any(self._model_name.startswith(m) for m in _VISION_MODELS)

    def invoke_with_images(self, messages: List[ChatMessage], images: List[str]) -> str:
        """Generate a response using text messages and images.

        Sends images as base64-encoded content inside a HumanMessage,
        which is the format langchain_ollama expects for vision models.

        Args:
            messages: List of ChatMessage from domain.
            images: List of image file paths (max 4).

        Returns:
            Generated response text.
        """
        try:
            prompt = next(
                (m.content for m in reversed(messages) if m.role == MessageRole.USER),
                ""
            )

            # Build multimodal content list: text + base64 images
            content: list = [{"type": "text", "text": prompt}]
            for path in images[:4]:
                if Path(path).exists():
                    with open(path, "rb") as f:
                        b64 = base64.b64encode(f.read()).decode("utf-8")
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{b64}"},
                    })

            # Rebuild history (excluding the last user message)
            langchain_messages = []
            for msg in messages[:-1]:
                if msg.role == MessageRole.SYSTEM:
                    langchain_messages.append(SystemMessage(content=msg.content))
                elif msg.role == MessageRole.USER:
                    langchain_messages.append(HumanMessage(content=msg.content))
                elif msg.role == MessageRole.ASSISTANT:
                    langchain_messages.append(AIMessage(content=msg.content))

            langchain_messages.append(HumanMessage(content=content))

            response = self._llm.invoke(langchain_messages)
            return str(response.content) if response.content else ""

        except Exception as e:
            error_msg = f"Error generating vision response from Ollama: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg
    
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
