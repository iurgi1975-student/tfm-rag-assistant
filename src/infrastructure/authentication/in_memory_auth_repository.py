"""In-memory authentication repository implementation."""
from typing import Optional, Dict
from ...domain.repositories.authentication_repository import AuthenticationRepository
from ...domain.models.user import User, UserRole


class InMemoryAuthRepository(AuthenticationRepository):
    """
    In-memory implementation of authentication repository.
    
    This adapter stores users in memory and is suitable for:
    - Development and testing
    - Simple applications with few users
    - Demo and educational purposes
    
    For production with many users, consider implementing a database adapter.
    """
    
    def __init__(self, users: Optional[Dict[str, User]] = None):
        """
        Initialize repository with user dictionary.
        
        Args:
            users: Dictionary mapping username to User objects.
                   If None, creates empty repository.
        """
        self._users: Dict[str, User] = users or {}
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username and password.
        
        Args:
            username: The username to authenticate
            password: The plain text password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        user = self._users.get(username)
        
        if user is None:
            return None
        
        # In this simple implementation, password_hash is the plain password
        # In production, use proper password hashing (bcrypt, argon2, etc.)
        if user.password_hash == password:
            return user
        
        return None
    
    def get_user(self, username: str) -> Optional[User]:
        """
        Retrieve user by username.
        
        Args:
            username: The username to look up
            
        Returns:
            User object if found, None otherwise
        """
        return self._users.get(username)
    
    def user_exists(self, username: str) -> bool:
        """
        Check if a user exists.
        
        Args:
            username: The username to check
            
        Returns:
            True if user exists, False otherwise
        """
        return username in self._users
    
    def add_user(self, user: User) -> None:
        """
        Add a user to the repository.
        
        Args:
            user: User object to add
        """
        self._users[user.username] = user
    
    @classmethod
    def from_env_config(cls, auth_config: str) -> 'InMemoryAuthRepository':
        """
        Create repository from environment variable configuration.
        
        Expected format: "username1:password1:role1,username2:password2:role2"
        Example: "admin:admin123:admin,user:user123:user"
        
        If role is not specified (format: "username:password"), defaults to USER role.
        
        Args:
            auth_config: Configuration string
            
        Returns:
            InMemoryAuthRepository instance with configured users
        """
        repository = cls()
        
        if not auth_config or not auth_config.strip():
            # Create default user if no config provided (as per user decision)
            repository.add_user(User(
                username="admin",
                password_hash="admin123",
                role=UserRole.ADMIN,
                display_name="Administrator"
            ))
            return repository
        
        # Parse configuration
        user_configs = auth_config.split(',')
        
        for user_config in user_configs:
            parts = user_config.strip().split(':')
            
            if len(parts) < 2:
                continue  # Skip invalid entries
            
            username = parts[0].strip()
            password = parts[1].strip()
            
            # Default role is USER (as per user decision for security)
            role = UserRole.USER
            if len(parts) >= 3:
                role_str = parts[2].strip().lower()
                if role_str == 'admin':
                    role = UserRole.ADMIN
                # Any other value defaults to USER
            
            user = User(
                username=username,
                password_hash=password,  # Plain text in this simple implementation
                role=role,
                display_name=username.capitalize()
            )
            
            repository.add_user(user)
        
        return repository
