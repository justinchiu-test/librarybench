"""
Common library for vectordb and syncdb implementations.

This package provides a unified library of components that can be shared
between vectordb and syncdb implementations.
"""

__version__ = "0.1.0"

# Core components
from common.core import (
    # Base classes
    BaseRecord,
    BaseCollection,
    BaseOperation,
    
    # Storage
    InMemoryStorage,
    
    # Serialization
    Serializable,
    SerializationRegistry,
    
    # Versioning
    ChangeType,
    Version,
    ChangeTracker,
    
    # Schema
    FieldType,
    SchemaField,
    Schema,
    SchemaRegistry
)

# Re-export utility functions
from common.utils import (
    # ID generation
    generate_id,
    generate_uuid,
    
    # Time utilities
    get_timestamp,
    format_timestamp,
    parse_timestamp,
    
    # Validation
    validate_type,
    validate_required,
    deep_validate,
    
    # Type utilities
    to_int,
    to_float,
    to_bool,
    to_string,
    safe_cast,
    is_numeric,
    is_collection
)

# Optimization utilities
from common.optimization import (
    # Compression
    compress_string,
    decompress_string,
    compress_bytes,
    decompress_bytes,
    compress_json,
    decompress_json,
    TYPE_COMPRESSORS,
    TypeAwareCompressor
)

# Operations
from common.operations import (
    # Transform
    Transformer,
    Pipeline,
    Operation,
    
    # Query
    Query,
    QueryResult,
    QueryType,
    FilterCondition,
    Operator
)

__all__ = [
    # Version
    "__version__",
    
    # Base classes
    "BaseRecord",
    "BaseCollection",
    "BaseOperation",
    
    # Storage
    "InMemoryStorage",
    
    # Serialization
    "Serializable",
    "SerializationRegistry",
    
    # Versioning
    "ChangeType",
    "Version",
    "ChangeTracker",
    
    # Schema
    "FieldType",
    "SchemaField",
    "Schema",
    "SchemaRegistry",
    
    # Utils
    "generate_id",
    "generate_uuid",
    "get_timestamp",
    "format_timestamp",
    "parse_timestamp",
    "validate_type",
    "validate_required",
    "deep_validate",
    "to_int",
    "to_float",
    "to_bool",
    "to_string",
    "safe_cast",
    "is_numeric",
    "is_collection",
    
    # Optimization
    "compress_string",
    "decompress_string",
    "compress_bytes",
    "decompress_bytes",
    "compress_json",
    "decompress_json",
    "TYPE_COMPRESSORS",
    "TypeAwareCompressor",
    
    # Operations
    "Transformer",
    "Pipeline",
    "Operation",
    "Query",
    "QueryResult",
    "QueryType",
    "FilterCondition",
    "Operator"
]