"""
Data encoder module for serializing and compressing Python data structures.

This module provides functionality to encode Python data structures into bytes,
optionally with compression, and decode them back. It also supports schema validation
and field-level access for dictionaries.
"""

import pickle
import zlib
import gzip
import lzma
from typing import Any, Dict, List, Optional, Set, Union, TypeVar, Callable

# Compression algorithm codes
ALG_NONE = 0
ALG_ZLIB = 1
ALG_GZIP = 2
ALG_LZMA = 3

# Type aliases
T = TypeVar('T')
SchemaType = Dict[str, Union[str, List[str]]]
DataType = Union[int, str, bool, List[Any], Set[Any], Dict[str, Any]]
CompressFunc = Callable[[bytes], bytes]


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
        Default value for the specified type
        
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
                if not _check_type(val, expected):
                    raise TypeError(f"Field '{key}' has wrong type")
                result[key] = val
        else:
            # Missing field: supply default
            if isinstance(expected, list):
                result[key] = []
            else:
                result[key] = _get_default_value(expected)
    
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


def _get_compressor(algorithm: str) -> tuple[CompressFunc, int]:
    """
    Get the compression function and algorithm code for the specified algorithm.
    
    Args:
        algorithm: Compression algorithm name ("zlib", "gzip", or "lzma")
        
    Returns:
        Tuple of (compression_function, algorithm_code)
        
    Raises:
        ValueError: If the algorithm is not supported
    """
    compressors = {
        "zlib": (zlib.compress, ALG_ZLIB),
        "gzip": (gzip.compress, ALG_GZIP),
        "lzma": (lzma.compress, ALG_LZMA)
    }
    
    alg = algorithm.lower()
    if alg not in compressors:
        raise ValueError(f"Unknown compression algorithm '{algorithm}'")
    
    return compressors[alg]


def encode(
    data: DataType, 
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
        data = _encode_with_schema(data, schema)
    
    # Validate data types
    _validate_data(data)
    
    # Serialize using pickle
    raw = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
    
    # Decide on compression
    algo_code = ALG_NONE
    payload = raw
    
    if compress:
        comp_func, code = _get_compressor(compression_algorithm)
        
        # Attempt compression
        compressed = comp_func(raw)
        
        # Use compression only if it shrinks data
        if len(compressed) < len(raw):
            algo_code = code
            payload = compressed
    
    # Build final bytes: first byte = algo code, rest = payload
    return bytes([algo_code]) + payload


def _decompress(code: int, payload: bytes) -> bytes:
    """
    Decompress payload based on algorithm code.
    
    Args:
        code: Algorithm code
        payload: Compressed payload
        
    Returns:
        Decompressed bytes
        
    Raises:
        ValueError: If the algorithm code is unknown
    """
    decompressors = {
        ALG_NONE: lambda p: p,
        ALG_ZLIB: zlib.decompress,
        ALG_GZIP: gzip.decompress,
        ALG_LZMA: lzma.decompress
    }
    
    if code not in decompressors:
        raise ValueError(f"Unknown encoding header: {code}")
    
    return decompressors[code](payload)


def decode(blob: Union[bytes, bytearray], field: Optional[str] = None) -> Any:
    """
    Decode bytes produced by encode(). Optionally extract a single field by name.
    
    Args:
        blob: Encoded bytes to decode
        field: Optional field name to extract from decoded dictionary
        
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
    raw = _decompress(code, payload)
    
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
