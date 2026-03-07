"""GoogleGeminiLLM - Google Gemini implementation of LLMRepository."""

from typing import List, Generator
from pathlib import Path
import google.generativeai as genai
from PIL import Image

from ...domain.repositories.llm_repository import LLMRepository
from ...domain.models import ChatMessage, MessageRole


class GoogleGeminiLLM(LLMRepository):
    """Google Gemini LLM implementation.
    
    Wraps Google's Generative AI SDK to provide a clean interface.
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.5-flash",
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
            # Extract system prompt if present
            system_instruction = None
            chat_messages = []
            
            for message in messages:
                if message.role == MessageRole.SYSTEM:
                    system_instruction = message.content
                else:
                    chat_messages.append(message)
            
            # Create model with system instruction if available
            model = self._model
            if system_instruction:
                model = genai.GenerativeModel(
                    self._model_name,
                    system_instruction=system_instruction
                )
            
            # Convert chat history to Gemini format
            history = []
            for i, msg in enumerate(chat_messages[:-1]):
                if msg.role == MessageRole.USER:
                    history.append({"role": "user", "parts": [msg.content]})
                elif msg.role == MessageRole.ASSISTANT:
                    history.append({"role": "model", "parts": [msg.content]})
            
            # Start chat with history
            chat = model.start_chat(history=history)
            
            # Send last message and get response
            last_message = chat_messages[-1]
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
            # Extract system prompt if present
            system_instruction = None
            chat_messages = []
            
            for message in messages:
                if message.role == MessageRole.SYSTEM:
                    system_instruction = message.content
                else:
                    chat_messages.append(message)
            
            # Create model with system instruction if available
            model = self._model
            if system_instruction:
                model = genai.GenerativeModel(
                    self._model_name,
                    system_instruction=system_instruction
                )
            
            # Convert chat history to Gemini format
            history = []
            for i, msg in enumerate(chat_messages[:-1]):
                if msg.role == MessageRole.USER:
                    history.append({"role": "user", "parts": [msg.content]})
                elif msg.role == MessageRole.ASSISTANT:
                    history.append({"role": "model", "parts": [msg.content]})
            
            # Start chat with history
            chat = model.start_chat(history=history)
            
            # Send last message and stream response
            last_message = chat_messages[-1]
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

    def supports_vision(self) -> bool:
        """Return True for Gemini models that support image input."""
        vision_models = ("gemini-2.0", "gemini-2.5", "gemini-1.5")
        return any(self._model_name.startswith(m) for m in vision_models)

    def invoke_with_images(self, messages: List[ChatMessage], images: List[str]) -> str:
        """Generate a response using both text messages and images.

        Args:
            messages: List of ChatMessage from domain.
            images: List of image file paths (max 4).

        Returns:
            Generated response text.
        """
        try:
            # Extract the last user message as the prompt
            prompt = next(
                (m.content for m in reversed(messages) if m.role == MessageRole.USER),
                ""
            )

            # Load images with PIL (max 4)
            pil_images = []
            for path in images[:4]:
                if Path(path).exists():
                    pil_images.append(Image.open(path).convert("RGB"))

            system_instruction = next(
                (m.content for m in messages if m.role == MessageRole.SYSTEM),
                None
            )
            model = genai.GenerativeModel(
                self._model_name,
                system_instruction=system_instruction
            ) if system_instruction else self._model

            content = [prompt] + pil_images
            response = model.generate_content(
                content,
                generation_config=genai.types.GenerationConfig(
                    temperature=self._temperature,
                    max_output_tokens=self._max_tokens,
                )
            )
            return response.text

        except Exception as e:
            error_msg = f"Error generating vision response from Gemini: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg
