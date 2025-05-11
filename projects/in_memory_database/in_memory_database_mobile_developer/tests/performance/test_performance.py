"""
Performance tests for the SyncDB system.
"""
import pytest
import time
import json
import random
import string
from typing import Dict, List, Any, Optional, Tuple

from syncdb.db.schema import DatabaseSchema, TableSchema, Column
from syncdb.db.database import Database
from syncdb.sync.change_tracker import ChangeTracker
from syncdb.sync.sync_protocol import SyncEngine, NetworkSimulator
from syncdb.compression.type_compressor import (
    PayloadCompressor, CompressionLevel
)
from syncdb.power.power_manager import (
    PowerManager, PowerMode, PowerProfile, OperationPriority,
    BatteryAwareClient
)
from syncdb.sync.conflict_resolution import (
    MergeFieldsResolver
)
from syncdb.client import SyncClient, SyncServer


# Helper functions for generating test data
def generate_random_string(length: int) -> str:
    """Generate a random string of specified length."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_random_record(id: int, size: int = 100) -> Dict[str, Any]:
    """Generate a random record with the specified ID and approximate size."""
    return {
        "id": id,
        "username": generate_random_string(10),
        "email": f"{generate_random_string(8)}@example.com",
        "description": generate_random_string(size - 50),  # Adjust to meet size target
        "created_at": time.time(),
        "active": random.choice([True, False]),
        "preferences": {
            "theme": random.choice(["light", "dark", "auto"]),
            "notifications": random.choice([True, False]),
            "language": random.choice(["en", "es", "fr", "de", "zh"])
        },
        "tags": [generate_random_string(5) for _ in range(random.randint(1, 5))]
    }


def create_large_schema():
    """Create a schema for performance testing."""
    # User table
    user_columns = [
        Column("id", int, primary_key=True),
        Column("username", str),
        Column("email", str),
        Column("description", str, nullable=True),
        Column("created_at", float, default=time.time),
        Column("active", bool, default=True),
        Column("preferences", dict, nullable=True),
        Column("tags", list, nullable=True)
    ]
    user_table = TableSchema("users", user_columns)
    
    # Large data table
    data_columns = [
        Column("id", int, primary_key=True),
        Column("user_id", int),
        Column("title", str),
        Column("content", str),
        Column("metadata", dict, nullable=True),
        Column("created_at", float, default=time.time),
        Column("updated_at", float, default=time.time)
    ]
    data_table = TableSchema("data", data_columns)
    
    # Create the database schema
    tables = {
        "users": user_table,
        "data": data_table
    }
    schema = DatabaseSchema(tables, version=1)
    
    return schema


def create_test_client_server(record_count: int, record_size: int):
    """Create a test client and server with the specified data volume."""
    # Create the schema
    schema = create_large_schema()
    
    # Create server
    server = SyncServer(schema)
    
    # Add test data to the server
    for i in range(record_count):
        server.insert("users", generate_random_record(i, record_size))
    
    # Create client
    client = SyncClient(
        schema=schema,
        client_id="perf_test_client",
        power_aware=False  # Disable power management for testing
    )
    
    # Connect client to server
    client.server_url = "mock://server"
    client.sync_engine = server.sync_engine
    client.server_connected = True
    
    # Register the client with the server
    server.register_client(client.client_id)
    
    return client, server


@pytest.mark.parametrize("mode", [
    PowerMode.PLUGGED_IN,
    PowerMode.BATTERY_NORMAL,
    PowerMode.BATTERY_LOW,
    PowerMode.BATTERY_CRITICAL
])
def test_battery_mode_performance(mode):
    """Test the performance impact of different battery modes."""
    # Create a client and server
    client, server = create_test_client_server(100, 500)
    
    # Create a power manager
    manager = PowerManager(mode)
    
    # Create a battery-aware client
    battery_client = BatteryAwareClient(client, manager)
    
    # Define a workload of operations
    operations = [
        ("insert", {"id": 1000, "username": "perf_test", "email": "perf@example.com"}),
        ("update", {"id": 1000, "username": "perf_test_updated", "email": "perf@example.com"}),
        ("query", {"user_id": 1}),
        ("get", [1000]),
        ("delete", [1000])
    ]
    
    # Time the execution of the workload
    start_time = time.time()
    
    for op_type, params in operations:
        if op_type == "insert":
            battery_client.insert("users", params)
        elif op_type == "update":
            battery_client.update("users", params)
        elif op_type == "query":
            battery_client.query("users", params)
        elif op_type == "get":
            battery_client.get("users", params)
        elif op_type == "delete":
            battery_client.delete("users", params)
    
    end_time = time.time()
    
    # Calculate execution time
    execution_time = end_time - start_time
    
    # For PLUGGED_IN mode, set a baseline
    if mode == PowerMode.PLUGGED_IN:
        baseline_time = execution_time
        # No assertion, just establishing the baseline
        return baseline_time
    else:
        # Get the baseline (assumes PLUGGED_IN test runs first)
        baseline_time = test_battery_mode_performance(PowerMode.PLUGGED_IN)
        
        # Check that battery-saving modes have longer execution time
        # (deferred operations take longer)
        assert execution_time >= baseline_time
        
        # In LOW and CRITICAL modes, operations should be significantly deferred
        if mode in (PowerMode.BATTERY_LOW, PowerMode.BATTERY_CRITICAL):
            # Non-critical operations should be deferred (execution time much higher)
            assert execution_time > baseline_time * 1.5
        
        return execution_time


@pytest.mark.parametrize("compression_level", [
    CompressionLevel.NONE,
    CompressionLevel.LOW,
    CompressionLevel.MEDIUM,
    CompressionLevel.HIGH
])
def test_compression_performance(compression_level):
    """Test the performance and efficiency of different compression levels."""
    # Create a compressor
    compressor = PayloadCompressor(compression_level)
    
    # Generate test records of different types
    text_record = {
        "id": 1,
        "title": "Text Test",
        "content": "Lorem ipsum " * 1000  # Lots of repeated text
    }
    
    numeric_record = {
        "id": 2,
        "values": [random.randint(1, 1000) for _ in range(1000)]
    }
    
    mixed_record = {
        "id": 3,
        "name": "Mixed Test",
        "metadata": {
            "created": time.time(),
            "tags": ["tag1", "tag2", "tag3"],
            "options": {
                "option1": True,
                "option2": False,
                "option3": "value3"
            }
        },
        "data_points": [
            {"x": random.random(), "y": random.random()}
            for _ in range(100)
        ]
    }
    
    records = [text_record, numeric_record, mixed_record]
    
    # Measure compression ratio and time for each record type
    results = []
    
    for record in records:
        # Convert to JSON for size comparison
        json_data = json.dumps(record).encode('utf-8')
        json_size = len(json_data)
        
        # Time the compression
        start_time = time.time()
        compressed = compressor.compress_record("test", record)
        compression_time = time.time() - start_time
        
        # Time the decompression
        start_time = time.time()
        decompressed = compressor.decompress_record("test", compressed)
        decompression_time = time.time() - start_time
        
        # Calculate compression ratio
        compressed_size = len(compressed)
        compression_ratio = compressed_size / json_size
        
        results.append({
            "record_type": record["id"],
            "json_size": json_size,
            "compressed_size": compressed_size,
            "compression_ratio": compression_ratio,
            "compression_time": compression_time,
            "decompression_time": decompression_time
        })
    
    # Analyze the results
    for result in results:
        # Higher compression levels should compress better
        if compression_level == CompressionLevel.HIGH:
            # Even HIGH compression should be fast enough for practical use
            assert result["compression_time"] < 0.1, f"Compression too slow: {result['compression_time']}"
            assert result["decompression_time"] < 0.1, f"Decompression too slow: {result['decompression_time']}"
            
            # HIGH should achieve good compression (better than 85%)
            assert result["compression_ratio"] < 0.85, f"Compression ratio not good enough: {result['compression_ratio']}"
        
        # For text, even LOW compression should achieve decent results
        if result["record_type"] == 1 and compression_level != CompressionLevel.NONE:
            assert result["compression_ratio"] < 0.3, f"Text compression not efficient: {result['compression_ratio']}"
    
    return results


@pytest.mark.parametrize("record_count", [10, 100, 1000])
@pytest.mark.parametrize("change_percent", [1, 10, 50])
def test_sync_performance(record_count, change_percent):
    """Test sync performance with different data volumes and change percentages."""
    # Create a client and server
    client, server = create_test_client_server(record_count, 500)
    
    # Track transfer sizes
    original_send = client.sync_engine.network.send
    transfer_data = {"initial_size": 0, "incremental_size": 0}
    
    def tracking_send(data):
        # Track the size of the transfer
        if transfer_data["initial_size"] == 0:
            transfer_data["initial_size"] = len(data.encode('utf-8'))
        else:
            transfer_data["incremental_size"] = len(data.encode('utf-8'))
        return original_send(data)
    
    client.sync_engine.network.send = tracking_send
    
    # Initial sync to get baseline data
    start_time = time.time()
    client.sync()
    initial_sync_time = time.time() - start_time
    
    # Calculate how many records to change
    records_to_change = max(1, int(record_count * change_percent / 100))
    
    # Make changes to some records on the server
    for i in range(records_to_change):
        record_id = random.randint(0, record_count - 1)
        server.update("users", {
            "id": record_id,
            "username": f"updated_{record_id}",
            "description": generate_random_string(200)
        })
    
    # Sync again and measure the time
    start_time = time.time()
    client.sync()
    incremental_sync_time = time.time() - start_time
    
    # Calculate the ratio of incremental to full sync
    size_ratio = transfer_data["incremental_size"] / transfer_data["initial_size"]
    time_ratio = incremental_sync_time / initial_sync_time
    
    # Check that incremental sync is more efficient
    assert size_ratio < change_percent / 100 * 2, f"Incremental sync not efficient: {size_ratio}"
    assert time_ratio < 0.5, f"Incremental sync not faster: {time_ratio}"
    
    # Additional checks for larger datasets
    if record_count >= 1000:
        # For large datasets, even with 50% changes, incremental should be much more efficient
        assert size_ratio < 0.6, f"Large dataset sync not efficient: {size_ratio}"
        
        # Sync should complete in a reasonable time even for large datasets
        assert initial_sync_time < 3.0, f"Initial sync too slow: {initial_sync_time}"
        assert incremental_sync_time < 3.0, f"Incremental sync too slow: {incremental_sync_time}"
    
    return {
        "record_count": record_count,
        "change_percent": change_percent,
        "initial_sync_time": initial_sync_time,
        "incremental_sync_time": incremental_sync_time,
        "initial_size": transfer_data["initial_size"],
        "incremental_size": transfer_data["incremental_size"],
        "size_ratio": size_ratio,
        "time_ratio": time_ratio
    }


@pytest.mark.parametrize("record_count", [1000])
@pytest.mark.parametrize("conflict_count", [10, 100])
def test_conflict_resolution_performance(record_count, conflict_count):
    """Test the performance of conflict resolution with different conflict volumes."""
    # Create a client and server
    client, server = create_test_client_server(record_count, 100)

    # Set up conflict resolvers
    field_priorities = {
        "users": ["username", "email"]  # Prioritize these fields from client
    }
    client.register_conflict_resolver("users", MergeFieldsResolver(field_priorities))
    server.register_conflict_resolver("users", MergeFieldsResolver(field_priorities))

    # Initial sync to get baseline data
    client.sync()

    # Generate a specific set of record IDs for conflict testing
    # We'll create these records explicitly to ensure they exist
    conflict_record_ids = list(range(conflict_count))

    # Ensure the test records exist on both client and server
    for record_id in conflict_record_ids:
        try:
            # Check if record exists
            existing = server.get("users", [record_id])
            if existing is None:
                # Create the record on the server if it doesn't exist
                server.insert("users", {
                    "id": record_id,
                    "username": f"original_user_{record_id}",
                    "email": f"original_{record_id}@example.com",
                    "description": f"Original description {record_id}"
                })
        except Exception as e:
            # If there's an error (like record not existing), create it
            server.insert("users", {
                "id": record_id,
                "username": f"original_user_{record_id}",
                "email": f"original_{record_id}@example.com",
                "description": f"Original description {record_id}"
            })

    # Sync to ensure client has all the test records
    client.sync()

    # Verify all test records exist on both sides
    for record_id in conflict_record_ids:
        server_record = server.get("users", [record_id])
        client_record = client.get("users", [record_id])
        assert server_record is not None, f"Record {record_id} missing on server"
        assert client_record is not None, f"Record {record_id} missing on client"

    # Create conflicts by updating the same records on both client and server
    for record_id in conflict_record_ids:
        # Update on server
        server.update("users", {
            "id": record_id,
            "username": f"server_{record_id}",
            "email": f"server_{record_id}@example.com",
            "description": f"Server description {record_id}"
        })

        # Update on client
        client.update("users", {
            "id": record_id,
            "username": f"client_{record_id}",
            "email": f"client_{record_id}@example.com",
            "description": f"Client description {record_id}"
        })

    # Sync and measure the time
    start_time = time.time()
    client.sync()
    sync_time = time.time() - start_time

    # Check the results
    # Conflict resolution should be reasonably fast
    assert sync_time < conflict_count * 0.01, f"Conflict resolution too slow: {sync_time} for {conflict_count} conflicts"

    # Check that the correct conflict resolution was applied
    for record_id in conflict_record_ids:
        server_record = server.get("users", [record_id])
        client_record = client.get("users", [record_id])

        # Records should exist on both sides
        assert server_record is not None, f"Record {record_id} missing on server after sync"
        assert client_record is not None, f"Record {record_id} missing on client after sync"

        # Fields should be merged correctly according to our field priorities
        # Since we're using MergeFieldsResolver with username and email priority,
        # these fields should come from the client
        assert server_record["username"] == f"client_{record_id}", f"Username not from client for record {record_id}"
        assert server_record["email"] == f"client_{record_id}@example.com", f"Email not from client for record {record_id}"
        assert client_record["username"] == server_record["username"], f"Username mismatch for record {record_id}"
        assert client_record["email"] == server_record["email"], f"Email mismatch for record {record_id}"

    # Check that conflict audit log recorded the conflicts
    server_conflicts = server.get_conflict_history()
    assert len(server_conflicts) >= conflict_count, f"Not enough conflicts in audit log: {len(server_conflicts)} < {conflict_count}"

    # Return a summary without binary data that might cause JSON serialization issues
    result = {
        "record_count": record_count,
        "conflict_count": conflict_count,
        "sync_time": sync_time,
        "conflicts_resolved": len(server_conflicts),
        "success": True
    }

    # Don't return any data that might contain non-JSON serializable values
    return result