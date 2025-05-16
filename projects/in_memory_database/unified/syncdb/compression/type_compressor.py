"""
Type-aware compression for different data types.

This module is now a wrapper around the common library's compression utilities
that maintains compatibility with the existing API.
"""
from typing import Dict, List, Any, Optional, Callable, Type, Union, Tuple
import json
import base64
import zlib
import struct
import re
from datetime import datetime, date, timedelta
from enum import Enum
import time

from common.optimization.compression import (
    TypeAwareCompressor, CompressionFormat,
    compress_string, decompress_string,
    compress_bytes, decompress_bytes,
    compress_json, decompress_json
)


class CompressionLevel(Enum):
    """Compression level for balancing CPU usage and size reduction."""
    NONE = 0  # No compression
    LOW = 1   # Low compression, less CPU usage
    MEDIUM = 2  # Medium compression, balanced
    HIGH = 3  # High compression, more CPU usage


def _compression_level_to_zlib(level: CompressionLevel) -> int:
    """Convert CompressionLevel to zlib compression level (1-9)."""
    if level == CompressionLevel.NONE:
        return 0
    elif level == CompressionLevel.LOW:
        return 3
    elif level == CompressionLevel.MEDIUM:
        return 6
    elif level == CompressionLevel.HIGH:
        return 9
    else:
        return 6  # Default


class TypeCompressor:
    """Base class for type-specific compressors."""
    def compress(self, value: Any) -> bytes:
        """Compress a value to bytes."""
        raise NotImplementedError
    
    def decompress(self, data: bytes) -> Any:
        """Decompress bytes to a value."""
        raise NotImplementedError


class IntCompressor(TypeCompressor):
    """Compressor for integer values."""
    def compress(self, value: int) -> bytes:
        """Compress an integer to bytes."""
        # Use variable-length encoding to save space for small integers
        if -128 <= value < 128:
            return struct.pack('b', value)  # 1 byte
        elif -32768 <= value < 32768:
            return struct.pack('>h', value)  # 2 bytes
        elif -2147483648 <= value < 2147483648:
            return struct.pack('>i', value)  # 4 bytes
        else:
            return struct.pack('>q', value)  # 8 bytes
    
    def decompress(self, data: bytes) -> int:
        """Decompress bytes to an integer."""
        if len(data) == 1:
            return struct.unpack('b', data)[0]
        elif len(data) == 2:
            return struct.unpack('>h', data)[0]
        elif len(data) == 4:
            return struct.unpack('>i', data)[0]
        else:
            return struct.unpack('>q', data)[0]


class FloatCompressor(TypeCompressor):
    """Compressor for floating point values."""
    def compress(self, value: float) -> bytes:
        """Compress a float to bytes."""
        return struct.pack('>f', value)  # 4 bytes
    
    def decompress(self, data: bytes) -> float:
        """Decompress bytes to a float."""
        return struct.unpack('>f', data)[0]


class TextCompressor(TypeCompressor):
    """Compressor for text values."""
    def __init__(self, level: CompressionLevel = CompressionLevel.MEDIUM):
        self.level = level
        self.zlib_level = _compression_level_to_zlib(level)
    
    def compress(self, value: str) -> bytes:
        """Compress a string to bytes."""
        # For very short strings, compression might increase size
        if len(value) < 10 or self.level == CompressionLevel.NONE:
            # Just encode to UTF-8
            return value.encode('utf-8')
        
        # Use the common library's string compression
        return compress_string(value, self.zlib_level)
    
    def decompress(self, data: bytes) -> str:
        """Decompress bytes to a string."""
        try:
            # Try to decompress using the common library
            return decompress_string(data)
        except zlib.error:
            # If decompression fails, assume it wasn't compressed
            return data.decode('utf-8')


class BinaryCompressor(TypeCompressor):
    """Compressor for binary data."""
    def __init__(self, level: CompressionLevel = CompressionLevel.MEDIUM):
        self.level = level
        self.zlib_level = _compression_level_to_zlib(level)
    
    def compress(self, value: bytes) -> bytes:
        """Compress binary data."""
        if len(value) < 50 or self.level == CompressionLevel.NONE:
            # For very small binary data, don't compress
            return value
        
        # Use the common library's bytes compression
        return compress_bytes(value, self.zlib_level)
    
    def decompress(self, data: bytes) -> bytes:
        """Decompress binary data."""
        try:
            # Try to decompress using the common library
            return decompress_bytes(data)
        except zlib.error:
            # If decompression fails, assume it wasn't compressed
            return data


class DateTimeCompressor(TypeCompressor):
    """Compressor for datetime values."""
    def compress(self, value: Union[datetime, date]) -> bytes:
        """Compress a datetime to bytes."""
        if isinstance(value, datetime):
            # Store as Unix timestamp (seconds since epoch)
            timestamp = value.timestamp()
            return struct.pack('>d', timestamp)  # 8 bytes
        elif isinstance(value, date):
            # Store as days since epoch (January 1, 1970)
            epoch = date(1970, 1, 1)
            days = (value - epoch).days
            return struct.pack('>i', days)  # 4 bytes
        else:
            raise ValueError(f"Unsupported date type: {type(value)}")
    
    def decompress(self, data: bytes) -> Union[datetime, date]:
        """Decompress bytes to a datetime."""
        if len(data) == 8:
            # Datetime (timestamp)
            timestamp = struct.unpack('>d', data)[0]
            return datetime.fromtimestamp(timestamp)
        else:
            # Date (days since epoch)
            days = struct.unpack('>i', data)[0]
            epoch = date(1970, 1, 1)
            return epoch + timedelta(days=days)


class BooleanCompressor(TypeCompressor):
    """Compressor for boolean values."""
    def compress(self, value: bool) -> bytes:
        """Compress a boolean to bytes."""
        return struct.pack('?', value)  # 1 byte
    
    def decompress(self, data: bytes) -> bool:
        """Decompress bytes to a boolean."""
        return struct.unpack('?', data)[0]


class NoneCompressor(TypeCompressor):
    """Compressor for None values."""
    def compress(self, value: None) -> bytes:
        """Compress None to bytes."""
        return b''  # Empty bytes
    
    def decompress(self, data: bytes) -> None:
        """Decompress bytes to None."""
        return None


class ListCompressor(TypeCompressor):
    """
    Compressor for list values, using the common library's TypeAwareCompressor internally.
    """
    def __init__(self, factory: 'CompressorFactory'):
        self.factory = factory
        self.common_compressor = factory.common_compressor
    
    def compress(self, value: List[Any]) -> bytes:
        """
        Compress a list using the common library.
        
        Args:
            value: List to compress
            
        Returns:
            Compressed bytes
        """
        # Check if the list is empty
        if not value:
            return b'\x00'  # Empty list marker
        
        # Use the common library to compress the list
        format_type, compressed_data = self.common_compressor.compress(value)
        # Add list marker at the beginning
        return b'\x01' + compressed_data
    
    def decompress(self, data: bytes) -> List[Any]:
        """
        Decompress bytes to a list.
        
        Args:
            data: Compressed bytes
            
        Returns:
            Decompressed list
        """
        # Check for empty list marker
        if data == b'\x00':
            return []
        
        # Strip list marker if present
        if data and data[0] == 1:
            data = data[1:]
        
        try:
            # Try using the common library with the LIST format
            return self.common_compressor.decompress(CompressionFormat.LIST, data)
        except Exception:
            # Fall back to JSON if that fails
            try:
                return json.loads(data.decode('utf-8'))
            except:
                # Last resort
                return []


class DictCompressor(TypeCompressor):
    """
    Compressor for dictionary values, using the common library's TypeAwareCompressor internally.
    """
    def __init__(self, factory: 'CompressorFactory'):
        self.factory = factory
        self.common_compressor = factory.common_compressor
    
    def compress(self, value: Dict[str, Any]) -> bytes:
        """
        Compress a dictionary using the common library.
        
        Args:
            value: Dictionary to compress
            
        Returns:
            Compressed bytes
        """
        # Check if the dictionary is empty
        if not value:
            return b'\x00'  # Empty dict marker
        
        # Use the common library to compress the dictionary
        format_type, compressed_data = self.common_compressor.compress(value)
        # Add dict marker at the beginning
        return b'\x01' + compressed_data
    
    def decompress(self, data: bytes) -> Dict[str, Any]:
        """
        Decompress bytes to a dictionary.
        
        Args:
            data: Compressed bytes
            
        Returns:
            Decompressed dictionary
        """
        # Check for empty dict marker
        if data == b'\x00':
            return {}
        
        # Strip dict marker if present
        if data and data[0] == 1:
            data = data[1:]
        
        try:
            # Try using the common library with the DICT format
            return self.common_compressor.decompress(CompressionFormat.DICT, data)
        except Exception:
            # Fall back to JSON if that fails
            try:
                return json.loads(data.decode('utf-8'))
            except:
                # Last resort
                return {}


class ListCompressorAdapter(ListCompressor):
    """
    Adapter for the common library's TypeAwareCompressor for lists.
    """
    def __init__(self, common_compressor: TypeAwareCompressor):
        self.common_compressor = common_compressor
    
    def compress(self, value: List[Any]) -> bytes:
        """
        Compress a list using the common library.
        
        Args:
            value: List to compress
            
        Returns:
            Compressed bytes
        """
        format_type, compressed_data = self.common_compressor.compress(value)
        return compressed_data
    
    def decompress(self, data: bytes) -> List[Any]:
        """
        Decompress bytes to a list using the common library.
        
        Args:
            data: Compressed bytes
            
        Returns:
            Decompressed list
        """
        try:
            # Try using the common library with the LIST format
            return self.common_compressor.decompress(CompressionFormat.LIST, data)
        except Exception:
            # Fall back to JSON if that fails
            return json.loads(data.decode('utf-8'))


class DictCompressorAdapter(DictCompressor):
    """
    Adapter for the common library's TypeAwareCompressor for dictionaries.
    """
    def __init__(self, common_compressor: TypeAwareCompressor):
        self.common_compressor = common_compressor
    
    def compress(self, value: Dict[str, Any]) -> bytes:
        """
        Compress a dictionary using the common library.
        
        Args:
            value: Dictionary to compress
            
        Returns:
            Compressed bytes
        """
        format_type, compressed_data = self.common_compressor.compress(value)
        return compressed_data
    
    def decompress(self, data: bytes) -> Dict[str, Any]:
        """
        Decompress bytes to a dictionary using the common library.
        
        Args:
            data: Compressed bytes
            
        Returns:
            Decompressed dictionary
        """
        try:
            # Try using the common library with the DICT format
            return self.common_compressor.decompress(CompressionFormat.DICT, data)
        except Exception:
            # Fall back to JSON if that fails
            return json.loads(data.decode('utf-8'))


class CompressorFactory:
    """Factory for creating and managing type-specific compressors."""
    def __init__(self, compression_level: CompressionLevel = CompressionLevel.MEDIUM):
        self.compression_level = compression_level
        self.zlib_level = _compression_level_to_zlib(compression_level)
        
        # Create a common library compressor
        self.common_compressor = TypeAwareCompressor(self.zlib_level)
        
        # Type signature mapping
        self.type_to_signature: Dict[Type, int] = {
            type(None): 0,
            bool: 1,
            int: 2,
            float: 3,
            str: 4,
            bytes: 5,
            list: 6,
            dict: 7,
            datetime: 8,
            date: 9
        }
        
        # Initialize compressors
        self.signature_to_compressor: Dict[int, TypeCompressor] = {}
        self._initialize_compressors()
    
    def _initialize_compressors(self) -> None:
        """Initialize the compressors for each type."""
        # Create list and dict compressors
        list_compressor = ListCompressor(self)
        dict_compressor = DictCompressor(self)
        
        # Mix of direct compressors and common library adapters
        self.signature_to_compressor = {
            0: NoneCompressor(),
            1: BooleanCompressor(),
            2: IntCompressor(),
            3: FloatCompressor(),
            4: TextCompressor(self.compression_level),
            5: BinaryCompressor(self.compression_level),
            6: list_compressor,  # Use ListCompressor for lists
            7: dict_compressor,  # Use DictCompressor for dicts
            8: DateTimeCompressor(),
            9: DateTimeCompressor()
        }
    
    def get_type_signature(self, value: Any) -> int:
        """Get the type signature for a value."""
        value_type = type(value)
        return self.type_to_signature.get(value_type, 0)
    
    def get_compressor_for_type(self, value_type: Type) -> Any:
        """Get the compressor for a specific type."""
        type_signature = self.type_to_signature.get(value_type, 0)
        return self.signature_to_compressor.get(type_signature, NoneCompressor())
    
    def get_compressor_for_signature(self, type_signature: int) -> Any:
        """Get the compressor for a specific type signature."""
        return self.signature_to_compressor.get(type_signature, NoneCompressor())
    
    def set_compression_level(self, level: CompressionLevel) -> None:
        """Set the compression level for all compressors."""
        self.compression_level = level
        self.zlib_level = _compression_level_to_zlib(level)
        
        # Update the common compressor's compression level
        self.common_compressor = TypeAwareCompressor(self.zlib_level)
        
        # Reinitialize compressors with the new level
        self._initialize_compressors()


class PayloadCompressor:
    """
    Compresses and decompresses data for efficient transfer.
    This now uses the common library's TypeAwareCompressor internally.
    """
    def __init__(self, 
               compression_level: CompressionLevel = CompressionLevel.MEDIUM, 
               schema: Optional[Dict[str, Dict[str, Type]]] = None):
        self.compression_level = compression_level
        self.zlib_level = _compression_level_to_zlib(compression_level)
        
        # Create a common library compressor
        self.common_compressor = TypeAwareCompressor(self.zlib_level)
        
        # For backward compatibility
        self.compressor_factory = CompressorFactory(compression_level)
        self.schema = schema or {}  # Table name -> {column name -> type}
    
    def compress_record(self, 
                       table_name: str, 
                       record: Dict[str, Any]) -> bytes:
        """
        Compress a record using type-aware compression.
        
        Args:
            table_name: Name of the table
            record: Record to compress
            
        Returns:
            Compressed record as bytes
        """
        # Use the common library to compress the record
        format_type, compressed_data = self.common_compressor.compress(record)
        
        # Check if compression actually reduced the size compared to JSON
        json_data = json.dumps(record, separators=(',', ':')).encode('utf-8')
        
        # Only use compressed data if it's actually smaller
        if len(compressed_data) < len(json_data):
            # For HIGH compression level, apply additional zlib compression
            if self.compression_level == CompressionLevel.HIGH:
                # Apply a higher zlib compression level
                compressed_data = zlib.compress(compressed_data, 9)
            return compressed_data
        else:
            # Fall back to JSON if compression didn't help, but still apply zlib for HIGH
            if self.compression_level == CompressionLevel.HIGH:
                return zlib.compress(json_data, 9)
            return json_data
    
    def decompress_record(self, 
                         table_name: str, 
                         data: bytes) -> Dict[str, Any]:
        """
        Decompress a record.
        
        Args:
            table_name: Name of the table
            data: Compressed record data
            
        Returns:
            Decompressed record
        """
        # First try to handle HIGH compression level (zlib)
        if self.compression_level == CompressionLevel.HIGH:
            try:
                # Try to decompress with zlib first
                decompressed_data = zlib.decompress(data)
                
                # Then try to decompress as a dictionary
                try:
                    return self.common_compressor.decompress(CompressionFormat.DICT, decompressed_data)
                except Exception:
                    # Fall back to JSON if that fails
                    try:
                        return json.loads(decompressed_data.decode('utf-8'))
                    except Exception:
                        # If decompressed data isn't JSON, continue to regular process
                        pass
            except zlib.error:
                # Not zlib compressed, continue to regular process
                pass
        
        # Regular decompression process
        try:
            return self.common_compressor.decompress(CompressionFormat.DICT, data)
        except Exception:
            # Fall back to JSON if that fails
            try:
                return json.loads(data.decode('utf-8'))
            except Exception:
                # Last resort: try json decompression
                return decompress_json(data)
    
    def compress_changes(self, 
                        table_name: str, 
                        changes: List[Dict[str, Any]]) -> bytes:
        """
        Compress a list of changes.
        
        Args:
            table_name: Name of the table
            changes: List of changes to compress
            
        Returns:
            Compressed changes as bytes
        """
        # Use the common library to compress the changes
        format_type, compressed_data = self.common_compressor.compress(changes)
        
        # Check if compression actually reduced the size compared to JSON
        json_data = json.dumps(changes, separators=(',', ':')).encode('utf-8')
        
        # Only use compressed data if it's actually smaller
        if len(compressed_data) < len(json_data):
            # For HIGH compression level, apply additional zlib compression
            if self.compression_level == CompressionLevel.HIGH:
                # Apply a higher zlib compression level
                compressed_data = zlib.compress(compressed_data, 9)
            return compressed_data
        else:
            # Fall back to JSON if compression didn't help, but still apply zlib for HIGH
            if self.compression_level == CompressionLevel.HIGH:
                return zlib.compress(json_data, 9)
            return json_data
    
    def decompress_changes(self, 
                          table_name: str, 
                          data: bytes) -> List[Dict[str, Any]]:
        """
        Decompress a list of changes.
        
        Args:
            table_name: Name of the table
            data: Compressed changes data
            
        Returns:
            Decompressed list of changes
        """
        # First try to handle HIGH compression level (zlib)
        if self.compression_level == CompressionLevel.HIGH:
            try:
                # Try to decompress with zlib first
                decompressed_data = zlib.decompress(data)
                
                # Then try to decompress as a list
                try:
                    return self.common_compressor.decompress(CompressionFormat.LIST, decompressed_data)
                except Exception:
                    # Fall back to JSON if that fails
                    try:
                        return json.loads(decompressed_data.decode('utf-8'))
                    except Exception:
                        # If decompressed data isn't JSON, continue to regular process
                        pass
            except zlib.error:
                # Not zlib compressed, continue to regular process
                pass
        
        # Regular decompression process
        try:
            return self.common_compressor.decompress(CompressionFormat.LIST, data)
        except Exception:
            # Fall back to JSON if that fails
            try:
                return json.loads(data.decode('utf-8'))
            except Exception:
                # Last resort: try json decompression
                return decompress_json(data)
    
    def set_compression_level(self, level: CompressionLevel) -> None:
        """Set the compression level."""
        self.compression_level = level
        self.zlib_level = _compression_level_to_zlib(level)
        
        # Update the common compressor's compression level
        self.common_compressor = TypeAwareCompressor(self.zlib_level)
        
        # For backward compatibility
        self.compressor_factory.set_compression_level(level)
    
    def set_schema(self, schema: Dict[str, Dict[str, Type]]) -> None:
        """Set the schema for type-aware compression."""
        self.schema = schema