"""Execution context for policies in query language interpreters."""

from typing import Any, Dict, List, Optional, Set, Union
from collections.abc import Mapping


class PolicyContext(Mapping):
    """Context for policy evaluation."""

    def __init__(self, data: Dict[str, Any] = None):
        """Initialize a policy context.

        Args:
            data: Initial context data
        """
        self._data = data or {}

    def __getitem__(self, key: str) -> Any:
        """Get a context value.

        Args:
            key: Context key

        Returns:
            Any: Context value

        Raises:
            KeyError: If key not found
        """
        return self._data[key]

    def __iter__(self):
        """Iterate over context keys.

        Returns:
            Iterator: Key iterator
        """
        return iter(self._data)

    def __len__(self) -> int:
        """Get the number of context items.

        Returns:
            int: Number of items
        """
        return len(self._data)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a context value with default.

        Args:
            key: Context key
            default: Default value if key not found

        Returns:
            Any: Context value or default
        """
        return self._data.get(key, default)

    def update(self, data: Dict[str, Any]) -> None:
        """Update the context with new data.

        Args:
            data: Data to update with
        """
        self._data.update(data)

    def contains_all(self, keys: List[str]) -> bool:
        """Check if the context contains all the given keys.

        Args:
            keys: Keys to check

        Returns:
            bool: True if all keys present, False otherwise
        """
        return all(key in self._data for key in keys)

    def contains_any(self, keys: List[str]) -> bool:
        """Check if the context contains any of the given keys.

        Args:
            keys: Keys to check

        Returns:
            bool: True if any key present, False otherwise
        """
        return any(key in self._data for key in keys)

    def has_permission(self, permission: str) -> bool:
        """Check if the context has a specific permission.

        Args:
            permission: Permission to check

        Returns:
            bool: True if permission present, False otherwise
        """
        permissions = self.get("permissions", [])
        return permission in permissions

    def has_role(self, role: str) -> bool:
        """Check if the context has a specific role.

        Args:
            role: Role to check

        Returns:
            bool: True if role present, False otherwise
        """
        roles = self.get("roles", [])
        return role in roles

    def has_purpose(self, purpose: str) -> bool:
        """Check if the context has a specific purpose.

        Args:
            purpose: Purpose to check

        Returns:
            bool: True if purpose matches, False otherwise
        """
        return self.get("purpose") == purpose
