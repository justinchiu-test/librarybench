"""Unit tests for Sync Engine."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from pymigrate.sync.engine import SyncEngine
from pymigrate.sync.conflict_resolver import ResolutionResult
from pymigrate.models.data import (
    DataChange,
    ChangeType,
    SyncDirection,
    SyncState,
    ConflictReport,
)
from pymigrate.models.config import ConflictResolutionStrategy


class TestSyncEngine:
    """Test cases for SyncEngine."""
    
    @pytest.mark.asyncio
    async def test_sync_engine_initialization(self, sync_config):
        """Test sync engine initialization."""
        engine = SyncEngine(sync_config)
        
        assert engine.config == sync_config
        assert engine._running is False
        assert engine._sync_task is None
        assert engine._sync_history == []
        
    @pytest.mark.asyncio
    async def test_start_stop_engine(self, sync_config):
        """Test starting and stopping sync engine."""
        engine = SyncEngine(sync_config)
        
        # Mock the sync loop to prevent actual execution
        with patch.object(engine, '_sync_loop', new_callable=AsyncMock):
            await engine.start()
            assert engine._running is True
            assert engine._sync_task is not None
            
            await engine.stop()
            assert engine._running is False
            
    @pytest.mark.asyncio
    async def test_sync_once_bidirectional(self, sync_config, sample_data_change):
        """Test single bidirectional sync cycle."""
        engine = SyncEngine(sync_config)
        
        # Mock change detection and sync
        with patch.object(engine.change_detector, 'detect_changes', new_callable=AsyncMock) as mock_detect:
            mock_detect.return_value = [sample_data_change]
            
            with patch.object(engine, '_apply_change', new_callable=AsyncMock):
                status = await engine.sync_once(SyncDirection.BIDIRECTIONAL)
                
                assert status.state == SyncState.COMPLETED
                assert status.direction == SyncDirection.BIDIRECTIONAL
                assert status.records_processed >= 0
                assert status.completed_at is not None
                
    @pytest.mark.asyncio
    async def test_conflict_detection(self, sync_config, sample_data_change):
        """Test conflict detection during sync."""
        engine = SyncEngine(sync_config)
        
        # Create conflicting change
        target_change = DataChange(
            id="change_456",
            table_name="users",
            change_type=ChangeType.UPDATE,
            timestamp=datetime.utcnow() + timedelta(minutes=1),
            data={
                "id": 1,
                "name": "Jane Doe",  # Different name
                "email": "jane@example.com",  # Different email
            },
            source_system="target",
            checksum="def456",
        )
        
        # Mock conflict check to return conflict
        with patch.object(engine, '_check_conflict', new_callable=AsyncMock) as mock_check:
            mock_check.return_value = target_change
            
            # Mock conflict resolution
            resolution = ResolutionResult(
                resolved=True,
                winning_change=sample_data_change,
                details={"strategy": "last_write_wins"}
            )
            
            with patch.object(engine.conflict_resolver, 'resolve', new_callable=AsyncMock) as mock_resolve:
                mock_resolve.return_value = resolution
                
                # Test conflict handling
                with patch.object(engine, '_apply_change', new_callable=AsyncMock):
                    with patch.object(engine.change_detector, 'detect_changes', new_callable=AsyncMock) as mock_detect:
                        mock_detect.return_value = [sample_data_change]
                        
                        status = await engine.sync_once()
                        
                        # Verify conflict was detected and resolved
                        mock_check.assert_called()
                        mock_resolve.assert_called_with(
                            sample_data_change,
                            target_change,
                            None  # No priority rules in default config
                        )
                        
    @pytest.mark.asyncio
    async def test_last_write_wins_resolution(self, sync_config, sample_data_change):
        """Test last-write-wins conflict resolution."""
        engine = SyncEngine(sync_config)
        
        older_change = DataChange(
            id="old_change",
            table_name="users",
            change_type=ChangeType.UPDATE,
            timestamp=datetime.utcnow() - timedelta(hours=1),
            data={"id": 1, "name": "Old Name"},
            source_system="target",
            checksum="old123",
        )
        
        newer_change = DataChange(
            id="new_change",
            table_name="users",
            change_type=ChangeType.UPDATE,
            timestamp=datetime.utcnow(),
            data={"id": 1, "name": "New Name"},
            source_system="source",
            checksum="new456",
        )
        
        result = await engine.conflict_resolver.resolve(
            newer_change,
            older_change,
            None
        )
        
        assert result.resolved is True
        assert result.winning_change == newer_change
        assert result.details["strategy"] == "last_write_wins"
        assert result.details["reason"] == "source_newer"
        
    @pytest.mark.asyncio
    async def test_priority_based_resolution(self, source_db_config, target_db_config):
        """Test priority-based conflict resolution."""
        config = SyncConfig(
            source_db=source_db_config,
            target_db=target_db_config,
            conflict_resolution=ConflictResolutionStrategy.PRIORITY_BASED,
            priority_rules={"source": 100, "target": 50},
        )
        
        engine = SyncEngine(config)
        
        source_change = DataChange(
            id="source_change",
            table_name="users",
            change_type=ChangeType.UPDATE,
            timestamp=datetime.utcnow(),
            data={"id": 1, "name": "Source Name"},
            source_system="source",
            checksum="src123",
        )
        
        target_change = DataChange(
            id="target_change",
            table_name="users",
            change_type=ChangeType.UPDATE,
            timestamp=datetime.utcnow(),
            data={"id": 1, "name": "Target Name"},
            source_system="target",
            checksum="tgt456",
        )
        
        result = await engine.conflict_resolver.resolve(
            source_change,
            target_change,
            config.priority_rules
        )
        
        assert result.resolved is True
        assert result.winning_change == source_change
        assert result.details["reason"] == "source_higher_priority"
        
    @pytest.mark.asyncio
    async def test_sync_performance_metrics(self, sync_config):
        """Test sync performance metrics calculation."""
        engine = SyncEngine(sync_config)
        
        # Add some sync history
        for i in range(5):
            status = await engine.sync_once()
            status.records_processed = 100
            status.records_synced = 95
            status.conflicts_detected = 5
            status.completed_at = status.started_at + timedelta(seconds=2)
            
        metrics = engine.get_performance_metrics()
        
        assert metrics["total_records_processed"] == 500
        assert metrics["total_records_synced"] == 475
        assert metrics["total_conflicts"] == 25
        assert metrics["success_rate"] == 95.0
        assert metrics["sync_count"] == 5
        assert "average_sync_time_ms" in metrics
        
    @pytest.mark.asyncio
    async def test_sync_with_errors(self, sync_config):
        """Test sync behavior with errors."""
        engine = SyncEngine(sync_config)
        
        # Mock change detection to raise error
        with patch.object(engine.change_detector, 'detect_changes', new_callable=AsyncMock) as mock_detect:
            mock_detect.side_effect = Exception("Database connection error")
            
            status = await engine.sync_once()
            
            assert status.state == SyncState.FAILED
            assert len(status.errors) > 0
            assert "Database connection error" in status.errors[0]
            
    @pytest.mark.asyncio
    async def test_checksum_calculation(self, sync_config):
        """Test data checksum calculation."""
        engine = SyncEngine(sync_config)
        
        data1 = {"id": 1, "name": "Test", "value": 100}
        data2 = {"id": 1, "name": "Test", "value": 100}
        data3 = {"id": 1, "name": "Test", "value": 200}
        
        checksum1 = engine._calculate_checksum(data1)
        checksum2 = engine._calculate_checksum(data2)
        checksum3 = engine._calculate_checksum(data3)
        
        # Same data should have same checksum
        assert checksum1 == checksum2
        
        # Different data should have different checksum
        assert checksum1 != checksum3
        
    @pytest.mark.asyncio
    async def test_sync_history_limit(self, sync_config):
        """Test sync history is limited."""
        engine = SyncEngine(sync_config)
        
        # Add many sync operations
        for i in range(150):
            status = await engine.sync_once()
            
        history = engine.get_sync_history(limit=100)
        
        assert len(history) == 100
        assert all(isinstance(s.sync_id, str) for s in history)