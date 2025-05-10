"""Unit tests for the sync protocol and conflict resolution."""

import time
import asyncio
import pytest
import copy
from typing import Dict, Any, List, Tuple

from in_memory_database_mobile_app_developer.database import MobileDBEngine, Record
from in_memory_database_mobile_app_developer.sync import (
    SyncBatch, SyncSession, SyncManager, SyncClientSession
)
from in_memory_database_mobile_app_developer.conflict import (
    ConflictStrategy, ConflictResolver, ConflictDetector, ConflictRecord
)
from in_memory_database_mobile_app_developer.exceptions import SyncError, ConflictError


@pytest.fixture
def db_engine() -> MobileDBEngine:
    """Create a database engine for testing."""
    db = MobileDBEngine(max_memory_mb=10)
    
    # Create a test table
    db.create_table(
        name="test_table",
        schema={
            "id": "string",
            "name": "string",
            "value": "integer",
            "updated_at": "string",
        },
        primary_key="id",
    )
    
    # Add some test data
    db.insert(
        table_name="test_table",
        data={
            "id": "record1",
            "name": "Test Record 1",
            "value": 100,
            "updated_at": "2023-01-01T12:00:00Z",
        },
        client_id="server",
    )
    
    db.insert(
        table_name="test_table",
        data={
            "id": "record2",
            "name": "Test Record 2",
            "value": 200,
            "updated_at": "2023-01-01T12:00:00Z",
        },
        client_id="server",
    )
    
    return db


@pytest.fixture
def sync_manager(db_engine: MobileDBEngine) -> SyncManager:
    """Create a sync manager for testing."""
    return SyncManager(db_engine, batch_size=2)


@pytest.fixture
def sync_session(db_engine: MobileDBEngine) -> SyncSession:
    """Create a sync session for testing."""
    # Register client
    db_engine.register_client("client1")
    
    return SyncSession("client1", db_engine, batch_size=2)


@pytest.fixture
def conflict_resolver() -> ConflictResolver:
    """Create a conflict resolver for testing."""
    return ConflictResolver(default_strategy=ConflictStrategy.LAST_WRITE_WINS.value)


@pytest.fixture
def conflict_detector(conflict_resolver: ConflictResolver) -> ConflictDetector:
    """Create a conflict detector for testing."""
    return ConflictDetector(conflict_resolver)


@pytest.fixture
def mock_server_connection() -> "MockServerConnection":
    """Create a mock server connection for testing."""
    return MockServerConnection()


class MockServerConnection:
    """Mock server connection for testing."""
    
    def __init__(self):
        """Initialize with empty state."""
        self.sessions = {}
        self.batches = {}
        self.completed_sessions = set()
        self.resume_tokens = {}
    
    async def start_sync(self, client_id: str, resume_token=None) -> Dict[str, Any]:
        """Start a sync session."""
        session_id = f"session_{client_id}_{int(time.time())}"
        self.sessions[session_id] = {
            "client_id": client_id,
            "started_at": time.time(),
            "batches": [],
        }
        return {
            "session_id": session_id,
            "started_at": self.sessions[session_id]["started_at"],
            "client_id": client_id,
        }
    
    async def get_next_batch(self, session_id: str, table_name: str) -> Dict[str, Any]:
        """Get the next batch of changes."""
        if session_id not in self.sessions:
            raise SyncError("Invalid session ID")
        
        # In a real implementation, this would get data from the server
        # For testing, we'll just return some mock data
        record1 = Record(
            data={
                "id": f"server_record1_{table_name}",
                "name": f"Server Record 1 - {table_name}",
                "value": 1000,
                "updated_at": "2023-01-02T12:00:00Z",
            },
            created_at=time.time() - 3600,
            updated_at=time.time() - 1800,
            version=1,
            client_id="server",
        )
        
        record2 = Record(
            data={
                "id": f"server_record2_{table_name}",
                "name": f"Server Record 2 - {table_name}",
                "value": 2000,
                "updated_at": "2023-01-02T13:00:00Z",
            },
            created_at=time.time() - 3600,
            updated_at=time.time() - 1800,
            version=1,
            client_id="server",
        )
        
        batch = SyncBatch(
            table_name=table_name,
            records=[
                (record1.data["id"], record1),
                (record2.data["id"], record2),
            ],
            is_last_batch=True,
        )
        
        batch_dict = batch.to_dict()
        self.batches[batch.batch_id] = batch_dict
        self.sessions[session_id]["batches"].append(batch.batch_id)
        
        return batch_dict
    
    async def apply_batch(self, session_id: str, batch_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a batch of changes."""
        if session_id not in self.sessions:
            raise SyncError("Invalid session ID")
        
        # In a real implementation, this would apply changes to the server
        # For testing, we'll just acknowledge receipt
        batch_id = batch_dict["batch_id"]
        return {
            "batch_id": batch_id,
            "applied_count": len(batch_dict["records"]),
            "conflicts": [],
            "table_name": batch_dict["table_name"],
            "is_complete": batch_dict["is_last_batch"],
        }
    
    async def complete_sync(self, session_id: str) -> Dict[str, Any]:
        """Complete a sync session."""
        if session_id not in self.sessions:
            raise SyncError("Invalid session ID")
        
        # Mark the session as completed
        self.completed_sessions.add(session_id)
        
        return {
            "session_id": session_id,
            "client_id": self.sessions[session_id]["client_id"],
            "started_at": self.sessions[session_id]["started_at"],
            "completed_at": time.time(),
            "duration": time.time() - self.sessions[session_id]["started_at"],
            "tables_synced": ["test_table"],
        }
    
    async def get_resume_token(self, session_id: str) -> Dict[str, Any]:
        """Get a resume token for a sync session."""
        if session_id not in self.sessions:
            raise SyncError("Invalid session ID")
        
        # Create a resume token
        resume_token = f"resume_{session_id}_{int(time.time())}"
        self.resume_tokens[resume_token] = session_id
        
        return {
            "session_id": session_id,
            "resume_token": resume_token,
        }


def test_sync_batch_creation() -> None:
    """Test creating a sync batch."""
    # Create a record
    record = Record(
        data={
            "id": "test1",
            "name": "Test Record",
            "value": 100,
        },
        created_at=time.time() - 3600,
        updated_at=time.time() - 1800,
        version=1,
        client_id="client1",
    )
    
    # Create a batch
    batch = SyncBatch(
        table_name="test_table",
        records=[("test1", record)],
        is_last_batch=True,
    )
    
    # Check batch properties
    assert batch.table_name == "test_table"
    assert len(batch.records) == 1
    assert batch.records[0][0] == "test1"
    assert batch.is_last_batch is True
    assert batch.checksum is not None
    
    # Convert to dict and back
    batch_dict = batch.to_dict()
    reconstructed = SyncBatch.from_dict(batch_dict)
    
    # Check reconstructed batch
    assert reconstructed.table_name == batch.table_name
    assert len(reconstructed.records) == len(batch.records)
    assert reconstructed.checksum == batch.checksum
    assert reconstructed.is_last_batch == batch.is_last_batch
    
    # Verify checksum
    assert batch.verify_checksum()
    assert reconstructed.verify_checksum()


def test_sync_session_get_next_batch(db_engine: MobileDBEngine, sync_session: SyncSession) -> None:
    """Test getting the next batch of changes from a sync session."""
    # Start the sync session
    sync_session.start_sync()
    
    # Get the next batch
    batch = sync_session.get_next_batch("test_table")
    
    # Check batch properties
    assert batch is not None
    assert batch.table_name == "test_table"
    assert len(batch.records) == 2  # We created 2 records in the fixture
    assert batch.is_last_batch is True  # Only 2 records, with batch size 2
    
    # Try to get another batch (should be None as we've sent all records)
    next_batch = sync_session.get_next_batch("test_table")
    assert next_batch is None
    
    # Verify table is marked as completed
    assert "test_table" in sync_session.completed_tables


def test_sync_session_apply_batch(db_engine: MobileDBEngine, sync_session: SyncSession) -> None:
    """Test applying a batch of changes to a sync session."""
    # Start the sync session
    sync_session.start_sync()
    
    # Create a batch to apply
    record = Record(
        data={
            "id": "client_record1",
            "name": "Client Record 1",
            "value": 300,
            "updated_at": "2023-01-03T12:00:00Z",
        },
        created_at=time.time() - 3600,
        updated_at=time.time() - 1800,
        version=1,
        client_id="client1",
    )
    
    batch = SyncBatch(
        table_name="test_table",
        records=[("client_record1", record)],
        is_last_batch=True,
    )
    
    # Apply the batch
    result = sync_session.apply_batch(batch)
    
    # Check result
    assert result["batch_id"] == batch.batch_id
    assert result["applied_count"] == 1
    assert len(result["conflicts"]) == 0
    assert result["is_complete"] is True
    
    # Verify the record was inserted
    try:
        inserted = db_engine.get("test_table", "client_record1")
        assert inserted["name"] == "Client Record 1"
        assert inserted["value"] == 300
    except Exception as e:
        pytest.fail(f"Failed to get inserted record: {str(e)}")
    
    # Verify table is marked as completed
    assert "test_table" in sync_session.completed_tables


def test_sync_session_handle_conflict(db_engine: MobileDBEngine, sync_session: SyncSession) -> None:
    """Test handling conflicts in a sync session."""
    # Start the sync session
    sync_session.start_sync()
    
    # Insert a record on the server with a specific version
    server_record = Record(
        data={
            "id": "conflict_record",
            "name": "Server Version",
            "value": 100,
            "updated_at": "2023-01-01T12:00:00Z",
        },
        created_at=time.time() - 3600,
        updated_at=time.time() - 1800,
        version=2,  # Higher version
        client_id="server",
    )
    
    db_engine.get_table("test_table").data["conflict_record"] = server_record
    
    # Create a client batch with the same record but lower version
    client_record = Record(
        data={
            "id": "conflict_record",
            "name": "Client Version",
            "value": 200,
            "updated_at": "2023-01-02T12:00:00Z",  # More recent date
        },
        created_at=time.time() - 3600,
        updated_at=time.time() - 1800,
        version=1,  # Lower version
        client_id="client1",
    )
    
    batch = SyncBatch(
        table_name="test_table",
        records=[("conflict_record", client_record)],
        is_last_batch=True,
    )
    
    # Apply the batch
    result = sync_session.apply_batch(batch)
    
    # Check result
    assert result["applied_count"] == 0  # No changes applied due to conflict
    assert len(result["conflicts"]) == 1  # One conflict detected
    
    # Verify the server record was not changed
    server_data = db_engine.get("test_table", "conflict_record")
    assert server_data["name"] == "Server Version"
    assert server_data["value"] == 100


def test_sync_manager_operations(db_engine: MobileDBEngine, sync_manager: SyncManager) -> None:
    """Test sync manager operations."""
    # Start a sync session
    result = sync_manager.start_sync_session("client1")
    session_id = result["session_id"]
    
    # Verify session was created
    assert session_id in sync_manager.active_sessions
    
    # Get next batch
    batch_dict = sync_manager.get_next_batch(session_id, "test_table")
    assert batch_dict is not None
    assert batch_dict["table_name"] == "test_table"
    assert len(batch_dict["records"]) == 2  # We created 2 records in the fixture
    
    # Apply a batch
    client_record = Record(
        data={
            "id": "client_record1",
            "name": "Client Record 1",
            "value": 300,
            "updated_at": "2023-01-03T12:00:00Z",
        },
        created_at=time.time() - 3600,
        updated_at=time.time() - 1800,
        version=1,
        client_id="client1",
    )
    
    client_batch = SyncBatch(
        table_name="test_table",
        records=[("client_record1", client_record)],
        is_last_batch=True,
    )
    
    apply_result = sync_manager.apply_batch(session_id, client_batch.to_dict())
    assert apply_result["applied_count"] == 1
    
    # Get sync status
    status = sync_manager.get_sync_status(session_id)
    assert status["client_id"] == "client1"
    assert status["in_progress"] is True
    
    # Complete the sync
    complete_result = sync_manager.complete_sync(session_id)
    assert complete_result["session_id"] == session_id
    
    # Verify session is removed
    assert session_id not in sync_manager.active_sessions


def test_conflict_detection_and_resolution(db_engine: MobileDBEngine, conflict_detector: ConflictDetector) -> None:
    """Test conflict detection and resolution."""
    # Create conflicting records
    server_record = Record(
        data={
            "id": "conflict_record",
            "name": "Server Version",
            "value": 100,
            "updated_at": "2023-01-01T12:00:00Z",
        },
        created_at=time.time() - 3600,
        updated_at=time.time() - 1800,
        version=1,
        client_id="server",
    )
    
    client_record = Record(
        data={
            "id": "conflict_record",
            "name": "Client Version",
            "value": 200,
            "updated_at": "2023-01-02T12:00:00Z",  # More recent
        },
        created_at=time.time() - 3600,
        updated_at=time.time() - 1700,  # More recent
        version=1,
        client_id="client1",
    )
    
    # Detect conflict
    conflict = conflict_detector.detect_conflict(
        table_name="test_table",
        record_id="conflict_record",
        server_record=server_record,
        client_record=client_record,
    )
    
    # Verify conflict was detected
    assert conflict is not None
    assert conflict.record_id == "conflict_record"
    assert "name" in conflict.field_conflicts
    assert "value" in conflict.field_conflicts
    
    # Resolve conflict with last-write-wins strategy
    resolved = conflict_detector.resolve_conflict(conflict, ConflictStrategy.LAST_WRITE_WINS.value)
    
    # In last-write-wins with client having more recent timestamp, client should win
    assert resolved is not None
    assert resolved.data["name"] == "Client Version"
    assert resolved.data["value"] == 200
    
    # Try server-wins strategy
    resolved2 = conflict_detector.resolve_conflict(conflict, ConflictStrategy.SERVER_WINS.value)
    
    # In server-wins, server should win regardless of timestamp
    assert resolved2 is not None
    assert resolved2.data["name"] == "Server Version"
    assert resolved2.data["value"] == 100


def test_conflict_resolution_strategies(conflict_resolver: ConflictResolver) -> None:
    """Test different conflict resolution strategies."""
    # Create conflicting records
    server_record = Record(
        data={
            "id": "conflict_record",
            "name": "Server Version",
            "value": 100,
            "updated_at": "2023-01-01T12:00:00Z",
            "shared": "Same Value",
        },
        created_at=time.time() - 3600,
        updated_at=time.time() - 1800,
        version=1,
        client_id="server",
    )
    
    client_record = Record(
        data={
            "id": "conflict_record",
            "name": "Client Version",
            "value": 200,
            "updated_at": "2023-01-02T12:00:00Z",
            "shared": "Same Value",
        },
        created_at=time.time() - 3600,
        updated_at=time.time() - 1700,  # More recent
        version=1,
        client_id="client1",
    )
    
    # Create conflict record
    conflict = ConflictRecord(
        record_id="conflict_record",
        server_record=server_record,
        client_record=client_record,
        field_conflicts={"name", "value"},
        table_name="test_table",
    )
    
    # Test last-write-wins strategy
    resolved_lww = conflict_resolver.resolve(conflict, ConflictStrategy.LAST_WRITE_WINS.value)
    assert resolved_lww.data["name"] == "Client Version"  # Client has newer timestamp
    
    # Test server-wins strategy
    resolved_server = conflict_resolver.resolve(conflict, ConflictStrategy.SERVER_WINS.value)
    assert resolved_server.data["name"] == "Server Version"
    
    # Test client-wins strategy
    resolved_client = conflict_resolver.resolve(conflict, ConflictStrategy.CLIENT_WINS.value)
    assert resolved_client.data["name"] == "Client Version"
    
    # Test merge strategy with field-specific strategies
    conflict_resolver.set_field_strategy(
        table_name="test_table",
        field_name="name",
        strategy="server_wins",
    )
    
    conflict_resolver.set_field_strategy(
        table_name="test_table",
        field_name="value",
        strategy="client_wins",
    )
    
    resolved_merge = conflict_resolver.resolve(conflict, ConflictStrategy.MERGE.value)
    assert resolved_merge.data["name"] == "Server Version"  # Server wins for name
    assert resolved_merge.data["value"] == 200  # Client wins for value
    assert resolved_merge.data["shared"] == "Same Value"  # No conflict, value preserved
    
    # Test custom merge function
    def sum_values(server_value, client_value):
        return server_value + client_value
    
    conflict_resolver.set_field_strategy(
        table_name="test_table",
        field_name="value",
        strategy=sum_values,
        description="Sum the values",
    )
    
    resolved_custom = conflict_resolver.resolve(conflict, ConflictStrategy.MERGE.value)
    assert resolved_custom.data["value"] == 300  # 100 + 200


def test_client_priority_resolution(conflict_resolver: ConflictResolver) -> None:
    """Test client priority conflict resolution."""
    # Set client priorities
    conflict_resolver.set_client_priority("high_priority", 10)
    conflict_resolver.set_client_priority("low_priority", 5)
    
    # Create conflicting records
    server_record = Record(
        data={
            "id": "conflict_record",
            "name": "Server Version",
            "value": 100,
        },
        created_at=time.time() - 3600,
        updated_at=time.time() - 1800,
        version=1,
        client_id="low_priority",
    )
    
    client_record = Record(
        data={
            "id": "conflict_record",
            "name": "Client Version",
            "value": 200,
        },
        created_at=time.time() - 3600,
        updated_at=time.time() - 1900,  # Older than server
        version=1,
        client_id="high_priority",
    )
    
    # Create conflict record
    conflict = ConflictRecord(
        record_id="conflict_record",
        server_record=server_record,
        client_record=client_record,
        field_conflicts={"name", "value"},
        table_name="test_table",
    )
    
    # Resolve with client priority
    resolved = conflict_resolver.resolve(conflict, ConflictStrategy.CLIENT_PRIORITY.value)
    
    # High priority client should win despite older timestamp
    assert resolved.data["name"] == "Client Version"
    assert resolved.data["value"] == 200


def test_manual_conflict_resolution(conflict_resolver: ConflictResolver) -> None:
    """Test manual conflict resolution."""
    # Create conflicting records
    server_record = Record(
        data={
            "id": "conflict_record",
            "name": "Server Version",
            "value": 100,
        },
        created_at=time.time() - 3600,
        updated_at=time.time() - 1800,
        version=1,
        client_id="server",
    )
    
    client_record = Record(
        data={
            "id": "conflict_record",
            "name": "Client Version",
            "value": 200,
        },
        created_at=time.time() - 3600,
        updated_at=time.time() - 1700,
        version=1,
        client_id="client1",
    )
    
    # Create conflict record
    conflict = ConflictRecord(
        record_id="conflict_record",
        server_record=server_record,
        client_record=client_record,
        field_conflicts={"name", "value"},
        table_name="test_table",
    )
    
    # Try to resolve with manual strategy (should not resolve)
    result = conflict_resolver.resolve(conflict, ConflictStrategy.MANUAL.value)
    assert result is None
    assert conflict.resolved_record is None
    
    # Manually resolve
    manually_resolved_data = {
        "id": "conflict_record",
        "name": "Manually Resolved Name",
        "value": 150,  # A compromise
    }
    
    manually_resolved = conflict_resolver.manual_resolve(
        conflict=conflict,
        resolved_data=manually_resolved_data,
        resolved_by="user",
    )
    
    # Check the result
    assert manually_resolved.data["name"] == "Manually Resolved Name"
    assert manually_resolved.data["value"] == 150
    assert conflict.resolved_record is not None
    assert conflict.resolution_strategy == "manual"
    assert conflict.resolved_by == "user"


@pytest.mark.asyncio
async def test_sync_client_session(db_engine: MobileDBEngine, mock_server_connection) -> None:
    """Test the client sync session."""
    # Create a client database
    client_db = MobileDBEngine()
    client_db.create_table(
        name="test_table",
        schema={
            "id": "string",
            "name": "string",
            "value": "integer",
            "updated_at": "string",
        },
        primary_key="id",
    )
    
    # Insert a client-side record
    client_db.insert(
        table_name="test_table",
        data={
            "id": "client_record",
            "name": "Client Record",
            "value": 300,
            "updated_at": "2023-01-03T12:00:00Z",
        },
        client_id="client1",
    )
    
    # Create a sync client session
    client_session = SyncClientSession(
        client_id="client1",
        server_connection=mock_server_connection,
        local_db=client_db,
    )
    
    # Start sync
    await client_session.start_sync()
    
    # Sync a table
    sync_result = await client_session.sync_table("test_table")
    
    # Verify local changes were pushed and server changes were pulled
    assert sync_result["pushed_changes"] > 0
    assert sync_result["pulled_changes"] > 0
    
    # Verify server records were added to client database
    server_record1 = client_db.get("test_table", "server_record1_test_table")
    assert server_record1["name"] == "Server Record 1 - test_table"
    
    # Complete sync
    complete_result = await client_session.complete_sync()
    assert complete_result["session_id"] == client_session.session_id
    
    # Verify session is no longer in progress
    assert client_session.in_progress is False