"""
Simple token-based authentication and authorization.
"""
from functools import wraps
from typing import Callable, Dict

# In-memory user->token store for demo
USER_TOKENS: Dict[str, str] = {
    "admin": "secrettoken123"
}

def authenticate(token: str):
    """
    Decorator to authenticate API calls.
    """
    def decorator(fn: Callable):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if token not in USER_TOKENS.values():
                raise PermissionError("Invalid authentication token")
            return fn(*args, **kwargs)
        return wrapper
    return decorator