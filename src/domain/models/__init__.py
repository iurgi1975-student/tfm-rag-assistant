"""Domain models - Document, DocumentChunk, SearchResult, ChatMessage, and User.

Simple data classes representing core domain concepts without external dependencies.
"""

from .document import Document, DocumentChunk
from .search_result import SearchResult
from .chat_message import ChatMessage, MessageRole
from .user import User, UserRole

__all__ = ["Document", "DocumentChunk", "SearchResult", "ChatMessage", "MessageRole", "User", "UserRole"]
