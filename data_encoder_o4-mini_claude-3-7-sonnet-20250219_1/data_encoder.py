"""
Data encoder module for serializing and compressing Python data structures.

This module provides functionality to encode Python data types into bytes,
optionally with compression, and decode them back to their original form.
It also supports schema validation and field-level access.
"""

import pickle
import zlib
import gzip
import lzma
from typing import Any, Dict, List, Optional, Set, Union, TypeVar, cast

# Compression algorithm codes
class CompressionAlgorithm:
    """Constants for compression algorithm codes."""
    NONE = 0
    ZLIB = 1
    GZIP = 2
    LZMA = 3

# Type definitions
T = TypeVar('T')
SchemaType = Dict[str, Union[str, List[str]]]
SupportedTypes = Union[int, str, bool, List[Any], Set[Any], Dict[str, Any]]

# Type checking functions
def _check_type(value: Any, expected: str) -> bool:
    """
    Check if a value matches the expected type descriptor.
    
    Args:
        value: The value to check
        expected: Type descriptor ("int", "str", "bool", or "dict")
        
    Returns:
        bool: True if the value matches the expected type, False otherwise
    """
    type_checkers = {
        "int": lambda v: isinstance(v, int),
        "str": lambda v: isinstance(v, str),
        "bool": lambda v: isinstance(v, bool),
        "dict": lambda v: isinstance(v, dict)
    }
    
    return type_checkers.get(expected, lambda _: False)(value)

def _get_default_value(expected_type: str) -> Any:
    """
    Get the default value for a given type descriptor.
    
    Args:
        expected_type: Type descriptor ("int", "str", "bool", or "dict")
        
    Returns:
        The default value for the specified type
        
    Raises:
        TypeError: If the type is not supported
    """
    defaults = {
        "int": 0,
        "str": "",
        "bool": False,
        "dict": {}
    }
    
    if expected_type not in defaults:
        raise TypeError(f"Unsupported schema type {expected_type}")
    
    return defaults[expected_type]

def _encode_with_schema(data: Dict[str, Any], schema: SchemaType) -> Dict[str, Any]:
    """
    Apply schema to data: fill defaults for missing fields and validate types.
    
    Args:
        data: Dictionary to validate against schema
        schema: Schema definition
        
    Returns:
        Dict with validated and default-filled values
        
    Raises:
        TypeError: If data is not a dict or if field types don't match schema
    """
    if not isinstance(data, dict):
        raise TypeError("Data must be a dict when using schema")
    
    result = {}
    
    # Process schema fields
    for key, expected in schema.items():
        if key in data:
            val = data[key]
            # Validate
            if isinstance(expected, list):
                # Expect a list with homogeneous subtype
                if not isinstance(val, list):
                    raise TypeError(f"Field '{key}' must be a list")
                
                subtype = expected[0]
                for item in val:
                    if not _check_type(item, subtype):
                        raise TypeError(f"Field '{key}' list item has wrong type")
                
                # Keep as is
                result[key] = val
            else:
                if not _check_type(val, cast(str, expected)):
                    raise TypeError(f"Field '{key}' has wrong type")
                result[key] = val
        else:
            # Missing field: supply default
            if isinstance(expected, list):
                result[key] = []
            else:
                result[key] = _get_default_value(cast(str, expected))
    
    # Include any extra keys not in schema
    for key, val in data.items():
        if key not in result:
            result[key] = val
    
    return result

def _validate_data(obj: Any) -> None:
    """
    Recursively validate that obj is composed of supported types.
    
    Supported types:
    - int, str, bool
    - list (homogeneous)
    - set (homogeneous)
    - dict (str keys)
    
    Args:
        obj: Object to validate
        
    Raises:
        TypeError: On unsupported or mixed types
    """
    obj_type = type(obj)
    
    if obj_type in (int, str, bool):
        return
    
    elif isinstance(obj, list):
        if not obj:
            return
            
        first_type = type(obj[0])
        # Validate allowed type
        if first_type not in (int, str, bool, list, set, dict):
            raise TypeError("Unsupported element type in list")
            
        for item in obj:
            if type(item) is not first_type:
                raise TypeError("Mixed types in list")
            _validate_data(item)
    
    elif isinstance(obj, set):
        if not obj:
            return
            
        # Get a sample
        first = next(iter(obj))
        first_type = type(first)
        
        if first_type not in (int, str, bool, list, set, dict):
            raise TypeError("Unsupported element type in set")
            
        for item in obj:
            if type(item) is not first_type:
                raise TypeError("Mixed types in set")
            _validate_data(item)
    
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if not isinstance(k, str):
                raise TypeError("Dictionary keys must be strings")
            _validate_data(v)
    
    else:
        raise TypeError(f"Type {obj_type} not supported")

def _compress_data(raw_data: bytes, algorithm: str) -> tuple[int, bytes]:
    """
    Compress data using the specified algorithm.
    
    Args:
        raw_data: Data to compress
        algorithm: Compression algorithm name
        
    Returns:
        Tuple of (algorithm_code, compressed_data)
        
    Raises:
        ValueError: If the algorithm is unknown
    """
    compressors = {
        "zlib": (zlib.compress, CompressionAlgorithm.ZLIB),
        "gzip": (gzip.compress, CompressionAlgorithm.GZIP),
        "lzma": (lzma.compress, CompressionAlgorithm.LZMA)
    }
    
    alg = algorithm.lower()
    if alg not in compressors:
        raise ValueError(f"Unknown compression algorithm '{algorithm}'")
    
    comp_func, code = compressors[alg]
    compressed = comp_func(raw_data)
    
    # Use compression only if it shrinks data
    if len(compressed) < len(raw_data):
        return code, compressed
    else:
        return CompressionAlgorithm.NONE, raw_data

def _decompress_data(payload: bytes, code: int) -> bytes:
    """
    Decompress data based on the compression algorithm code.
    
    Args:
        payload: Compressed data
        code: Compression algorithm code
        
    Returns:
        Decompressed data
        
    Raises:
        ValueError: If the compression code is unknown
    """
    decompressors = {
        CompressionAlgorithm.NONE: lambda x: x,
        CompressionAlgorithm.ZLIB: zlib.decompress,
        CompressionAlgorithm.GZIP: gzip.decompress,
        CompressionAlgorithm.LZMA: lzma.decompress
    }
    
    if code not in decompressors:
        raise ValueError(f"Unknown encoding header: {code}")
    
    return decompressors[code](payload)

def encode(
    data: SupportedTypes, 
    compress: bool = False, 
    compression_algorithm: str = "zlib", 
    schema: Optional[SchemaType] = None
) -> bytes:
    """
    Encode supported Python data types into bytes.
    
    Args:
        data: Data to encode
        compress: Whether to compress the serialized payload
        compression_algorithm: Compression algorithm to use ("zlib", "gzip", or "lzma")
        schema: Optional schema for validation and default values
        
    Returns:
        Encoded bytes
        
    Raises:
        TypeError: If data types are not supported
        ValueError: If compression algorithm is unknown
    """
    # Schema processing
    if schema is not None:
        data = _encode_with_schema(cast(Dict[str, Any], data), schema)
    
    # Validate data types
    _validate_data(data)
    
    # Serialize using pickle
    raw = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
    
    # Decide on compression
    algo_code = CompressionAlgorithm.NONE
    payload = raw
    
    if compress:
        algo_code, payload = _compress_data(raw, compression_algorithm)
    
    # Build final bytes: first byte = algo code, rest = payload
    return bytes([algo_code]) + payload

def decode(blob: Union[bytes, bytearray], field: Optional[str] = None) -> Any:
    """
    Decode bytes produced by encode(). Optionally extract a single field by name.
    
    Args:
        blob: Encoded bytes to decode
        field: Optional field name to extract
        
    Returns:
        Decoded data or field value
        
    Raises:
        ValueError: If blob is invalid or field is not found
    """
    if not isinstance(blob, (bytes, bytearray)) or len(blob) < 1:
        raise ValueError("Invalid blob for decoding")
    
    code = blob[0]
    payload = blob[1:]
    
    # Decompress if needed
    try:
        raw = _decompress_data(payload, code)
    except Exception as e:
        raise ValueError(f"Failed to decompress data: {e}") from e
    
    # Deserialize
    try:
        data = pickle.loads(raw)
    except Exception as e:
        raise ValueError("Failed to deserialize data") from e
    
    # Field extraction
    if field is None:
        return data
    
    # Field-level access
    if not isinstance(data, dict):
        raise ValueError("Field specified but decoded data is not a dict")
    
    if field not in data:
        raise ValueError(f"Field '{field}' not found")
    
    return data[field]
