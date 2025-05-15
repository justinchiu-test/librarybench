"""
Serialization utilities for the common library.

This module provides interfaces and utilities for serializing and deserializing
data in various formats, with a focus on JSON as the primary format.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic, Callable
import json
import base64
import datetime

T = TypeVar('T')

class Serializable(ABC):
    """
    Interface for objects that can be serialized and deserialized.
    
    Classes implementing this interface must provide methods to convert
    themselves to and from dictionaries and JSON strings.
    """
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the object to a dictionary representation.
        
        Returns:
            A dictionary containing the object's data.
        """
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Serializable':
        """
        Create an object from a dictionary representation.
        
        Args:
            data: Dictionary containing object data.
        
        Returns:
            A new instance of the implementing class.
        """
        pass
    
    def to_json(self) -> str:
        """
        Convert the object to a JSON string.
        
        Returns:
            JSON representation of the object.
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Serializable':
        """
        Create an object from a JSON string.
        
        Args:
            json_str: JSON string representing the object.
        
        Returns:
            A new instance of the implementing class.
        """
        data = json.loads(json_str)
        return cls.from_dict(data)


class SerializationRegistry:
    """
    Registry for serializable types.
    
    This class maintains a mapping of type names to serializable classes,
    allowing for dynamic serialization and deserialization of objects.
    """
    
    def __init__(self) -> None:
        """
        Initialize the serialization registry.
        """
        self._types: Dict[str, Type[Serializable]] = {}
    
    def register(self, type_name: str, cls: Type[Serializable]) -> None:
        """
        Register a serializable class with a type name.
        
        Args:
            type_name: The name to associate with the class.
            cls: The serializable class to register.
        """
        if not issubclass(cls, Serializable):
            raise ValueError(f"Class {cls.__name__} must implement Serializable")
        
        self._types[type_name] = cls
    
    def get_class(self, type_name: str) -> Optional[Type[Serializable]]:
        """
        Get the class associated with a type name.
        
        Args:
            type_name: The name of the type to retrieve.
        
        Returns:
            The associated class, or None if not found.
        """
        return self._types.get(type_name)
    
    def serialize(self, obj: Serializable) -> Dict[str, Any]:
        """
        Serialize an object with its type information.
        
        Args:
            obj: The object to serialize.
        
        Returns:
            A dictionary containing the serialized object and its type.
        """
        for type_name, cls in self._types.items():
            if isinstance(obj, cls):
                return {
                    '_type': type_name,
                    '_data': obj.to_dict()
                }
        
        raise ValueError(f"Object of type {type(obj).__name__} is not registered")
    
    def deserialize(self, data: Dict[str, Any]) -> Optional[Serializable]:
        """
        Deserialize an object from a dictionary with type information.
        
        Args:
            data: Dictionary containing serialized object and its type.
        
        Returns:
            The deserialized object, or None if the type is not registered.
        """
        if '_type' not in data or '_data' not in data:
            return None
        
        type_name = data['_type']
        obj_data = data['_data']
        
        cls = self.get_class(type_name)
        if cls:
            return cls.from_dict(obj_data)
        
        return None


# Singleton instance of the serialization registry
registry = SerializationRegistry()


# Type converters for common data types
def datetime_to_iso(dt: datetime.datetime) -> str:
    """
    Convert a datetime object to an ISO 8601 string.
    
    Args:
        dt: The datetime object to convert.
    
    Returns:
        ISO 8601 formatted string.
    """
    return dt.isoformat()


def iso_to_datetime(iso_str: str) -> datetime.datetime:
    """
    Convert an ISO 8601 string to a datetime object.
    
    Args:
        iso_str: The ISO 8601 string to convert.
    
    Returns:
        A datetime object.
    """
    return datetime.datetime.fromisoformat(iso_str)


def bytes_to_base64(data: bytes) -> str:
    """
    Convert bytes to a base64-encoded string.
    
    Args:
        data: The bytes to encode.
    
    Returns:
        Base64-encoded string.
    """
    return base64.b64encode(data).decode('utf-8')


def base64_to_bytes(base64_str: str) -> bytes:
    """
    Convert a base64-encoded string to bytes.
    
    Args:
        base64_str: The base64-encoded string to decode.
    
    Returns:
        The decoded bytes.
    """
    return base64.b64decode(base64_str)


# Helper functions for serialization
def serialize_collection(items: List[Serializable]) -> List[Dict[str, Any]]:
    """
    Serialize a collection of serializable objects.
    
    Args:
        items: List of serializable objects.
    
    Returns:
        List of serialized dictionaries.
    """
    return [item.to_dict() for item in items]


def deserialize_collection(
    data: List[Dict[str, Any]], 
    item_class: Type[Serializable]
) -> List[Serializable]:
    """
    Deserialize a collection of serialized objects.
    
    Args:
        data: List of serialized dictionaries.
        item_class: The class to deserialize items to.
    
    Returns:
        List of deserialized objects.
    """
    return [item_class.from_dict(item_data) for item_data in data]