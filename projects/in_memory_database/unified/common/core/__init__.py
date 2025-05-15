"""
Core functionality for the common library.

This package provides the core components of the unified in-memory database
library, which are shared by both vectordb and syncdb implementations.
"""

# Base classes
from .base import BaseRecord, BaseCollection, BaseOperation

# Storage classes
from .storage import InMemoryStorage, Index

# Serialization classes
from .serialization import (
    Serializable, 
    SerializationRegistry, 
    registry,
    datetime_to_iso,
    iso_to_datetime,
    bytes_to_base64,
    base64_to_bytes,
    serialize_collection,
    deserialize_collection
)

# Versioning classes
from .versioning import (
    ChangeType,
    Version,
    Change,
    VersionVector,
    ChangeTracker
)

# Schema classes
from .schema import (
    FieldType,
    SchemaField,
    Schema,
    SchemaRegistry
)

__all__ = [
    # Base
    'BaseRecord',
    'BaseCollection',
    'BaseOperation',
    
    # Storage
    'InMemoryStorage',
    'Index',
    
    # Serialization
    'Serializable',
    'SerializationRegistry',
    'registry',
    'datetime_to_iso',
    'iso_to_datetime',
    'bytes_to_base64',
    'base64_to_bytes',
    'serialize_collection',
    'deserialize_collection',
    
    # Versioning
    'ChangeType',
    'Version',
    'Change',
    'VersionVector',
    'ChangeTracker',
    
    # Schema
    'FieldType',
    'SchemaField',
    'Schema',
    'SchemaRegistry'
]