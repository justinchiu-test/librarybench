"""Base data models for query language interpreters."""

from typing import Any, Dict, List, Optional, Set, Union
from abc import ABC, abstractmethod


class BaseModel(ABC):
    """Base class for data models."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation
        """
        return self.__dict__

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """Create model from dictionary.

        Args:
            data: Dictionary data

        Returns:
            BaseModel: Model instance
        """
        return cls(**data)


class Document(BaseModel):
    """Represents a document in the system."""

    def __init__(
        self,
        id: str,
        content: str,
        metadata: Dict[str, Any] = None,
    ):
        """Initialize a document.

        Args:
            id: Document ID
            content: Document content
            metadata: Document metadata
        """
        self.id = id
        self._content = content
        self.metadata = metadata or {}

    def __str__(self) -> str:
        """String representation of the document.

        Returns:
            str: String representation
        """
        return f"Document(id={self.id}, metadata={self.metadata})"
        
    def get_content(self) -> str:
        """Get the document content.
        
        Returns:
            str: Document content
        """
        return self._content
        
    @property
    def content(self) -> str:
        """Property to access document content.
        
        Returns:
            str: Document content
        """
        return self._content


class DataField(BaseModel):
    """Represents a data field in the system."""

    def __init__(
        self,
        name: str,
        field_type: str,
        description: str = "",
        sensitive: bool = False,
        required: bool = False,
        metadata: Dict[str, Any] = None,
    ):
        """Initialize a data field.

        Args:
            name: Field name
            field_type: Field type
            description: Field description
            sensitive: Whether the field contains sensitive data
            required: Whether the field is required
            metadata: Field metadata
        """
        self.name = name
        self.field_type = field_type
        self.description = description
        self.sensitive = sensitive
        self.required = required
        self.metadata = metadata or {}

    def __str__(self) -> str:
        """String representation of the field.

        Returns:
            str: String representation
        """
        return f"DataField(name={self.name}, type={self.field_type}, sensitive={self.sensitive})"


class Category(BaseModel):
    """Represents a category in the system."""

    def __init__(
        self,
        id: str,
        name: str,
        description: str = "",
        parent_id: Optional[str] = None,
        metadata: Dict[str, Any] = None,
    ):
        """Initialize a category.

        Args:
            id: Category ID
            name: Category name
            description: Category description
            parent_id: Parent category ID
            metadata: Category metadata
        """
        self.id = id
        self.name = name
        self.description = description
        self.parent_id = parent_id
        self.metadata = metadata or {}

    def __str__(self) -> str:
        """String representation of the category.

        Returns:
            str: String representation
        """
        return f"Category(id={self.id}, name={self.name})"