import functools
from .auth import AuthError
from utils import execute_task  # though unused here, we keep utils import style

class AuthManager:
    """Simple token‐based authentication manager."""
    def __init__(self):
        self._valid_tokens = set()

    def register_token(self, token: str):
        self._valid_tokens.add(token)

    def authenticate(self, token: str) -> bool:
        if token in self._valid_tokens:
            return True
        raise AuthError('Invalid token')

def requires_auth(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        token = kwargs.pop('token', None)
        if not token or not hasattr(self, '_auth_manager'):
            raise AuthError('Authentication required')
        self._auth_manager.authenticate(token)
        return func(self, *args, **kwargs)
    return wrapper
