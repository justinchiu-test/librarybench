"""Unit tests for the database engine."""

import time
import pytest
from typing import Dict, Any

from in_memory_database_mobile_app_developer.database import (
    MobileDBEngine, ColumnType, TableSchema, SchemaField
)
from in_memory_database_mobile_app_developer.exceptions import (
    TableAlreadyExistsError, TableNotFoundError, RecordNotFoundError, SchemaValidationError
)


@pytest.fixture
def db_engine() -> MobileDBEngine:
    """Create a database engine for testing."""
    return MobileDBEngine(max_memory_mb=10)


@pytest.fixture
def test_table(db_engine: MobileDBEngine) -> None:
    """Create a test table for testing."""
    db_engine.create_table(
        name="test_table",
        schema={
            "id": "string",
            "name": "string",
            "age": "integer",
            "is_active": "boolean",
            "created_at": "datetime",
            "metadata": "json",
        },
        primary_key="id",
        nullable_fields=["age", "metadata"],
        default_values={"is_active": True},
        indexes=["name"],
    )


def test_create_table(db_engine: MobileDBEngine) -> None:
    """Test creating a table."""
    # Create a table
    db_engine.create_table(
        name="users",
        schema={
            "id": "string",
            "username": "string",
            "email": "string",
            "age": "integer",
            "is_active": "boolean",
        },
        primary_key="id",
        nullable_fields=["age"],
        default_values={"is_active": True},
        indexes=["username", "email"],
    )
    
    # Verify the table exists
    assert db_engine.table_exists("users")
    
    # Verify the schema
    table = db_engine.get_table("users")
    assert table.schema.name == "users"
    assert table.schema.primary_key == "id"
    assert set(table.schema.indexes) == {"id", "username", "email"}
    
    # Verify field properties
    assert table.schema.fields["id"].is_primary_key
    assert table.schema.fields["age"].nullable
    assert table.schema.fields["is_active"].default is True
    assert table.schema.fields["username"].data_type == "string"
    
    # Test creating a table that already exists
    with pytest.raises(TableAlreadyExistsError):
        db_engine.create_table(
            name="users",
            schema={"id": "string"},
            primary_key="id",
        )


def test_drop_table(db_engine: MobileDBEngine) -> None:
    """Test dropping a table."""
    # Create a table
    db_engine.create_table(
        name="temp_table",
        schema={"id": "string"},
        primary_key="id",
    )
    
    # Verify the table exists
    assert db_engine.table_exists("temp_table")
    
    # Drop the table
    db_engine.drop_table("temp_table")
    
    # Verify the table no longer exists
    assert not db_engine.table_exists("temp_table")
    
    # Test dropping a table that does not exist
    with pytest.raises(TableNotFoundError):
        db_engine.drop_table("nonexistent_table")


def test_insert_record(db_engine: MobileDBEngine, test_table) -> None:
    """Test inserting a record."""
    # Insert a record
    record_id = db_engine.insert(
        table_name="test_table",
        data={
            "id": "user1",
            "name": "John Doe",
            "age": 30,
            "is_active": True,
            "created_at": "2023-01-01T12:00:00Z",
            "metadata": {"tags": ["customer", "premium"]},
        },
        client_id="client1",
    )
    
    # Verify the record was inserted
    assert record_id == "user1"
    
    # Get the record
    record = db_engine.get("test_table", "user1")
    
    # Verify the record data
    assert record["id"] == "user1"
    assert record["name"] == "John Doe"
    assert record["age"] == 30
    assert record["is_active"] is True
    assert record["created_at"] == "2023-01-01T12:00:00Z"
    assert record["metadata"] == {"tags": ["customer", "premium"]}
    
    # Test inserting a record with a primary key that already exists
    with pytest.raises(ValueError):
        db_engine.insert(
            table_name="test_table",
            data={
                "id": "user1",
                "name": "Jane Doe",
            },
        )
    
    # Test inserting a record with missing required fields
    with pytest.raises(SchemaValidationError):
        db_engine.insert(
            table_name="test_table",
            data={
                "id": "user2",
                # missing required 'name' field
                "age": 25,
            },
        )
    
    # Test inserting a record with defaults and nullable fields
    record_id2 = db_engine.insert(
        table_name="test_table",
        data={
            "id": "user2",
            "name": "Jane Doe",
            # omitting 'age' and 'metadata' which are nullable
            "created_at": "2023-01-02T12:00:00Z",
            # omitting 'is_active' which has a default value
        },
    )
    
    # Verify the record was inserted with defaults
    record2 = db_engine.get("test_table", "user2")
    assert record2["is_active"] is True  # default value
    assert record2["age"] is None  # nullable field


def test_get_record(db_engine: MobileDBEngine, test_table) -> None:
    """Test getting a record."""
    # Insert a record
    db_engine.insert(
        table_name="test_table",
        data={
            "id": "user1",
            "name": "John Doe",
            "age": 30,
            "is_active": True,
            "created_at": "2023-01-01T12:00:00Z",
        },
    )
    
    # Get the record
    record = db_engine.get("test_table", "user1")
    
    # Verify the record data
    assert record["id"] == "user1"
    assert record["name"] == "John Doe"
    assert record["age"] == 30
    
    # Test getting a record that does not exist
    with pytest.raises(RecordNotFoundError):
        db_engine.get("test_table", "nonexistent")
    
    # Test getting a record from a table that does not exist
    with pytest.raises(TableNotFoundError):
        db_engine.get("nonexistent_table", "user1")


def test_update_record(db_engine: MobileDBEngine, test_table) -> None:
    """Test updating a record."""
    # Insert a record
    db_engine.insert(
        table_name="test_table",
        data={
            "id": "user1",
            "name": "John Doe",
            "age": 30,
            "is_active": True,
            "created_at": "2023-01-01T12:00:00Z",
        },
    )
    
    # Update the record
    updated_data = db_engine.update(
        table_name="test_table",
        pk="user1",
        data={
            "name": "John Smith",
            "age": 31,
        },
        client_id="client1",
    )
    
    # Verify the updated data
    assert updated_data["name"] == "John Smith"
    assert updated_data["age"] == 31
    assert updated_data["is_active"] is True  # unchanged
    
    # Get the record to verify the update
    record = db_engine.get("test_table", "user1")
    assert record["name"] == "John Smith"
    assert record["age"] == 31
    
    # Test updating a record that does not exist
    with pytest.raises(RecordNotFoundError):
        db_engine.update(
            table_name="test_table",
            pk="nonexistent",
            data={"name": "New Name"},
        )
    
    # Test updating a record with an invalid field type
    with pytest.raises(SchemaValidationError):
        db_engine.update(
            table_name="test_table",
            pk="user1",
            data={"age": "not an integer"},
        )
    
    # Test updating a primary key (should not be allowed)
    with pytest.raises(SchemaValidationError):
        db_engine.update(
            table_name="test_table",
            pk="user1",
            data={"id": "user2"},
        )


def test_delete_record(db_engine: MobileDBEngine, test_table) -> None:
    """Test deleting a record."""
    # Insert a record
    db_engine.insert(
        table_name="test_table",
        data={
            "id": "user1",
            "name": "John Doe",
            "age": 30,
            "is_active": True,
            "created_at": "2023-01-01T12:00:00Z",
        },
    )
    
    # Delete the record
    db_engine.delete("test_table", "user1", "client1")
    
    # Verify the record was deleted
    with pytest.raises(RecordNotFoundError):
        db_engine.get("test_table", "user1")
    
    # Test deleting a record that does not exist
    with pytest.raises(RecordNotFoundError):
        db_engine.delete("test_table", "nonexistent")


def test_find_records(db_engine: MobileDBEngine, test_table) -> None:
    """Test finding records based on conditions."""
    # Insert multiple records
    db_engine.insert(
        table_name="test_table",
        data={
            "id": "user1",
            "name": "John Doe",
            "age": 30,
            "is_active": True,
            "created_at": "2023-01-01T12:00:00Z",
        },
    )
    
    db_engine.insert(
        table_name="test_table",
        data={
            "id": "user2",
            "name": "Jane Doe",
            "age": 28,
            "is_active": True,
            "created_at": "2023-01-02T12:00:00Z",
        },
    )
    
    db_engine.insert(
        table_name="test_table",
        data={
            "id": "user3",
            "name": "Alice Smith",
            "age": 35,
            "is_active": False,
            "created_at": "2023-01-03T12:00:00Z",
        },
    )
    
    # Find records by a single condition
    active_users = db_engine.find("test_table", {"is_active": True})
    assert len(active_users) == 2
    assert active_users[0]["id"] in ["user1", "user2"]
    assert active_users[1]["id"] in ["user1", "user2"]
    
    # Find records by multiple conditions
    active_and_young = db_engine.find("test_table", {"is_active": True, "age": 28})
    assert len(active_and_young) == 1
    assert active_and_young[0]["id"] == "user2"
    
    # Find with limit and offset
    all_limited = db_engine.find("test_table", {}, limit=2)
    assert len(all_limited) == 2
    
    all_offset = db_engine.find("test_table", {}, offset=1)
    assert len(all_offset) == 2
    assert all_offset[0]["id"] != "user1"  # First record should be skipped
    
    # Find by indexed field (name)
    by_name = db_engine.find("test_table", {"name": "Alice Smith"})
    assert len(by_name) == 1
    assert by_name[0]["id"] == "user3"
    
    # Test find with no matches
    no_matches = db_engine.find("test_table", {"age": 99})
    assert len(no_matches) == 0


def test_count_records(db_engine: MobileDBEngine, test_table) -> None:
    """Test counting records."""
    # Insert multiple records
    db_engine.insert(
        table_name="test_table",
        data={
            "id": "user1",
            "name": "John Doe",
            "age": 30,
            "is_active": True,
            "created_at": "2023-01-01T12:00:00Z",
        },
    )
    
    db_engine.insert(
        table_name="test_table",
        data={
            "id": "user2",
            "name": "Jane Doe",
            "age": 28,
            "is_active": True,
            "created_at": "2023-01-02T12:00:00Z",
        },
    )
    
    db_engine.insert(
        table_name="test_table",
        data={
            "id": "user3",
            "name": "Alice Smith",
            "age": 35,
            "is_active": False,
            "created_at": "2023-01-03T12:00:00Z",
        },
    )
    
    # Count all records
    total_count = db_engine.count("test_table")
    assert total_count == 3
    
    # Count with condition
    active_count = db_engine.count("test_table", {"is_active": True})
    assert active_count == 2
    
    # Count with multiple conditions
    specific_count = db_engine.count("test_table", {"is_active": True, "age": 28})
    assert specific_count == 1
    
    # Count with no matches
    no_matches = db_engine.count("test_table", {"age": 99})
    assert no_matches == 0


def test_get_all_records(db_engine: MobileDBEngine, test_table) -> None:
    """Test getting all records."""
    # Insert multiple records
    db_engine.insert(
        table_name="test_table",
        data={
            "id": "user1",
            "name": "John Doe",
            "age": 30,
            "is_active": True,
            "created_at": "2023-01-01T12:00:00Z",
        },
    )
    
    db_engine.insert(
        table_name="test_table",
        data={
            "id": "user2",
            "name": "Jane Doe",
            "age": 28,
            "is_active": True,
            "created_at": "2023-01-02T12:00:00Z",
        },
    )
    
    # Get all records
    all_records = db_engine.get_all("test_table")
    assert len(all_records) == 2
    
    # Get with limit
    limited = db_engine.get_all("test_table", limit=1)
    assert len(limited) == 1
    
    # Get with offset
    offset = db_engine.get_all("test_table", offset=1)
    assert len(offset) == 1
    assert offset[0]["id"] != all_records[0]["id"]


def test_change_tracking(db_engine: MobileDBEngine, test_table) -> None:
    """Test change tracking functionality."""
    # Insert a record
    db_engine.insert(
        table_name="test_table",
        data={
            "id": "user1",
            "name": "John Doe",
            "age": 30,
            "is_active": True,
            "created_at": "2023-01-01T12:00:00Z",
        },
        client_id="client1",
    )
    
    # Get the insertion time
    insert_time = time.time()
    
    # Wait a moment to ensure time difference
    time.sleep(0.1)
    
    # Update the record
    db_engine.update(
        table_name="test_table",
        pk="user1",
        data={"name": "John Smith"},
        client_id="client2",
    )
    
    # Get changes since insertion
    changes = db_engine.get_changes_since("test_table", insert_time)
    assert len(changes) == 1
    assert changes[0][0] == "user1"  # Primary key
    assert changes[0][1].data["name"] == "John Smith"  # Updated data
    
    # Get changes from a specific client
    client_changes = db_engine.get_changes_since("test_table", 0, "client1")
    assert len(client_changes) == 0  # Should be none since we exclude client1's changes
    
    # Get changes from another client
    other_client_changes = db_engine.get_changes_since("test_table", 0, "client3")
    assert len(other_client_changes) == 1  # Should include both changes
    
    # Wait a moment to ensure time difference
    time.sleep(0.1)
    
    # Update again
    db_engine.update(
        table_name="test_table",
        pk="user1",
        data={"age": 31},
        client_id="client3",
    )
    
    # Delete the record
    time.sleep(0.1)
    db_engine.delete("test_table", "user1", "client1")
    
    # Get all changes
    all_changes = db_engine.get_changes_since("test_table", 0)
    assert len(all_changes) == 1  # Should include the record with deleted flag
    assert all_changes[0][1].is_deleted  # Should be marked as deleted


def test_client_session_management(db_engine: MobileDBEngine) -> None:
    """Test client session management."""
    # Register a client
    db_engine.register_client("client1")
    
    # Verify the client session was created
    client_session = db_engine.get_client_session("client1")
    assert client_session is not None
    assert client_session["id"] == "client1"
    
    # Update client sync state
    db_engine.update_client_sync_state("client1", "test_table", 12345.0)
    
    # Verify the sync state was updated
    sync_state = db_engine.get_client_sync_state("client1", "test_table")
    assert sync_state == 12345.0
    
    # Register a client with initial sync state
    db_engine.register_client("client2", {"table1": 100.0, "table2": 200.0})
    
    # Verify the sync state was set
    all_sync_state = db_engine.get_client_sync_state("client2")
    assert all_sync_state["table1"] == 100.0
    assert all_sync_state["table2"] == 200.0


def test_column_type_validation() -> None:
    """Test column type validation."""
    # Test string validation
    assert ColumnType.validate("test", ColumnType.STRING)
    assert not ColumnType.validate(123, ColumnType.STRING)
    
    # Test integer validation
    assert ColumnType.validate(123, ColumnType.INTEGER)
    assert not ColumnType.validate("123", ColumnType.INTEGER)
    assert not ColumnType.validate(True, ColumnType.INTEGER)  # Boolean is not an integer
    
    # Test float validation
    assert ColumnType.validate(123.45, ColumnType.FLOAT)
    assert not ColumnType.validate("123.45", ColumnType.FLOAT)
    
    # Test boolean validation
    assert ColumnType.validate(True, ColumnType.BOOLEAN)
    assert ColumnType.validate(False, ColumnType.BOOLEAN)
    assert not ColumnType.validate("true", ColumnType.BOOLEAN)
    assert not ColumnType.validate(1, ColumnType.BOOLEAN)
    
    # Test datetime validation
    assert ColumnType.validate("2023-01-01T12:00:00Z", ColumnType.DATETIME)
    assert not ColumnType.validate("invalid date", ColumnType.DATETIME)
    
    # Test JSON validation
    assert ColumnType.validate({"key": "value"}, ColumnType.JSON)
    assert ColumnType.validate([1, 2, 3], ColumnType.JSON)
    assert ColumnType.validate('{"key": "value"}', ColumnType.JSON)
    assert not ColumnType.validate(object(), ColumnType.JSON)
    
    # Test binary validation
    assert ColumnType.validate(b"binary data", ColumnType.BINARY)
    assert not ColumnType.validate("string data", ColumnType.BINARY)


def test_column_type_conversion() -> None:
    """Test column type conversion."""
    # Test string conversion
    assert ColumnType.convert(123, ColumnType.STRING) == "123"
    
    # Test integer conversion
    assert ColumnType.convert("123", ColumnType.INTEGER) == 123
    
    # Test float conversion
    assert ColumnType.convert("123.45", ColumnType.FLOAT) == 123.45
    
    # Test boolean conversion
    assert ColumnType.convert("True", ColumnType.BOOLEAN) is True
    assert ColumnType.convert(0, ColumnType.BOOLEAN) is False
    
    # Test datetime conversion
    assert ColumnType.convert("2023-01-01T12:00:00Z", ColumnType.DATETIME) is not None
    
    # Test JSON conversion
    converted_json = ColumnType.convert('{"key": "value"}', ColumnType.JSON)
    assert converted_json == {"key": "value"}
    
    # Test binary conversion
    assert ColumnType.convert("binary", ColumnType.BINARY) == b"binary"