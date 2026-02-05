"""GoogleGeminiLLM - Google Gemini implementation of LLMRepository."""

from typing import List, Generator
import google.generativeai as genai

from ...domain.repositories.llm_repository import LLMRepository
from ...domain.models import ChatMessage, MessageRole


class GoogleGeminiLLM(LLMRepository):
    """Google Gemini LLM implementation.
    
    Wraps Google's Generative AI SDK to provide a clean interface.
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash-lite",
        temperature: float = 0.7,
        max_tokens: int = 4000
    ):
        """Initialize Google Gemini LLM.
        
        Args:
            api_key: Google AI Studio API key.
            model: Model name (e.g., "gemini-2.5-flash", "gemini-2.5-pro").
            temperature: Sampling temperature (0.0 to 2.0).
            max_tokens: Maximum tokens in response.
        """
        self._model_name = model
        self._temperature = temperature
        self._max_tokens = max_tokens
        
        # Configure API
        genai.configure(api_key=api_key)
        
        # Initialize model
        self._model = genai.GenerativeModel(model)
    
    def invoke(self, messages: List[ChatMessage]) -> str:
        """Generate a response for the given messages.
        
        Args:
            messages: List of ChatMessage from domain.
            
        Returns:
            Generated response text.
        """
        try:
            # Convert domain messages to Gemini chat format
            chat = self._model.start_chat(history=[])
            
            # Process all messages except the last one
            for message in messages[:-1]:
                if message.role == MessageRole.USER:
                    chat.send_message(message.content)
                elif message.role == MessageRole.ASSISTANT:
                    # For assistant messages, we need to add them to history
                    # Gemini handles this automatically in chat mode
                    pass
            
            # Send last message and get response
            last_message = messages[-1]
            response = chat.send_message(
                last_message.content,
                generation_config=genai.types.GenerationConfig(
                    temperature=self._temperature,
                    max_output_tokens=self._max_tokens,
                )
            )
            
            return response.text
            
        except Exception as e:
            error_msg = f"Error generating response from Gemini: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg
    
    def stream(self, messages: List[ChatMessage]) -> Generator[str, None, None]:
        """Stream a response for the given messages.
        
        Args:
            messages: List of ChatMessage from domain.
            
        Yields:
            Chunks of the generated response.
        """
        try:
            # Convert domain messages to Gemini chat format
            chat = self._model.start_chat(history=[])
            
            # Process all messages except the last one
            for message in messages[:-1]:
                if message.role == MessageRole.USER:
                    chat.send_message(message.content)
            
            # Send last message and stream response
            last_message = messages[-1]
            response = chat.send_message(
                last_message.content,
                generation_config=genai.types.GenerationConfig(
                    temperature=self._temperature,
                    max_output_tokens=self._max_tokens,
                ),
                stream=True
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            error_msg = f"Error streaming response from Gemini: {str(e)}"
            print(f"❌ {error_msg}")
            yield error_msg
    
    def get_model_name(self) -> str:
        """Get the name of the model being used.
        
        Returns:
            Model name string.
        """
        return self._model_name
