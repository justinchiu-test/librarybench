"""Unit tests for Change Detector."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from pymigrate.sync.change_detector import ChangeDetector
from pymigrate.models.data import ChangeType


class TestChangeDetector:
    """Test cases for Change Detector."""
    
    @pytest.mark.asyncio
    async def test_change_detector_initialization(self):
        """Test change detector initialization."""
        detector = ChangeDetector()
        
        assert detector._last_sync_timestamps == {}
        assert detector._processed_changes == set()
        assert detector._change_log_tables == set()
        
    @pytest.mark.asyncio
    async def test_detect_changes_from_change_log(self, mock_db_connection):
        """Test change detection using CDC logs."""
        detector = ChangeDetector()
        detector._change_log_tables.add("users")
        
        # Mock change log entries
        mock_db_connection.get_tracked_tables.return_value = ["users"]
        mock_db_connection.get_last_processed_log_id.return_value = 100
        mock_db_connection.query_change_log.return_value = [
            {
                "log_id": 101,
                "operation": "insert",
                "timestamp": datetime.utcnow(),
                "data": {"id": 1, "name": "New User"},
                "transaction_id": "tx_123",
            },
            {
                "log_id": 102,
                "operation": "update",
                "timestamp": datetime.utcnow(),
                "data": {"id": 2, "name": "Updated User"},
                "transaction_id": "tx_124",
            },
        ]
        
        changes = await detector.detect_changes(mock_db_connection, batch_size=10)
        
        assert len(changes) == 2
        assert changes[0].change_type == ChangeType.INSERT
        assert changes[1].change_type == ChangeType.UPDATE
        assert "users:101" in detector._processed_changes
        assert "users:102" in detector._processed_changes
        
    @pytest.mark.asyncio
    async def test_detect_changes_from_timestamps(self, mock_db_connection):
        """Test change detection using timestamp comparison."""
        detector = ChangeDetector()
        
        # Mock timestamp-based detection
        mock_db_connection.get_tracked_tables.return_value = ["orders"]
        mock_db_connection.query_modified_records.return_value = [
            {
                "id": 1,
                "order_id": "ORD001",
                "created_at": datetime.utcnow() - timedelta(hours=1),
                "updated_at": datetime.utcnow(),
            },
            {
                "id": 2,
                "order_id": "ORD002",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
        ]
        mock_db_connection.supports_soft_delete = True
        mock_db_connection.query_deleted_records.return_value = [
            {
                "id": 3,
                "order_id": "ORD003",
                "deleted_at": datetime.utcnow(),
            }
        ]
        
        changes = await detector.detect_changes(mock_db_connection)
        
        assert len(changes) == 3
        assert any(c.change_type == ChangeType.DELETE for c in changes)
        assert "orders" in detector._last_sync_timestamps
        
    @pytest.mark.asyncio
    async def test_setup_change_tracking(self, mock_db_connection):
        """Test setting up change tracking for tables."""
        detector = ChangeDetector()
        
        # Mock CDC support
        mock_db_connection.supports_cdc.return_value = True
        mock_db_connection.enable_cdc.return_value = None
        
        await detector.setup_change_tracking(mock_db_connection, ["users", "orders"])
        
        assert "users" in detector._change_log_tables
        assert "orders" in detector._change_log_tables
        mock_db_connection.enable_cdc.assert_called()
        
    @pytest.mark.asyncio
    async def test_setup_change_tracking_without_cdc(self, mock_db_connection):
        """Test setting up change tracking without CDC support."""
        detector = ChangeDetector()
        
        # Mock no CDC support
        mock_db_connection.supports_cdc.return_value = False
        mock_db_connection.ensure_timestamp_columns.return_value = None
        
        await detector.setup_change_tracking(mock_db_connection, ["products"])
        
        assert "products" not in detector._change_log_tables
        mock_db_connection.ensure_timestamp_columns.assert_called_with("products")
        
    def test_checksum_calculation(self):
        """Test checksum calculation for data integrity."""
        detector = ChangeDetector()
        
        data1 = {"id": 1, "name": "Test", "value": 100}
        data2 = {"id": 1, "name": "Test", "value": 100}
        data3 = {"id": 1, "name": "Test", "value": 200}
        
        checksum1 = detector._calculate_checksum(data1)
        checksum2 = detector._calculate_checksum(data2)
        checksum3 = detector._calculate_checksum(data3)
        
        # Same data should have same checksum
        assert checksum1 == checksum2
        
        # Different data should have different checksum
        assert checksum1 != checksum3
        
    def test_checksum_excludes_system_columns(self):
        """Test that checksum excludes system columns."""
        detector = ChangeDetector()
        
        data_with_timestamps = {
            "id": 1,
            "name": "Test",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "_version": 1,
        }
        
        data_without_timestamps = {
            "id": 1,
            "name": "Test",
        }
        
        checksum1 = detector._calculate_checksum(data_with_timestamps)
        checksum2 = detector._calculate_checksum(data_without_timestamps)
        
        # Should have same checksum since system columns are excluded
        assert checksum1 == checksum2
        
    def test_reset_tracking(self):
        """Test resetting change tracking state."""
        detector = ChangeDetector()
        
        # Add some state
        detector._last_sync_timestamps["users"] = datetime.utcnow()
        detector._last_sync_timestamps["orders"] = datetime.utcnow()
        detector._processed_changes.add("users:1")
        detector._processed_changes.add("users:2")
        detector._processed_changes.add("orders:1")
        
        # Reset specific table
        detector.reset_tracking("users")
        
        assert "users" not in detector._last_sync_timestamps
        assert "orders" in detector._last_sync_timestamps
        assert "users:1" not in detector._processed_changes
        assert "users:2" not in detector._processed_changes
        assert "orders:1" in detector._processed_changes
        
        # Reset all
        detector.reset_tracking()
        
        assert len(detector._last_sync_timestamps) == 0
        assert len(detector._processed_changes) == 0
        
    def test_get_tracking_status(self):
        """Test getting tracking status."""
        detector = ChangeDetector()
        
        # Add some tracking state
        now = datetime.utcnow()
        detector._last_sync_timestamps["users"] = now
        detector._last_sync_timestamps["orders"] = now - timedelta(hours=1)
        detector._change_log_tables.add("users")
        detector._processed_changes.update(["users:1", "users:2", "orders:1"])
        
        status = detector.get_tracking_status()
        
        assert "users" in status["tracked_tables"]
        assert "orders" in status["tracked_tables"]
        assert "users" in status["change_log_tables"]
        assert status["processed_changes_count"] == 3
        assert "last_sync_times" in status
        
    @pytest.mark.asyncio
    async def test_skip_already_processed_changes(self, mock_db_connection):
        """Test that already processed changes are skipped."""
        detector = ChangeDetector()
        detector._change_log_tables.add("users")
        
        # Add already processed change
        detector._processed_changes.add("users:101")
        
        mock_db_connection.get_tracked_tables.return_value = ["users"]
        mock_db_connection.get_last_processed_log_id.return_value = 100
        mock_db_connection.query_change_log.return_value = [
            {
                "log_id": 101,  # Already processed
                "operation": "insert",
                "timestamp": datetime.utcnow(),
                "data": {"id": 1},
                "transaction_id": "tx_123",
            },
            {
                "log_id": 102,  # New change
                "operation": "update",
                "timestamp": datetime.utcnow(),
                "data": {"id": 2},
                "transaction_id": "tx_124",
            },
        ]
        
        changes = await detector.detect_changes(mock_db_connection)
        
        # Should only return the new change
        assert len(changes) == 1
        assert changes[0].metadata["log_id"] == 102
        
    @pytest.mark.asyncio
    async def test_detect_insertions_vs_updates(self, mock_db_connection):
        """Test differentiating between insertions and updates."""
        detector = ChangeDetector()
        
        # Set last sync time to 1 hour ago
        last_sync = datetime.utcnow() - timedelta(hours=1)
        detector._last_sync_timestamps["products"] = last_sync
        
        mock_db_connection.get_tracked_tables.return_value = ["products"]
        mock_db_connection.query_modified_records.return_value = [
            {
                "id": 1,
                "name": "Product 1",
                "created_at": datetime.utcnow() - timedelta(hours=2),  # Before last sync
                "updated_at": datetime.utcnow(),  # After last sync
            },
            {
                "id": 2,
                "name": "Product 2",
                "created_at": datetime.utcnow() - timedelta(minutes=30),  # After last sync
                "updated_at": datetime.utcnow() - timedelta(minutes=30),
            },
        ]
        
        changes = await detector.detect_changes(mock_db_connection)
        
        assert len(changes) == 2
        
        # First should be UPDATE (created before last sync)
        update_change = next(c for c in changes if c.data["id"] == 1)
        assert update_change.change_type == ChangeType.UPDATE
        
        # Second should be INSERT (created after last sync)
        insert_change = next(c for c in changes if c.data["id"] == 2)
        assert insert_change.change_type == ChangeType.INSERT