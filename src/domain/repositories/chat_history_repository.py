"""Chat History Repository Interface.

Interface for persisting chat conversation history.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from ..models import ChatMessage


class ChatHistoryRepository(ABC):
    """Abstract repository for chat history persistence."""
    
    @abstractmethod
    def save_message(self, session_id: str, message: ChatMessage) -> None:
        """Save a single message to persistent storage.
        
        Args:
            session_id: Unique identifier for the chat session.
            message: ChatMessage to persist.
        """
        pass
    
    @abstractmethod
    def get_history(
        self, 
        session_id: str, 
        limit: Optional[int] = None
    ) -> List[ChatMessage]:
        """Retrieve conversation history for a session.
        
        Args:
            session_id: Session identifier.
            limit: Maximum number of messages to retrieve (most recent).
            
        Returns:
            List of ChatMessage objects in chronological order.
        """
        pass
    
    @abstractmethod
    def clear_history(self, session_id: str) -> None:
        """Clear all messages for a session.
        
        Args:
            session_id: Session identifier to clear.
        """
        pass
    
    @abstractmethod
    def delete_session(self, session_id: str) -> None:
        """Permanently delete a session and all its messages.
        
        Args:
            session_id: Session identifier to delete.
        """
        pass
    
    @abstractmethod
    def list_sessions(self) -> List[str]:
        """List all available session IDs.
        
        Returns:
            List of session identifiers.
        """
        pass
