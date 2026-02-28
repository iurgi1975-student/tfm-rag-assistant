"""Authentication service for user authentication and authorization."""
from typing import Optional, Tuple
from ...domain.repositories.authentication_repository import AuthenticationRepository
from ...domain.models.user import User


class AuthenticationService:
    """
    Application service handling user authentication and authorization logic.
    
    Following hexagonal architecture, this service orchestrates domain logic
    and delegates data access to repositories.
    """
    
    def __init__(self, auth_repository: AuthenticationRepository):
        """
        Initialize authentication service.
        
        Args:
            auth_repository: Repository for user authentication
        """
        self.auth_repository = auth_repository
    
    def login(self, username: str, password: str) -> Tuple[bool, Optional[User], str]:
        """
        Authenticate user and return login status.
        
        Args:
            username: Username to authenticate
            password: Password in plain text
            
        Returns:
            Tuple of (success: bool, user: Optional[User], message: str)
        """
        if not username or not username.strip():
            return False, None, "Username cannot be empty"
        
        if not password or not password.strip():
            return False, None, "Password cannot be empty"
        
        user = self.auth_repository.authenticate(username.strip(), password)
        
        if user is None:
            return False, None, "Invalid credentials"
        
        return True, user, f"Welcome, {user.display_name}!"
    
    def get_user(self, username: str) -> Optional[User]:
        """
        Retrieve user by username.
        
        Args:
            username: Username to retrieve
            
        Returns:
            User object if found, None otherwise
        """
        return self.auth_repository.get_user(username)
    
    def check_access(self, user: User, resource: str) -> bool:
        """
        Check if user has access to a specific resource.
        
        Args:
            user: The authenticated user
            resource: Resource identifier (e.g., 'upload', 'manage_kb')
            
        Returns:
            True if user has access, False otherwise
        """
        access_map = {
            'chat': user.can_chat(),
            'upload': user.can_upload_documents(),
            'manage_kb': user.can_manage_knowledge_base(),
            'admin': user.has_admin_access(),
        }
        
        return access_map.get(resource, False)
