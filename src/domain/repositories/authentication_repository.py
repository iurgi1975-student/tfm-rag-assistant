"""Authentication repository interface."""
from abc import ABC, abstractmethod
from typing import Optional
from ..models.user import User


class AuthenticationRepository(ABC):
    """
    Repository interface for user authentication.
    
    Following hexagonal architecture, this defines the port
    that infrastructure adapters must implement.
    """
    
    @abstractmethod
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user with username and password.
        
        Args:
            username: The username to authenticate
            password: The plain text password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        pass
    
    @abstractmethod
    def get_user(self, username: str) -> Optional[User]:
        """
        Retrieve user by username.
        
        Args:
            username: The username to look up
            
        Returns:
            User object if found, None otherwise
        """
        pass
    
    @abstractmethod
    def user_exists(self, username: str) -> bool:
        """
        Check if a user exists.
        
        Args:
            username: The username to check
            
        Returns:
            True if user exists, False otherwise
        """
        pass
