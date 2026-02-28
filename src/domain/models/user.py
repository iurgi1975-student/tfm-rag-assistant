"""User domain model with role-based access control."""
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class UserRole(Enum):
    """User roles for access control."""
    ADMIN = "admin"  # Full access to all features
    USER = "user"    # Limited access - only chat functionality


@dataclass
class User:
    """
    User entity representing an authenticated user.
    
    Following DDD principles, this is a domain entity that encapsulates
    user information and role-based access rules.
    """
    username: str
    password_hash: str  # In simple implementation, stores plain password
    role: UserRole
    display_name: Optional[str] = None
    
    def __post_init__(self):
        """Validate user data."""
        if not self.username or not self.username.strip():
            raise ValueError("Username cannot be empty")
        if not self.password_hash or not self.password_hash.strip():
            raise ValueError("Password hash cannot be empty")
        if self.display_name is None:
            self.display_name = self.username.capitalize()
    
    def has_admin_access(self) -> bool:
        """Check if user has administrative privileges."""
        return self.role == UserRole.ADMIN
    
    def can_upload_documents(self) -> bool:
        """Check if user can upload and process documents."""
        return self.role == UserRole.ADMIN
    
    def can_manage_knowledge_base(self) -> bool:
        """Check if user can manage the knowledge base."""
        return self.role == UserRole.ADMIN
    
    def can_chat(self) -> bool:
        """Check if user can use chat functionality."""
        return True  # All authenticated users can chat
    
    def __str__(self) -> str:
        return f"User(username={self.username}, role={self.role.value})"
    
    def __repr__(self) -> str:
        return self.__str__()
