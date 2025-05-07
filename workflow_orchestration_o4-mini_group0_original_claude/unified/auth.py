"""
Authentication and authorization for the unified workflow orchestration system.
"""
import os
import secrets
import time
import base64
import hmac
import hashlib
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Set, Union

from unified.logger import default_logger

# In-memory token store
USER_TOKENS: Dict[str, str] = {
    "admin": "admin_secret_token_123",
    "data_engineer": "data_engineer_token_456",
    "data_scientist": "data_scientist_token_789",
    "product_manager": "product_manager_token_abc"
}

# Role-based permissions
USER_ROLES: Dict[str, List[str]] = {
    "admin": ["admin", "read", "write", "execute"],
    "data_engineer": ["read", "write", "execute"],
    "data_scientist": ["read", "write", "execute"],
    "product_manager": ["read", "execute"]
}


def authenticate_token(token: str) -> Optional[str]:
    """
    Authenticate a token and return the associated username.
    
    :param token: API token
    :return: Username if token is valid, None otherwise
    """
    for username, user_token in USER_TOKENS.items():
        if token == user_token:
            return username
    return None


def get_user_permissions(username: str) -> List[str]:
    """
    Get permissions for a user.
    
    :param username: Username
    :return: List of permission strings
    """
    return USER_ROLES.get(username, [])


def has_permission(username: str, required_permission: str) -> bool:
    """
    Check if a user has a specific permission.
    
    :param username: Username
    :param required_permission: Required permission
    :return: True if user has permission, False otherwise
    """
    if username == "admin":
        return True  # Admin has all permissions
    
    permissions = get_user_permissions(username)
    return required_permission in permissions


def generate_token() -> str:
    """
    Generate a secure random token.
    
    :return: Random token string
    """
    return secrets.token_hex(16)


def authenticate(token: str):
    """
    Authentication decorator for API functions.
    
    :param token: Expected token
    :return: Decorator function
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if token not in USER_TOKENS.values():
                raise PermissionError("Invalid authentication token")
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_permission(permission: str):
    """
    Permission decorator for API functions.
    
    :param permission: Required permission
    :return: Decorator function
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract token from kwargs or request
            token = kwargs.get("token")
            if not token:
                raise ValueError("Authentication token required")
                
            username = authenticate_token(token)
            if not username:
                raise PermissionError("Invalid authentication token")
                
            if not has_permission(username, permission):
                raise PermissionError(f"User {username} does not have {permission} permission")
                
            return func(*args, **kwargs)
        return wrapper
    return decorator


def create_user(username: str, password: str, roles: List[str]) -> str:
    """
    Create a new user with specified roles.
    
    :param username: Username
    :param password: Password (not stored)
    :param roles: List of roles
    :return: Generated token
    """
    if username in USER_TOKENS:
        raise ValueError(f"User {username} already exists")
        
    # Generate token
    token = generate_token()
    USER_TOKENS[username] = token
    
    # Assign roles
    all_permissions = set()
    for role in roles:
        if role in USER_ROLES:
            all_permissions.update(USER_ROLES[role])
    
    USER_ROLES[username] = list(all_permissions)
    
    default_logger.info(f"Created user {username} with roles {roles}")
    return token


def delete_user(username: str) -> bool:
    """
    Delete a user.
    
    :param username: Username
    :return: True if user was deleted, False otherwise
    """
    if username not in USER_TOKENS:
        return False
        
    del USER_TOKENS[username]
    if username in USER_ROLES:
        del USER_ROLES[username]
    
    default_logger.info(f"Deleted user {username}")
    return True