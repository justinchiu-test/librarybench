"""Tests for payload compression and performance benchmarks."""

import pytest
import json
import random
import string
import time
from typing import Dict, Any, List, Tuple

from in_memory_database_mobile_app_developer.compression import (
    CompressionEngine, PREDEFINED_PROFILES, CompressionAlgorithm, CompressionLevel,
    SyncPayloadCompressor, DataType
)
from in_memory_database_mobile_app_developer.database import MobileDBEngine, Record
from in_memory_database_mobile_app_developer.sync import SyncBatch


@pytest.fixture
def compression_engine() -> CompressionEngine:
    """Create a compression engine for testing."""
    return CompressionEngine()


@pytest.fixture
def sync_payload_compressor(compression_engine: CompressionEngine) -> SyncPayloadCompressor:
    """Create a sync payload compressor for testing."""
    return SyncPayloadCompressor(compression_engine)


@pytest.fixture
def test_data() -> Dict[str, Any]:
    """Generate test data for compression benchmarks."""
    # Text data
    text_data = {
        "short_text": "Hello, world!",
        "medium_text": "".join(random.choice(string.ascii_letters) for _ in range(1000)),
        "long_text": "".join(random.choice(string.ascii_letters) for _ in range(10000)),
    }
    
    # Numeric data
    numeric_data = {
        "integers": [random.randint(0, 1000000) for _ in range(1000)],
        "floats": [random.random() * 1000 for _ in range(1000)],
    }
    
    # JSON data
    json_data = {
        "small_object": {
            "id": "123",
            "name": "Test Object",
            "properties": {"color": "blue", "size": "medium"},
        },
        "medium_object": {
            "id": "456",
            "name": "Medium Object",
            "items": [{"id": i, "value": f"Item {i}"} for i in range(100)],
            "metadata": {f"key_{i}": f"value_{i}" for i in range(100)},
        },
        "large_object": {
            "id": "789",
            "name": "Large Object",
            "matrix": [[random.random() for _ in range(50)] for _ in range(50)],
            "tags": [f"tag_{i}" for i in range(1000)],
            "details": {f"detail_{i}": random.choice(["a", "b", "c", "d", "e"]) for i in range(1000)},
        },
    }
    
    # Binary data
    binary_data = {
        "small_binary": bytes([random.randint(0, 255) for _ in range(100)]),
        "medium_binary": bytes([random.randint(0, 255) for _ in range(5000)]),
        "large_binary": bytes([random.randint(0, 255) for _ in range(20000)]),
    }
    
    return {
        "text": text_data,
        "numeric": numeric_data,
        "json": json_data,
        "binary": binary_data,
    }


@pytest.fixture
def sync_test_data(test_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate test data for sync batch compression."""
    # Create records
    records = []
    
    # Small record
    small_record = Record(
        data={
            "id": "small_record",
            "name": "Small Record",
            "description": test_data["text"]["short_text"],
            "value": random.randint(1, 100),
            "properties": test_data["json"]["small_object"],
        },
        created_at=time.time() - 3600,
        updated_at=time.time() - 1800,
        version=1,
        client_id="client1",
    )
    records.append(("small_record", small_record))
    
    # Medium record
    medium_record = Record(
        data={
            "id": "medium_record",
            "name": "Medium Record",
            "description": test_data["text"]["medium_text"][:500],
            "values": [random.randint(1, 1000) for _ in range(50)],
            "properties": test_data["json"]["medium_object"],
        },
        created_at=time.time() - 3600,
        updated_at=time.time() - 1800,
        version=1,
        client_id="client1",
    )
    records.append(("medium_record", medium_record))
    
    # Large record
    large_record = Record(
        data={
            "id": "large_record",
            "name": "Large Record",
            "description": test_data["text"]["long_text"][:1000],
            "values": [random.random() * 1000 for _ in range(200)],
            "properties": test_data["json"]["large_object"],
            "binary_data": test_data["binary"]["medium_binary"].decode('latin1'),  # Convert to string for JSON
        },
        created_at=time.time() - 3600,
        updated_at=time.time() - 1800,
        version=1,
        client_id="client1",
    )
    records.append(("large_record", large_record))
    
    # Create batch
    batch = SyncBatch(
        table_name="test_table",
        records=records,
        is_last_batch=True,
    )
    
    return {
        "batch": batch,
        "batch_dict": batch.to_dict(),
    }


def test_compression_profiles() -> None:
    """Test the predefined compression profiles."""
    engine = CompressionEngine()
    
    # Test each predefined profile
    for profile_name in PREDEFINED_PROFILES:
        profile = engine.get_profile(profile_name)
        assert profile.name == profile_name
        
        # Ensure profile serialization works
        profile_dict = profile.to_dict()
        assert profile_dict["name"] == profile_name
        assert profile_dict["algorithm"] == profile.algorithm.value
        assert profile_dict["level"] == profile.level.value


def test_data_type_detection(compression_engine: CompressionEngine, test_data: Dict[str, Any]) -> None:
    """Test data type detection."""
    # Test text detection
    assert compression_engine.detect_data_type(test_data["text"]["short_text"]) == DataType.TEXT.value
    assert compression_engine.detect_data_type(test_data["text"]["medium_text"]) == DataType.TEXT.value
    
    # Test numeric detection
    assert compression_engine.detect_data_type(123) == DataType.NUMERIC.value
    assert compression_engine.detect_data_type(123.45) == DataType.NUMERIC.value
    
    # Test JSON detection
    assert compression_engine.detect_data_type(test_data["json"]["small_object"]) == DataType.JSON.value
    assert compression_engine.detect_data_type(json.dumps(test_data["json"]["small_object"])) == DataType.JSON.value
    
    # Test binary detection
    assert compression_engine.detect_data_type(test_data["binary"]["small_binary"]) == DataType.BINARY.value


def test_basic_compression(compression_engine: CompressionEngine, test_data: Dict[str, Any]) -> None:
    """Test basic compression functionality."""
    # Compress text data
    compressed_text = compression_engine.compress(test_data["text"]["medium_text"])
    assert compressed_text["data_type"] == DataType.TEXT.value
    assert compressed_text["original_size"] > compressed_text["compressed_size"]
    
    # Compress JSON data
    compressed_json = compression_engine.compress(test_data["json"]["medium_object"])
    assert compressed_json["data_type"] == DataType.JSON.value
    assert compressed_json["original_size"] > compressed_json["compressed_size"]
    
    # Compress binary data
    compressed_binary = compression_engine.compress(test_data["binary"]["medium_binary"])
    assert compressed_binary["data_type"] == DataType.BINARY.value
    assert compressed_binary["original_size"] > compressed_binary["compressed_size"]
    
    # Compress numeric data
    compressed_numeric = compression_engine.compress(test_data["numeric"]["integers"])
    assert compressed_numeric["data_type"] == DataType.JSON.value  # List of integers is treated as JSON
    assert compressed_numeric["original_size"] > compressed_numeric["compressed_size"]


def test_compression_decompression_roundtrip(compression_engine: CompressionEngine, test_data: Dict[str, Any]) -> None:
    """Test compression and decompression roundtrip."""
    for data_category, data_items in test_data.items():
        for data_name, data_value in data_items.items():
            # Skip very large data for basic roundtrip test
            if "large" in data_name:
                continue
            
            # Compress the data
            compressed = compression_engine.compress(data_value)
            
            # Decompress the data
            decompressed = compression_engine.decompress(compressed)
            
            # For binary data, compare bytes directly
            if data_category == "binary":
                assert decompressed == data_value
            # For lists and dicts, compare structures
            elif isinstance(data_value, (list, dict)):
                assert decompressed == data_value
            # For simple types, compare values
            else:
                assert decompressed == data_value


def test_sync_batch_compression(
    sync_payload_compressor: SyncPayloadCompressor,
    sync_test_data: Dict[str, Any]
) -> None:
    """Test compressing and decompressing a sync batch."""
    # Compress the batch
    batch_dict = sync_test_data["batch_dict"]
    compressed_batch = sync_payload_compressor.compress_sync_batch(batch_dict)
    
    # Check that compression happened
    assert "compression_profile" in compressed_batch
    assert "records" in compressed_batch
    assert len(compressed_batch["records"]) == len(batch_dict["records"])
    
    # Check that records were compressed
    for record in compressed_batch["records"]:
        assert "compressed_data" in record
        assert "data" not in record  # Original data replaced with compressed version
    
    # Decompress the batch
    decompressed_batch = sync_payload_compressor.decompress_sync_batch(compressed_batch)
    
    # Check that decompression returned the original batch structure
    assert decompressed_batch["batch_id"] == batch_dict["batch_id"]
    assert decompressed_batch["table_name"] == batch_dict["table_name"]
    assert len(decompressed_batch["records"]) == len(batch_dict["records"])
    
    # Verify record data was properly decompressed
    for orig_record, decomp_record in zip(batch_dict["records"], decompressed_batch["records"]):
        assert decomp_record["pk"] == orig_record["pk"]
        assert decomp_record["data"]["id"] == orig_record["data"]["id"]
        assert decomp_record["data"]["name"] == orig_record["data"]["name"]


@pytest.mark.parametrize("profile_name", ["high_compression", "balanced", "fast", "no_compression"])
def test_compression_profiles_performance(
    compression_engine: CompressionEngine,
    test_data: Dict[str, Any],
    profile_name: str
) -> None:
    """Test performance of different compression profiles."""
    # Reset statistics
    compression_engine.reset_statistics()
    
    # Compress large text with the profile
    start_time = time.time()
    compressed = compression_engine.compress(test_data["text"]["long_text"], profile_name)
    compression_time = time.time() - start_time
    
    # Decompress the data
    start_time = time.time()
    _ = compression_engine.decompress(compressed)
    decompression_time = time.time() - start_time
    
    # Log performance data
    print(f"\n=== Profile: {profile_name} ===")
    print(f"Compression ratio: {compressed['compression_ratio']:.4f}")
    print(f"Compression time: {compression_time:.6f} seconds")
    print(f"Decompression time: {decompression_time:.6f} seconds")
    
    # For high_compression, verify it achieves better compression ratio
    if profile_name == "high_compression":
        # Try balanced for comparison
        balanced = compression_engine.compress(test_data["text"]["long_text"], "balanced")
        assert compressed["compression_ratio"] < balanced["compression_ratio"]
    
    # For fast, verify it's faster than high_compression
    if profile_name == "fast":
        # Compress with high_compression for comparison
        start_time = time.time()
        _ = compression_engine.compress(test_data["text"]["long_text"], "high_compression")
        high_comp_time = time.time() - start_time
        
        # Fast should be faster than high_compression
        assert compression_time < high_comp_time
    
    # For no_compression, verify no actual compression happened
    if profile_name == "no_compression":
        assert compressed["compression_ratio"] == 1.0


@pytest.mark.parametrize("data_type", ["text", "json", "binary"])
def test_compression_by_data_type(
    compression_engine: CompressionEngine,
    test_data: Dict[str, Any],
    data_type: str
) -> None:
    """Test compression effectiveness for different data types."""
    # Reset statistics
    compression_engine.reset_statistics()
    
    data_value = None
    if data_type == "text":
        data_value = test_data["text"]["long_text"]
    elif data_type == "json":
        data_value = test_data["json"]["large_object"]
    elif data_type == "binary":
        data_value = test_data["binary"]["large_binary"]
    
    # Compress with different profiles
    results = {}
    for profile_name in ["high_compression", "balanced", "fast"]:
        compressed = compression_engine.compress(data_value, profile_name)
        results[profile_name] = {
            "ratio": compressed["compression_ratio"],
            "original_size": compressed["original_size"],
            "compressed_size": compressed["compressed_size"],
        }
    
    # Log comparison data
    print(f"\n=== Data Type: {data_type} ===")
    for profile, stats in results.items():
        print(f"{profile}: {stats['ratio']:.4f} ratio, {stats['compressed_size']:,} bytes")
    
    # Assert reasonable compression for each data type
    # Note: These thresholds may need adjustment based on actual compression performance
    best_ratio = min(result["ratio"] for result in results.values())
    if data_type == "text":
        assert best_ratio < 0.5, f"Text compression ratio {best_ratio} exceeds threshold"
    elif data_type == "json":
        assert best_ratio < 0.6, f"JSON compression ratio {best_ratio} exceeds threshold"
    elif data_type == "binary":
        # Binary data is often less compressible, especially if already compressed or random
        assert best_ratio < 0.9, f"Binary compression ratio {best_ratio} exceeds threshold"


def test_dict_compression(compression_engine: CompressionEngine, test_data: Dict[str, Any]) -> None:
    """Test compressing and decompressing dictionaries with different field types."""
    # Create a mixed dict with different types of fields
    mixed_dict = {
        "text_field": test_data["text"]["medium_text"][:500],
        "numeric_field": random.randint(1, 1000000),
        "json_field": test_data["json"]["medium_object"],
        "binary_field_str": test_data["binary"]["small_binary"].decode('latin1'),  # As string
        "list_field": test_data["numeric"]["integers"][:100],
    }
    
    # Compress the dict
    compressed_dict = compression_engine.compress_dict(mixed_dict)
    
    # Check structure
    assert "data" in compressed_dict
    assert "metadata" in compressed_dict
    
    # Check that each field has metadata
    for field in mixed_dict:
        assert field in compressed_dict["metadata"]
        assert "algorithm" in compressed_dict["metadata"][field]
        assert "data_type" in compressed_dict["metadata"][field]
        assert "original_size" in compressed_dict["metadata"][field]
        assert "compressed_size" in compressed_dict["metadata"][field]
    
    # Decompress the dict
    decompressed_dict = compression_engine.decompress_dict(compressed_dict)
    
    # Verify the decompressed dict matches the original
    for field, value in mixed_dict.items():
        assert field in decompressed_dict
        if isinstance(value, (dict, list)):
            assert decompressed_dict[field] == value
        else:
            assert decompressed_dict[field] == value


def test_compression_statistics(compression_engine: CompressionEngine, test_data: Dict[str, Any]) -> None:
    """Test compression statistics collection."""
    # Reset statistics
    compression_engine.reset_statistics()
    
    # Compress different types of data
    compression_engine.compress(test_data["text"]["medium_text"])
    compression_engine.compress(test_data["json"]["medium_object"])
    compression_engine.compress(test_data["binary"]["medium_binary"])
    
    # Get statistics
    stats = compression_engine.get_statistics()
    
    # Check overall stats
    assert stats["compression_count"] == 3
    assert stats["total_original_size"] > 0
    assert stats["total_compressed_size"] > 0
    assert stats["overall_ratio"] < 1.0  # Should achieve some compression
    
    # Check per-type stats
    assert DataType.TEXT.value in stats["by_type"]
    assert stats["by_type"][DataType.TEXT.value]["count"] == 1
    assert stats["by_type"][DataType.TEXT.value]["ratio"] < 1.0
    
    assert DataType.JSON.value in stats["by_type"]
    assert stats["by_type"][DataType.JSON.value]["count"] == 1
    assert stats["by_type"][DataType.JSON.value]["ratio"] < 1.0
    
    assert DataType.BINARY.value in stats["by_type"]
    assert stats["by_type"][DataType.BINARY.value]["count"] == 1
    
    # Reset and verify
    compression_engine.reset_statistics()
    new_stats = compression_engine.get_statistics()
    assert new_stats["compression_count"] == 0
    assert new_stats["total_original_size"] == 0