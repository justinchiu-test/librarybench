"""Payload compression for MobileSyncDB."""

import json
import zlib
import lz4.frame
import msgpack
import zstandard as zstd
import base64
from enum import Enum
from typing import Dict, Any, List, Optional, Union, Tuple, Callable, ByteString

from .exceptions import CompressionError


class CompressionAlgorithm(Enum):
    """Available compression algorithms."""

    ZLIB = "zlib"
    LZ4 = "lz4"
    ZSTD = "zstd"
    NONE = "none"


class CompressionLevel(Enum):
    """Compression levels balancing CPU usage vs compression ratio."""

    HIGH = "high"  # Best compression ratio, highest CPU usage
    BALANCED = "balanced"  # Good balance between ratio and CPU
    LOW = "low"  # Fastest, but lower compression ratio
    NONE = "none"  # No compression


class DataType(Enum):
    """Data types for specialized compression."""

    TEXT = "text"
    NUMERIC = "numeric"
    BINARY = "binary"
    JSON = "json"
    MIXED = "mixed"


class CompressionProfile:
    """Defines a compression profile with specific settings."""

    def __init__(
        self,
        name: str,
        algorithm: CompressionAlgorithm,
        level: CompressionLevel,
        type_specific: bool = True,
        description: Optional[str] = None,
    ):
        """Initialize a compression profile."""
        self.name = name
        self.algorithm = algorithm
        self.level = level
        self.type_specific = type_specific
        self.description = description or f"{name} ({algorithm.value} - {level.value})"

    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary for serialization."""
        return {
            "name": self.name,
            "algorithm": self.algorithm.value,
            "level": self.level.value,
            "type_specific": self.type_specific,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CompressionProfile":
        """Create a profile from a dictionary."""
        return cls(
            name=data["name"],
            algorithm=CompressionAlgorithm(data["algorithm"]),
            level=CompressionLevel(data["level"]),
            type_specific=data.get("type_specific", True),
            description=data.get("description"),
        )


# Standard compression profiles
PREDEFINED_PROFILES = {
    "high_compression": CompressionProfile(
        name="high_compression",
        algorithm=CompressionAlgorithm.ZSTD,
        level=CompressionLevel.HIGH,
        description="Maximum compression ratio for slow connections",
    ),
    "balanced": CompressionProfile(
        name="balanced",
        algorithm=CompressionAlgorithm.ZSTD,
        level=CompressionLevel.BALANCED,
        description="Good balance between compression and CPU usage",
    ),
    "fast": CompressionProfile(
        name="fast",
        algorithm=CompressionAlgorithm.LZ4,
        level=CompressionLevel.LOW,
        description="Fast compression for better battery life",
    ),
    "no_compression": CompressionProfile(
        name="no_compression",
        algorithm=CompressionAlgorithm.NONE,
        level=CompressionLevel.NONE,
        description="No compression for minimal CPU impact",
    ),
}


class CompressionStatistics:
    """Collects statistics about compression performance."""

    def __init__(self):
        """Initialize compression statistics."""
        self.total_original_size = 0
        self.total_compressed_size = 0
        self.compression_count = 0
        self.decompression_count = 0
        self.compression_time_ms = 0.0
        self.decompression_time_ms = 0.0
        self.by_type: Dict[str, Dict[str, Any]] = {}
        for dtype in DataType:
            self.by_type[dtype.value] = {
                "original_size": 0,
                "compressed_size": 0,
                "count": 0,
                "ratio": 0.0,
            }

    def add_compression_result(
        self,
        data_type: str,
        original_size: int,
        compressed_size: int,
        time_ms: float,
    ) -> None:
        """Add a compression result to the statistics."""
        self.total_original_size += original_size
        self.total_compressed_size += compressed_size
        self.compression_count += 1
        self.compression_time_ms += time_ms
        
        if data_type in self.by_type:
            self.by_type[data_type]["original_size"] += original_size
            self.by_type[data_type]["compressed_size"] += compressed_size
            self.by_type[data_type]["count"] += 1
            if self.by_type[data_type]["original_size"] > 0:
                self.by_type[data_type]["ratio"] = (
                    self.by_type[data_type]["compressed_size"] /
                    self.by_type[data_type]["original_size"]
                )

    def add_decompression_result(self, time_ms: float) -> None:
        """Add a decompression result to the statistics."""
        self.decompression_count += 1
        self.decompression_time_ms += time_ms

    def get_overall_ratio(self) -> float:
        """Get the overall compression ratio."""
        if self.total_original_size == 0:
            return 1.0
        return self.total_compressed_size / self.total_original_size

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of compression statistics."""
        avg_compression_time = (
            self.compression_time_ms / self.compression_count
            if self.compression_count > 0
            else 0
        )
        avg_decompression_time = (
            self.decompression_time_ms / self.decompression_count
            if self.decompression_count > 0
            else 0
        )
        
        return {
            "total_original_size": self.total_original_size,
            "total_compressed_size": self.total_compressed_size,
            "overall_ratio": self.get_overall_ratio(),
            "compression_count": self.compression_count,
            "decompression_count": self.decompression_count,
            "avg_compression_time_ms": avg_compression_time,
            "avg_decompression_time_ms": avg_decompression_time,
            "by_type": self.by_type,
        }

    def reset(self) -> None:
        """Reset all statistics."""
        self.__init__()


class CompressionEngine:
    """Handles data compression and decompression for sync operations."""

    def __init__(self, default_profile_name: str = "balanced"):
        """Initialize the compression engine."""
        self.profiles = PREDEFINED_PROFILES.copy()
        self.default_profile_name = default_profile_name
        self.stats = CompressionStatistics()
        self.type_detectors: Dict[str, Callable[[Any], bool]] = {
            DataType.TEXT.value: lambda x: isinstance(x, str) and not x.startswith('{') and not x.startswith('['),
            DataType.NUMERIC.value: lambda x: isinstance(x, (int, float)),
            DataType.JSON.value: lambda x: (isinstance(x, str) and (x.startswith('{') or x.startswith('['))) or isinstance(x, (dict, list)),
            DataType.BINARY.value: lambda x: isinstance(x, (bytes, bytearray, memoryview)),
        }

    def add_profile(self, profile: CompressionProfile) -> None:
        """Add a new compression profile."""
        self.profiles[profile.name] = profile

    def get_profile(self, profile_name: Optional[str] = None) -> CompressionProfile:
        """Get a compression profile by name."""
        name = profile_name or self.default_profile_name
        if name not in self.profiles:
            raise CompressionError(f"Compression profile '{name}' not found")
        return self.profiles[name]

    def detect_data_type(self, data: Any) -> str:
        """Detect the type of data for specialized compression."""
        for dtype, detector in self.type_detectors.items():
            if detector(data):
                return dtype
        return DataType.MIXED.value

    def _get_algorithm_settings(
        self,
        algorithm: CompressionAlgorithm,
        level: CompressionLevel,
    ) -> Dict[str, Any]:
        """Get the settings for a compression algorithm."""
        if algorithm == CompressionAlgorithm.ZLIB:
            # Zlib compression level: 1-9, where 9 is highest compression
            if level == CompressionLevel.HIGH:
                return {"level": 9}
            elif level == CompressionLevel.BALANCED:
                return {"level": 6}
            elif level == CompressionLevel.LOW:
                return {"level": 1}
            else:
                return {"level": 0}
        
        elif algorithm == CompressionAlgorithm.LZ4:
            # LZ4 compression level: 0-16, where 16 is highest compression
            if level == CompressionLevel.HIGH:
                return {"compression_level": 16}
            elif level == CompressionLevel.BALANCED:
                return {"compression_level": 9}
            elif level == CompressionLevel.LOW:
                return {"compression_level": 1}
            else:
                return {"compression_level": 0}
        
        elif algorithm == CompressionAlgorithm.ZSTD:
            # Zstandard compression level: 1-22, where 22 is highest compression
            if level == CompressionLevel.HIGH:
                return {"level": 19}
            elif level == CompressionLevel.BALANCED:
                return {"level": 10}
            elif level == CompressionLevel.LOW:
                return {"level": 3}
            else:
                return {"level": 1}
        
        elif algorithm == CompressionAlgorithm.NONE:
            return {}
        
        raise CompressionError(f"Unknown compression algorithm: {algorithm}")

    def _compress_data(
        self,
        data: bytes,
        algorithm: CompressionAlgorithm,
        settings: Dict[str, Any],
    ) -> bytes:
        """Compress data using the specified algorithm and settings."""
        try:
            if algorithm == CompressionAlgorithm.ZLIB:
                level = settings.get("level", 6)
                return zlib.compress(data, level)
            
            elif algorithm == CompressionAlgorithm.LZ4:
                compression_level = settings.get("compression_level", 9)
                return lz4.frame.compress(data, compression_level=compression_level)
            
            elif algorithm == CompressionAlgorithm.ZSTD:
                level = settings.get("level", 10)
                compressor = zstd.ZstdCompressor(level=level)
                return compressor.compress(data)
            
            elif algorithm == CompressionAlgorithm.NONE:
                return data
            
            raise CompressionError(f"Unknown compression algorithm: {algorithm}")
        
        except Exception as e:
            raise CompressionError(f"Compression error with {algorithm.value}: {str(e)}")

    def _decompress_data(
        self,
        data: bytes,
        algorithm: CompressionAlgorithm,
    ) -> bytes:
        """Decompress data using the specified algorithm."""
        try:
            if algorithm == CompressionAlgorithm.ZLIB:
                return zlib.decompress(data)
            
            elif algorithm == CompressionAlgorithm.LZ4:
                return lz4.frame.decompress(data)
            
            elif algorithm == CompressionAlgorithm.ZSTD:
                decompressor = zstd.ZstdDecompressor()
                return decompressor.decompress(data)
            
            elif algorithm == CompressionAlgorithm.NONE:
                return data
            
            raise CompressionError(f"Unknown compression algorithm: {algorithm}")
        
        except Exception as e:
            raise CompressionError(f"Decompression error with {algorithm.value}: {str(e)}")

    def _serialize_data(self, data: Any) -> Tuple[bytes, str]:
        """Serialize data to bytes based on its type."""
        data_type = self.detect_data_type(data)
        
        try:
            if data_type == DataType.BINARY.value:
                return data if isinstance(data, bytes) else bytes(data), data_type
            
            elif data_type == DataType.JSON.value:
                if isinstance(data, (dict, list)):
                    return msgpack.packb(data), data_type
                else:
                    # Parse JSON string to object, then serialize with msgpack
                    return msgpack.packb(json.loads(data)), data_type
            
            elif data_type == DataType.TEXT.value:
                return data.encode('utf-8'), data_type
            
            elif data_type == DataType.NUMERIC.value:
                return str(data).encode('utf-8'), data_type
            
            else:  # MIXED
                return msgpack.packb(data), data_type
        
        except Exception as e:
            raise CompressionError(f"Serialization error for {data_type}: {str(e)}")

    def _deserialize_data(self, data: bytes, data_type: str) -> Any:
        """Deserialize bytes to original data based on its type."""
        try:
            if data_type == DataType.BINARY.value:
                return data
            
            elif data_type == DataType.JSON.value:
                return msgpack.unpackb(data)
            
            elif data_type == DataType.TEXT.value:
                return data.decode('utf-8')
            
            elif data_type == DataType.NUMERIC.value:
                try:
                    return int(data.decode('utf-8'))
                except ValueError:
                    return float(data.decode('utf-8'))
            
            else:  # MIXED
                return msgpack.unpackb(data)
        
        except Exception as e:
            raise CompressionError(f"Deserialization error for {data_type}: {str(e)}")

    def compress(
        self,
        data: Any,
        profile_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Compress data using the specified or default profile."""
        import time
        
        profile = self.get_profile(profile_name)
        
        # Skip compression if using NONE algorithm
        if profile.algorithm == CompressionAlgorithm.NONE:
            if isinstance(data, (bytes, bytearray)):
                serialized = data
                data_type = DataType.BINARY.value
            else:
                serialized, data_type = self._serialize_data(data)
            
            return {
                "compressed_data": base64.b64encode(serialized).decode('utf-8'),
                "algorithm": profile.algorithm.value,
                "data_type": data_type,
                "original_size": len(serialized),
                "compressed_size": len(serialized),
                "compression_ratio": 1.0,
            }
        
        # Serialize data to bytes
        start_time = time.time()
        serialized, data_type = self._serialize_data(data)
        original_size = len(serialized)
        
        # Get algorithm settings
        settings = self._get_algorithm_settings(profile.algorithm, profile.level)
        
        # Compress data
        compressed = self._compress_data(serialized, profile.algorithm, settings)
        compressed_size = len(compressed)
        
        # Calculate compression ratio and time
        ratio = compressed_size / original_size if original_size > 0 else 1.0
        end_time = time.time()
        compression_time_ms = (end_time - start_time) * 1000
        
        # Update statistics
        self.stats.add_compression_result(
            data_type=data_type,
            original_size=original_size,
            compressed_size=compressed_size,
            time_ms=compression_time_ms,
        )
        
        # Base64 encode for safe transport
        encoded = base64.b64encode(compressed).decode('utf-8')
        
        return {
            "compressed_data": encoded,
            "algorithm": profile.algorithm.value,
            "data_type": data_type,
            "original_size": original_size,
            "compressed_size": compressed_size,
            "compression_ratio": ratio,
        }

    def decompress(self, compressed_info: Dict[str, Any]) -> Any:
        """Decompress data from a compressed info dictionary."""
        import time
        
        # Extract information from the compressed info
        encoded = compressed_info["compressed_data"]
        algorithm_name = compressed_info["algorithm"]
        data_type = compressed_info["data_type"]
        
        # Skip decompression if no compression was applied
        if algorithm_name == CompressionAlgorithm.NONE.value:
            compressed = base64.b64decode(encoded)
            return self._deserialize_data(compressed, data_type)
        
        # Decode base64
        compressed = base64.b64decode(encoded)
        
        # Get algorithm
        algorithm = CompressionAlgorithm(algorithm_name)
        
        # Decompress data
        start_time = time.time()
        decompressed = self._decompress_data(compressed, algorithm)
        
        # Deserialize data
        result = self._deserialize_data(decompressed, data_type)
        
        # Update statistics
        end_time = time.time()
        decompression_time_ms = (end_time - start_time) * 1000
        self.stats.add_decompression_result(decompression_time_ms)
        
        return result

    def compress_dict(
        self,
        data: Dict[str, Any],
        profile_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Compress a dictionary, handling each field separately for optimal compression."""
        result = {}
        metadata = {}
        
        for key, value in data.items():
            compressed_info = self.compress(value, profile_name)
            result[key] = compressed_info["compressed_data"]
            metadata[key] = {
                "algorithm": compressed_info["algorithm"],
                "data_type": compressed_info["data_type"],
                "original_size": compressed_info["original_size"],
                "compressed_size": compressed_info["compressed_size"],
            }
        
        return {
            "data": result,
            "metadata": metadata,
        }

    def decompress_dict(self, compressed_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Decompress a dictionary that was compressed with compress_dict."""
        data = compressed_dict["data"]
        metadata = compressed_dict["metadata"]
        result = {}
        
        for key, value in data.items():
            field_meta = metadata[key]
            compressed_info = {
                "compressed_data": value,
                "algorithm": field_meta["algorithm"],
                "data_type": field_meta["data_type"],
            }
            result[key] = self.decompress(compressed_info)
        
        return result

    def get_statistics(self) -> Dict[str, Any]:
        """Get compression statistics."""
        return self.stats.get_summary()

    def reset_statistics(self) -> None:
        """Reset compression statistics."""
        self.stats.reset()


class SyncPayloadCompressor:
    """Compresses and decompresses sync payloads for network transfer."""

    def __init__(self, compression_engine: CompressionEngine):
        """Initialize the sync payload compressor."""
        self.engine = compression_engine

    def compress_sync_batch(
        self,
        batch_dict: Dict[str, Any],
        profile_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Compress a sync batch for network transfer."""
        # Separate metadata from records
        metadata = {
            "batch_id": batch_dict["batch_id"],
            "table_name": batch_dict["table_name"],
            "created_at": batch_dict["created_at"],
            "is_last_batch": batch_dict["is_last_batch"],
            "checksum": batch_dict["checksum"],
        }
        
        # Compress records data
        records_compressed = []
        for record in batch_dict["records"]:
            # Compress the record data dict
            compressed_data = self.engine.compress_dict(record["data"], profile_name)
            
            # Create compressed record
            compressed_record = {
                "pk": record["pk"],
                "compressed_data": compressed_data,
                "version": record["version"],
                "updated_at": record["updated_at"],
                "created_at": record["created_at"],
                "is_deleted": record.get("is_deleted", False),
                "client_id": record.get("client_id"),
                "conflict_info": record.get("conflict_info"),
            }
            records_compressed.append(compressed_record)
        
        # Build final compressed batch
        compressed_batch = metadata.copy()
        compressed_batch["records"] = records_compressed
        
        # Get compression profile for metadata
        profile = self.engine.get_profile(profile_name)
        compressed_batch["compression_profile"] = profile.to_dict()
        
        return compressed_batch

    def decompress_sync_batch(self, compressed_batch: Dict[str, Any]) -> Dict[str, Any]:
        """Decompress a sync batch for processing."""
        # Extract metadata
        metadata = {
            "batch_id": compressed_batch["batch_id"],
            "table_name": compressed_batch["table_name"],
            "created_at": compressed_batch["created_at"],
            "is_last_batch": compressed_batch["is_last_batch"],
            "checksum": compressed_batch["checksum"],
        }
        
        # Decompress records
        records_decompressed = []
        for record in compressed_batch["records"]:
            # Decompress the record data
            decompressed_data = self.engine.decompress_dict(record["compressed_data"])
            
            # Create decompressed record
            decompressed_record = {
                "pk": record["pk"],
                "data": decompressed_data,
                "version": record["version"],
                "updated_at": record["updated_at"],
                "created_at": record["created_at"],
                "is_deleted": record.get("is_deleted", False),
                "client_id": record.get("client_id"),
                "conflict_info": record.get("conflict_info"),
            }
            records_decompressed.append(decompressed_record)
        
        # Build final decompressed batch
        decompressed_batch = metadata.copy()
        decompressed_batch["records"] = records_decompressed
        
        return decompressed_batch