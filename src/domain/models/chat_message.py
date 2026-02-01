"""ChatMessage model.

Represents a message in a conversation.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class MessageRole(Enum):
    """Role of the message sender."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class ChatMessage:
    """A message in a conversation.
    
    Attributes:
        role: Who sent the message (user, assistant, system)
        content: The message text
        timestamp: When the message was created
        metadata: Additional metadata about the message
    """
    role: MessageRole
    content: str
    timestamp: Optional[datetime] = None
    metadata: Optional[dict] = None
    
    def __post_init__(self):
        """Validate message after initialization."""
        if not self.content or not self.content.strip():
            raise ValueError("Message content cannot be empty")
        
        if self.timestamp is None:
            self.timestamp = datetime.now()
        
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> dict:
        """Convert message to dictionary format.
        
        Returns:
            Dictionary representation of the message.
        """
        return {
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ChatMessage":
        """Create message from dictionary.
        
        Args:
            data: Dictionary with message data.
            
        Returns:
            ChatMessage instance.
        """
        return cls(
            role=MessageRole(data["role"]),
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else None,
            metadata=data.get("metadata", {})
        )
    
    def is_from_user(self) -> bool:
        """Check if message is from user."""
        return self.role == MessageRole.USER
    
    def is_from_assistant(self) -> bool:
        """Check if message is from assistant."""
        return self.role == MessageRole.ASSISTANT
    
    def is_system(self) -> bool:
        """Check if message is a system message."""
        return self.role == MessageRole.SYSTEM
