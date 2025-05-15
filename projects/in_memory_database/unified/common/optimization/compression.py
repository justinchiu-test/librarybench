"""
Compression utilities for the common library.

This module provides utilities for compressing and decompressing data, with a
focus on type-aware compression to optimize for different data types.
"""

import json
import zlib
import base64
from typing import Any, Dict, Optional, Type, TypeVar, Union, List, Callable, Tuple
import re
from enum import Enum


def compress_bytes(data: bytes, level: int = 6) -> bytes:
    """
    Compress bytes using zlib.
    
    Args:
        data: The bytes to compress.
        level: Compression level (0-9, where 0 is no compression and 9 is maximum).
    
    Returns:
        Compressed bytes.
    """
    return zlib.compress(data, level)


def decompress_bytes(compressed_data: bytes) -> bytes:
    """
    Decompress bytes using zlib.
    
    Args:
        compressed_data: The compressed bytes to decompress.
    
    Returns:
        Decompressed bytes.
    """
    return zlib.decompress(compressed_data)


def compress_string(s: str, level: int = 6) -> bytes:
    """
    Compress a string using zlib.
    
    Args:
        s: The string to compress.
        level: Compression level (0-9, where 0 is no compression and 9 is maximum).
    
    Returns:
        Compressed bytes.
    """
    return compress_bytes(s.encode('utf-8'), level)


def decompress_string(compressed_data: bytes) -> str:
    """
    Decompress bytes to a string using zlib.
    
    Args:
        compressed_data: The compressed bytes to decompress.
    
    Returns:
        Decompressed string.
    """
    return decompress_bytes(compressed_data).decode('utf-8')


def compress_json(obj: Any, level: int = 6) -> bytes:
    """
    Compress a JSON-serializable object.
    
    Args:
        obj: The object to compress.
        level: Compression level (0-9, where 0 is no compression and 9 is maximum).
    
    Returns:
        Compressed bytes.
    """
    json_str = json.dumps(obj, separators=(',', ':'))
    return compress_string(json_str, level)


def decompress_json(compressed_data: bytes) -> Any:
    """
    Decompress bytes to a JSON object.
    
    Args:
        compressed_data: The compressed bytes to decompress.
    
    Returns:
        Decompressed JSON object.
    """
    json_str = decompress_string(compressed_data)
    return json.loads(json_str)


class CompressionFormat(Enum):
    """
    Enum representing compression formats for encoding in the TypeAwareCompressor.
    """
    NONE = "none"
    NUMERIC = "numeric"
    BOOLEAN = "boolean"
    STRING = "string"
    LIST = "list"
    DICT = "dict"
    BINARY = "binary"


class TypeCompressor:
    """
    Base class for type-specific compressors.
    """
    
    def __init__(self, compression_level: int = 6) -> None:
        """
        Initialize a type compressor.
        
        Args:
            compression_level: Compression level (0-9, where 0 is no compression
                              and 9 is maximum).
        """
        self.compression_level = compression_level
    
    def compress(self, value: Any) -> Tuple[CompressionFormat, bytes]:
        """
        Compress a value.
        
        Args:
            value: The value to compress.
        
        Returns:
            A tuple containing the compression format and compressed bytes.
        """
        raise NotImplementedError
    
    def decompress(
        self, 
        format_type: CompressionFormat, 
        compressed_data: bytes
    ) -> Any:
        """
        Decompress data.
        
        Args:
            format_type: The compression format.
            compressed_data: The compressed data.
        
        Returns:
            The decompressed value.
        """
        raise NotImplementedError
    
    def can_compress(self, value: Any) -> bool:
        """
        Check if this compressor can compress the given value.
        
        Args:
            value: The value to check.
        
        Returns:
            True if this compressor can compress the value, False otherwise.
        """
        raise NotImplementedError


class NumericCompressor(TypeCompressor):
    """
    Compressor for numeric values (int, float).
    """
    
    def can_compress(self, value: Any) -> bool:
        """
        Check if this compressor can compress the given value.
        
        Args:
            value: The value to check.
        
        Returns:
            True if the value is an int or float (but not bool), False otherwise.
        """
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    
    def compress(self, value: Union[int, float]) -> Tuple[CompressionFormat, bytes]:
        """
        Compress a numeric value.
        
        For numeric values, we simply convert to string to avoid floating-point issues.
        
        Args:
            value: The numeric value to compress.
        
        Returns:
            A tuple containing the compression format and compressed bytes.
        """
        if not self.can_compress(value):
            raise ValueError("Value must be a numeric type (int, float)")
        
        # Convert to string with full precision
        s = repr(value)
        
        return CompressionFormat.NUMERIC, s.encode('utf-8')
    
    def decompress(
        self, 
        format_type: CompressionFormat, 
        compressed_data: bytes
    ) -> Union[int, float]:
        """
        Decompress numeric data.
        
        Args:
            format_type: The compression format.
            compressed_data: The compressed data.
        
        Returns:
            The decompressed numeric value.
        """
        if format_type != CompressionFormat.NUMERIC:
            raise ValueError(f"Invalid format type: {format_type}")
        
        s = compressed_data.decode('utf-8')
        
        # Check if it's an int or float based on decimal point
        if '.' in s or 'e' in s.lower():
            return float(s)
        else:
            return int(s)


class BooleanCompressor(TypeCompressor):
    """
    Compressor for boolean values.
    """
    
    def can_compress(self, value: Any) -> bool:
        """
        Check if this compressor can compress the given value.
        
        Args:
            value: The value to check.
        
        Returns:
            True if the value is a bool, False otherwise.
        """
        return isinstance(value, bool)
    
    def compress(self, value: bool) -> Tuple[CompressionFormat, bytes]:
        """
        Compress a boolean value.
        
        For booleans, we simply use a single byte: 1 for True, 0 for False.
        
        Args:
            value: The boolean value to compress.
        
        Returns:
            A tuple containing the compression format and compressed bytes.
        """
        if not self.can_compress(value):
            raise ValueError("Value must be a boolean type")
        
        return CompressionFormat.BOOLEAN, b'1' if value else b'0'
    
    def decompress(
        self, 
        format_type: CompressionFormat, 
        compressed_data: bytes
    ) -> bool:
        """
        Decompress boolean data.
        
        Args:
            format_type: The compression format.
            compressed_data: The compressed data.
        
        Returns:
            The decompressed boolean value.
        """
        if format_type != CompressionFormat.BOOLEAN:
            raise ValueError(f"Invalid format type: {format_type}")
        
        return compressed_data == b'1'


class StringCompressor(TypeCompressor):
    """
    Compressor for string values.
    """
    
    def can_compress(self, value: Any) -> bool:
        """
        Check if this compressor can compress the given value.
        
        Args:
            value: The value to check.
        
        Returns:
            True if the value is a string, False otherwise.
        """
        return isinstance(value, str)
    
    def compress(self, value: str) -> Tuple[CompressionFormat, bytes]:
        """
        Compress a string value.
        
        Args:
            value: The string value to compress.
        
        Returns:
            A tuple containing the compression format and compressed bytes.
        """
        if not self.can_compress(value):
            raise ValueError("Value must be a string type")
        
        # For short strings, compression might make them larger, so only compress longer strings
        if len(value) < 20:
            return CompressionFormat.STRING, value.encode('utf-8')
        
        compressed = compress_string(value, self.compression_level)
        return CompressionFormat.STRING, compressed
    
    def decompress(
        self, 
        format_type: CompressionFormat, 
        compressed_data: bytes
    ) -> str:
        """
        Decompress string data.
        
        Args:
            format_type: The compression format.
            compressed_data: The compressed data.
        
        Returns:
            The decompressed string value.
        """
        if format_type != CompressionFormat.STRING:
            raise ValueError(f"Invalid format type: {format_type}")
        
        # Try to decompress, but fall back to direct decoding if it fails
        try:
            return decompress_string(compressed_data)
        except zlib.error:
            return compressed_data.decode('utf-8')


class ListCompressor(TypeCompressor):
    """
    Compressor for list values.
    """
    
    def __init__(
        self, 
        compression_level: int = 6, 
        type_aware_compressor: Optional['TypeAwareCompressor'] = None
    ) -> None:
        """
        Initialize a list compressor.
        
        Args:
            compression_level: Compression level (0-9, where 0 is no compression
                              and 9 is maximum).
            type_aware_compressor: TypeAwareCompressor to use for compressing list items.
        """
        super().__init__(compression_level)
        self.type_aware_compressor = type_aware_compressor
    
    def can_compress(self, value: Any) -> bool:
        """
        Check if this compressor can compress the given value.
        
        Args:
            value: The value to check.
        
        Returns:
            True if the value is a list, False otherwise.
        """
        return isinstance(value, list)
    
    def compress(self, value: List[Any]) -> Tuple[CompressionFormat, bytes]:
        """
        Compress a list value.
        
        Args:
            value: The list value to compress.
        
        Returns:
            A tuple containing the compression format and compressed bytes.
        """
        if not self.can_compress(value):
            raise ValueError("Value must be a list type")
        
        if not value:
            # Empty list
            return CompressionFormat.LIST, b'[]'
        
        if self.type_aware_compressor:
            # Compress each item with type awareness
            compressed_items = [
                self.type_aware_compressor.compress(item) 
                for item in value
            ]
            
            # Format: [format_type:compressed_data, ...]
            serialized = json.dumps(
                [(fmt.value, base64.b64encode(data).decode('ascii')) 
                 for fmt, data in compressed_items],
                separators=(',', ':')
            )
            
            compressed = compress_string(serialized, self.compression_level)
            return CompressionFormat.LIST, compressed
        else:
            # Just use JSON if we don't have a type-aware compressor
            serialized = json.dumps(value, separators=(',', ':'))
            compressed = compress_string(serialized, self.compression_level)
            return CompressionFormat.LIST, compressed
    
    def decompress(
        self, 
        format_type: CompressionFormat, 
        compressed_data: bytes
    ) -> List[Any]:
        """
        Decompress list data.
        
        Args:
            format_type: The compression format.
            compressed_data: The compressed data.
        
        Returns:
            The decompressed list value.
        """
        if format_type != CompressionFormat.LIST:
            raise ValueError(f"Invalid format type: {format_type}")
        
        if compressed_data == b'[]':
            return []
        
        try:
            serialized = decompress_string(compressed_data)
            data = json.loads(serialized)
            
            if self.type_aware_compressor and isinstance(data, list) and all(isinstance(item, list) and len(item) == 2 for item in data):
                # This is a list of [format_type, base64_data] pairs
                return [
                    self.type_aware_compressor.decompress(
                        CompressionFormat(fmt),
                        base64.b64decode(b64_data)
                    )
                    for fmt, b64_data in data
                ]
            else:
                # Regular JSON list
                return data
        except (zlib.error, json.JSONDecodeError):
            # Older format or not compressed
            try:
                return json.loads(compressed_data.decode('utf-8'))
            except json.JSONDecodeError:
                raise ValueError("Invalid compressed list data")


class DictCompressor(TypeCompressor):
    """
    Compressor for dictionary values.
    """
    
    def __init__(
        self, 
        compression_level: int = 6, 
        type_aware_compressor: Optional['TypeAwareCompressor'] = None
    ) -> None:
        """
        Initialize a dictionary compressor.
        
        Args:
            compression_level: Compression level (0-9, where 0 is no compression
                              and 9 is maximum).
            type_aware_compressor: TypeAwareCompressor to use for compressing dict values.
        """
        super().__init__(compression_level)
        self.type_aware_compressor = type_aware_compressor
    
    def can_compress(self, value: Any) -> bool:
        """
        Check if this compressor can compress the given value.
        
        Args:
            value: The value to check.
        
        Returns:
            True if the value is a dict, False otherwise.
        """
        return isinstance(value, dict)
    
    def compress(self, value: Dict[str, Any]) -> Tuple[CompressionFormat, bytes]:
        """
        Compress a dictionary value.
        
        Args:
            value: The dictionary value to compress.
        
        Returns:
            A tuple containing the compression format and compressed bytes.
        """
        if not self.can_compress(value):
            raise ValueError("Value must be a dict type")
        
        if not value:
            # Empty dict
            return CompressionFormat.DICT, b'{}'
        
        if self.type_aware_compressor:
            # Compress each value with type awareness (keys are always strings)
            compressed_items = {
                key: self.type_aware_compressor.compress(val)
                for key, val in value.items()
            }
            
            # Format: {"key": [format_type, compressed_data_base64], ...}
            serialized = json.dumps(
                {
                    key: [fmt.value, base64.b64encode(data).decode('ascii')]
                    for key, (fmt, data) in compressed_items.items()
                },
                separators=(',', ':')
            )
            
            compressed = compress_string(serialized, self.compression_level)
            return CompressionFormat.DICT, compressed
        else:
            # Just use JSON if we don't have a type-aware compressor
            serialized = json.dumps(value, separators=(',', ':'))
            compressed = compress_string(serialized, self.compression_level)
            return CompressionFormat.DICT, compressed
    
    def decompress(
        self, 
        format_type: CompressionFormat, 
        compressed_data: bytes
    ) -> Dict[str, Any]:
        """
        Decompress dictionary data.
        
        Args:
            format_type: The compression format.
            compressed_data: The compressed data.
        
        Returns:
            The decompressed dictionary value.
        """
        if format_type != CompressionFormat.DICT:
            raise ValueError(f"Invalid format type: {format_type}")
        
        if compressed_data == b'{}':
            return {}
        
        try:
            serialized = decompress_string(compressed_data)
            data = json.loads(serialized)
            
            if self.type_aware_compressor and isinstance(data, dict) and all(isinstance(v, list) and len(v) == 2 for v in data.values()):
                # This is a dict of key -> [format_type, base64_data] pairs
                return {
                    key: self.type_aware_compressor.decompress(
                        CompressionFormat(fmt),
                        base64.b64decode(b64_data)
                    )
                    for key, [fmt, b64_data] in data.items()
                }
            else:
                # Regular JSON dict
                return data
        except (zlib.error, json.JSONDecodeError):
            # Older format or not compressed
            try:
                return json.loads(compressed_data.decode('utf-8'))
            except json.JSONDecodeError:
                raise ValueError("Invalid compressed dict data")


class BinaryCompressor(TypeCompressor):
    """
    Compressor for binary data (bytes).
    """
    
    def can_compress(self, value: Any) -> bool:
        """
        Check if this compressor can compress the given value.
        
        Args:
            value: The value to check.
        
        Returns:
            True if the value is bytes, False otherwise.
        """
        return isinstance(value, bytes)
    
    def compress(self, value: bytes) -> Tuple[CompressionFormat, bytes]:
        """
        Compress binary data.
        
        Args:
            value: The bytes value to compress.
        
        Returns:
            A tuple containing the compression format and compressed bytes.
        """
        if not self.can_compress(value):
            raise ValueError("Value must be a bytes type")
        
        # Only compress if it's worth it
        if len(value) < 20:
            return CompressionFormat.BINARY, value
        
        compressed = compress_bytes(value, self.compression_level)
        
        # Only use the compressed version if it's smaller
        if len(compressed) < len(value):
            return CompressionFormat.BINARY, compressed
        else:
            return CompressionFormat.BINARY, value
    
    def decompress(
        self, 
        format_type: CompressionFormat, 
        compressed_data: bytes
    ) -> bytes:
        """
        Decompress binary data.
        
        Args:
            format_type: The compression format.
            compressed_data: The compressed data.
        
        Returns:
            The decompressed bytes value.
        """
        if format_type != CompressionFormat.BINARY:
            raise ValueError(f"Invalid format type: {format_type}")
        
        # Try to decompress, but return the original data if decompression fails
        try:
            return decompress_bytes(compressed_data)
        except zlib.error:
            return compressed_data


class NoneCompressor(TypeCompressor):
    """
    Compressor for None values.
    """
    
    def can_compress(self, value: Any) -> bool:
        """
        Check if this compressor can compress the given value.
        
        Args:
            value: The value to check.
        
        Returns:
            True if the value is None, False otherwise.
        """
        return value is None
    
    def compress(self, value: None) -> Tuple[CompressionFormat, bytes]:
        """
        Compress None.
        
        Args:
            value: The None value to compress.
        
        Returns:
            A tuple containing the compression format and compressed bytes.
        """
        if not self.can_compress(value):
            raise ValueError("Value must be None")
        
        return CompressionFormat.NONE, b''
    
    def decompress(
        self, 
        format_type: CompressionFormat, 
        compressed_data: bytes
    ) -> None:
        """
        Decompress None data.
        
        Args:
            format_type: The compression format.
            compressed_data: The compressed data.
        
        Returns:
            None
        """
        if format_type != CompressionFormat.NONE:
            raise ValueError(f"Invalid format type: {format_type}")
        
        return None


# Dictionary of compressors by format type
TYPE_COMPRESSORS = {
    CompressionFormat.NONE: NoneCompressor,
    CompressionFormat.NUMERIC: NumericCompressor,
    CompressionFormat.BOOLEAN: BooleanCompressor,
    CompressionFormat.STRING: StringCompressor,
    CompressionFormat.BINARY: BinaryCompressor,
    CompressionFormat.LIST: ListCompressor,
    CompressionFormat.DICT: DictCompressor
}


class TypeAwareCompressor:
    """
    Compressor that automatically selects the appropriate compression algorithm
    based on the data type.
    """
    
    def __init__(self, compression_level: int = 6) -> None:
        """
        Initialize a type-aware compressor.
        
        Args:
            compression_level: Compression level (0-9, where 0 is no compression
                              and 9 is maximum).
        """
        self.compression_level = compression_level
        
        # Initialize compressors
        self.compressors = {
            fmt: cls(compression_level) 
            for fmt, cls in TYPE_COMPRESSORS.items()
            if fmt not in (CompressionFormat.LIST, CompressionFormat.DICT)
        }
        
        # List and Dict compressors need a reference to this TypeAwareCompressor
        self.compressors[CompressionFormat.LIST] = ListCompressor(
            compression_level, self
        )
        self.compressors[CompressionFormat.DICT] = DictCompressor(
            compression_level, self
        )
    
    def compress(self, value: Any) -> Tuple[CompressionFormat, bytes]:
        """
        Compress a value using the appropriate compressor for its type.
        
        Args:
            value: The value to compress.
        
        Returns:
            A tuple containing the compression format and compressed bytes.
        """
        # Find a compressor that can handle this value
        for compressor in self.compressors.values():
            if compressor.can_compress(value):
                return compressor.compress(value)
        
        # Fall back to JSON for unhandled types
        serialized = json.dumps(value, separators=(',', ':'))
        compressed = compress_string(serialized, self.compression_level)
        return CompressionFormat.STRING, compressed
    
    def decompress(
        self, 
        format_type: CompressionFormat, 
        compressed_data: bytes
    ) -> Any:
        """
        Decompress data using the specified format type.
        
        Args:
            format_type: The compression format.
            compressed_data: The compressed data.
        
        Returns:
            The decompressed value.
        """
        if format_type not in self.compressors:
            raise ValueError(f"Unsupported compression format: {format_type}")
        
        return self.compressors[format_type].decompress(
            format_type, compressed_data
        )
    
    def serialize(self, value: Any) -> bytes:
        """
        Serialize a value with type information.
        
        This method compresses the value and adds format type information, so
        the value can be correctly decompressed later.
        
        Args:
            value: The value to serialize.
        
        Returns:
            Serialized bytes, including format type information.
        """
        format_type, compressed_data = self.compress(value)
        
        # Format: <format_type>:<compressed_data>
        return format_type.value.encode('utf-8') + b':' + compressed_data
    
    def deserialize(self, serialized_data: bytes) -> Any:
        """
        Deserialize a value with type information.
        
        Args:
            serialized_data: The serialized data to deserialize.
        
        Returns:
            The deserialized value.
        """
        # Split by first colon to get format type and compressed data
        parts = serialized_data.split(b':', 1)
        if len(parts) != 2:
            raise ValueError("Invalid serialized data format")
        
        format_type_str, compressed_data = parts
        try:
            format_type = CompressionFormat(format_type_str.decode('utf-8'))
        except (ValueError, UnicodeDecodeError):
            raise ValueError(f"Invalid compression format: {format_type_str}")
        
        return self.decompress(format_type, compressed_data)