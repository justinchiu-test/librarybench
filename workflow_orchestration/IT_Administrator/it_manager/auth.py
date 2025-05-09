import functools
from typing import Dict, Set


class AuthenticationError(Exception):
    pass


class AuthorizationError(Exception):
    pass


class AuthManager:
    """
    Simple in-memory authentication and authorization manager.
    """
    _users: Dict[str, str] = {}      # username -> password
    _roles: Dict[str, Set[str]] = {} # username -> roles
    _permissions: Dict[str, Set[str]] = {} # role -> permissions

    @classmethod
    def add_user(cls, username: str, password: str):
        cls._users[username] = password
        cls._roles[username] = set()

    @classmethod
    def assign_role(cls, username: str, role: str):
        if username not in cls._users:
            raise AuthenticationError("User does not exist")
        cls._roles[username].add(role)

    @classmethod
    def add_permission(cls, role: str, permission: str):
        cls._permissions.setdefault(role, set()).add(permission)

    @classmethod
    def authenticate(cls, username: str, password: str):
        if cls._users.get(username) != password:
            raise AuthenticationError("Invalid credentials")
        return True

    @classmethod
    def authorize(cls, username: str, permission: str):
        roles = cls._roles.get(username, set())
        for role in roles:
            if permission in cls._permissions.get(role, set()):
                return True
        raise AuthorizationError(f"User '{username}' lacks permission '{permission}'")

    @classmethod
    def requires_permission(cls, permission: str):
        """
        Decorator to enforce authorization on functions that require certain permission.
        Expects 'username' in kwargs.
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                username = kwargs.get("username")
                if not username:
                    raise AuthorizationError("No username provided")
                cls.authorize(username, permission)
                return func(*args, **kwargs)
            return wrapper
        return decorator
