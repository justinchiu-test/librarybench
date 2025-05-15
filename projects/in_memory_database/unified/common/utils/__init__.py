"""
Utility functions for the common library.

This package provides various utility functions used by both vectordb and syncdb 
implementations.
"""

from .id_generator import generate_id, generate_uuid
from .time_utils import get_timestamp, format_timestamp, parse_timestamp
from .validation import validate_type, validate_required, deep_validate
from .type_utils import (
    to_int, 
    to_float, 
    to_bool, 
    to_string,
    safe_cast,
    is_numeric,
    is_collection
)

__all__ = [
    # ID generation
    'generate_id',
    'generate_uuid',
    
    # Time utilities
    'get_timestamp',
    'format_timestamp',
    'parse_timestamp',
    
    # Validation
    'validate_type',
    'validate_required',
    'deep_validate',
    
    # Type utilities
    'to_int',
    'to_float',
    'to_bool',
    'to_string',
    'safe_cast',
    'is_numeric',
    'is_collection'
]