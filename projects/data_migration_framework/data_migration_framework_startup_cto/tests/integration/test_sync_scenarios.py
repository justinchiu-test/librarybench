"""Integration tests for synchronization scenarios."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

from pymigrate.sync.engine import SyncEngine
from pymigrate.models.config import (
    SyncConfig,
    ConflictResolutionStrategy,
    DatabaseConfig,
    DatabaseType,
)
from pymigrate.models.data import DataChange, ChangeType, SyncDirection
from pymigrate.validator.consistency import ConsistencyValidator


class TestSyncScenarios:
    """Integration tests for various sync scenarios."""
    
    @pytest.mark.asyncio
    async def test_bidirectional_sync_no_conflicts(self, sync_config):
        """Test bidirectional sync without conflicts."""
        engine = SyncEngine(sync_config)
        
        # Mock changes from both sides
        source_changes = [
            DataChange(
                id="s1",
                table_name="users",
                change_type=ChangeType.INSERT,
                timestamp=datetime.utcnow(),
                data={"id": 1, "name": "New User"},
                source_system="source",
            ),
            DataChange(
                id="s2",
                table_name="users",
                change_type=ChangeType.UPDATE,
                timestamp=datetime.utcnow(),
                data={"id": 2, "name": "Updated User"},
                source_system="source",
            ),
        ]
        
        target_changes = [
            DataChange(
                id="t1",
                table_name="orders",
                change_type=ChangeType.INSERT,
                timestamp=datetime.utcnow(),
                data={"id": 100, "user_id": 1, "total": 99.99},
                source_system="target",
            ),
        ]
        
        with patch.object(engine.change_detector, 'detect_changes', new_callable=AsyncMock) as mock_detect:
            # Return different changes for source and target
            mock_detect.side_effect = [source_changes, target_changes]
            
            with patch.object(engine, '_check_conflict', new_callable=AsyncMock) as mock_conflict:
                mock_conflict.return_value = None  # No conflicts
                
                with patch.object(engine, '_apply_change', new_callable=AsyncMock) as mock_apply:
                    status = await engine.sync_once(SyncDirection.BIDIRECTIONAL)
                    
                    # Verify all changes were applied
                    assert mock_apply.call_count == 3
                    assert status.records_processed == 3
                    assert status.records_synced == 3
                    assert status.conflicts_detected == 0
                    
    @pytest.mark.asyncio
    async def test_conflict_resolution_last_write_wins(self, source_db_config, target_db_config):
        """Test conflict resolution with last-write-wins strategy."""
        config = SyncConfig(
            source_db=source_db_config,
            target_db=target_db_config,
            conflict_resolution=ConflictResolutionStrategy.LAST_WRITE_WINS,
        )
        
        engine = SyncEngine(config)
        
        # Create conflicting changes
        older_change = DataChange(
            id="old",
            table_name="users",
            change_type=ChangeType.UPDATE,
            timestamp=datetime.utcnow() - timedelta(minutes=5),
            data={"id": 1, "name": "Old Name", "email": "old@example.com"},
            source_system="source",
        )
        
        newer_change = DataChange(
            id="new",
            table_name="users",
            change_type=ChangeType.UPDATE,
            timestamp=datetime.utcnow(),
            data={"id": 1, "name": "New Name", "email": "new@example.com"},
            source_system="target",
        )
        
        with patch.object(engine.change_detector, 'detect_changes', new_callable=AsyncMock) as mock_detect:
            mock_detect.return_value = [older_change]
            
            with patch.object(engine, '_check_conflict', new_callable=AsyncMock) as mock_conflict:
                mock_conflict.return_value = newer_change
                
                with patch.object(engine, '_apply_change', new_callable=AsyncMock) as mock_apply:
                    status = await engine.sync_once()
                    
                    # Verify newer change was applied
                    mock_apply.assert_called_with(newer_change, engine.target_conn)
                    assert status.records_synced == 1
                    assert status.conflicts_detected == 0  # Resolved automatically
                    
    @pytest.mark.asyncio
    async def test_manual_conflict_resolution(self, source_db_config, target_db_config):
        """Test manual conflict resolution strategy."""
        config = SyncConfig(
            source_db=source_db_config,
            target_db=target_db_config,
            conflict_resolution=ConflictResolutionStrategy.MANUAL,
        )
        
        engine = SyncEngine(config)
        
        # Create conflicting changes
        source_change = DataChange(
            id="src",
            table_name="users",
            change_type=ChangeType.UPDATE,
            timestamp=datetime.utcnow(),
            data={"id": 1, "name": "Source Name"},
            source_system="source",
        )
        
        target_change = DataChange(
            id="tgt",
            table_name="users",
            change_type=ChangeType.UPDATE,
            timestamp=datetime.utcnow(),
            data={"id": 1, "name": "Target Name"},
            source_system="target",
        )
        
        with patch.object(engine.change_detector, 'detect_changes', new_callable=AsyncMock) as mock_detect:
            mock_detect.return_value = [source_change]
            
            with patch.object(engine, '_check_conflict', new_callable=AsyncMock) as mock_conflict:
                mock_conflict.return_value = target_change
                
                with patch.object(engine, '_apply_change', new_callable=AsyncMock) as mock_apply:
                    with patch.object(engine, '_log_conflict', new_callable=AsyncMock) as mock_log:
                        status = await engine.sync_once()
                        
                        # Change should not be applied
                        mock_apply.assert_not_called()
                        
                        # Conflict should be logged
                        mock_log.assert_called_once()
                        
                        assert status.conflicts_detected == 1
                        assert status.records_synced == 0
                        
    @pytest.mark.asyncio
    async def test_sync_with_network_failure(self, sync_config):
        """Test sync behavior with network failures."""
        engine = SyncEngine(sync_config)
        
        changes = [
            DataChange(
                id="c1",
                table_name="users",
                change_type=ChangeType.INSERT,
                timestamp=datetime.utcnow(),
                data={"id": 1, "name": "User 1"},
                source_system="source",
            ),
            DataChange(
                id="c2",
                table_name="users",
                change_type=ChangeType.INSERT,
                timestamp=datetime.utcnow(),
                data={"id": 2, "name": "User 2"},
                source_system="source",
            ),
        ]
        
        with patch.object(engine.change_detector, 'detect_changes', new_callable=AsyncMock) as mock_detect:
            mock_detect.return_value = changes
            
            with patch.object(engine, '_check_conflict', new_callable=AsyncMock) as mock_conflict:
                mock_conflict.return_value = None
                
                with patch.object(engine, '_apply_change', new_callable=AsyncMock) as mock_apply:
                    # First change succeeds, second fails
                    mock_apply.side_effect = [None, Exception("Network error")]
                    
                    status = await engine.sync_once()
                    
                    assert status.records_processed == 2
                    assert status.records_synced == 1
                    assert len(status.errors) == 1
                    assert "Network error" in status.errors[0]
                    
    @pytest.mark.asyncio
    async def test_sync_with_validation(self, sync_config, mock_db_connection):
        """Test sync followed by consistency validation."""
        engine = SyncEngine(sync_config)
        validator = ConsistencyValidator(mock_db_connection, mock_db_connection)
        
        # Setup initial state
        mock_db_connection.get_all_tables.return_value = ["users"]
        mock_db_connection.get_table_count.return_value = 100
        
        # Perform sync
        with patch.object(engine.change_detector, 'detect_changes', new_callable=AsyncMock) as mock_detect:
            mock_detect.return_value = []  # No changes
            
            sync_status = await engine.sync_once()
            
        # Validate consistency
        consistency_report = await validator.validate_consistency(tables=["users"])
        
        assert sync_status.state.value == "completed"
        assert consistency_report.consistency_percentage == 100.0
        
    @pytest.mark.asyncio
    async def test_concurrent_sync_operations(self, sync_config):
        """Test handling of concurrent sync operations."""
        engine = SyncEngine(sync_config)
        
        # Start sync engine
        with patch.object(engine, '_sync_loop', new_callable=AsyncMock):
            await engine.start()
            
            # Try to start again
            await engine.start()  # Should handle gracefully
            
            assert engine._running is True
            
            # Stop engine
            await engine.stop()
            assert engine._running is False
            
    @pytest.mark.asyncio
    async def test_sync_performance_under_load(self, sync_config):
        """Test sync performance with large number of changes."""
        engine = SyncEngine(sync_config)
        
        # Generate many changes
        num_changes = 1000
        changes = []
        for i in range(num_changes):
            changes.append(
                DataChange(
                    id=f"change_{i}",
                    table_name="users",
                    change_type=ChangeType.UPDATE,
                    timestamp=datetime.utcnow(),
                    data={"id": i, "name": f"User {i}"},
                    source_system="source",
                )
            )
            
        with patch.object(engine.change_detector, 'detect_changes', new_callable=AsyncMock) as mock_detect:
            # Return changes in batches
            mock_detect.return_value = changes[:sync_config.batch_size]
            
            with patch.object(engine, '_check_conflict', new_callable=AsyncMock) as mock_conflict:
                mock_conflict.return_value = None
                
                with patch.object(engine, '_apply_change', new_callable=AsyncMock) as mock_apply:
                    mock_apply.return_value = None
                    
                    start_time = datetime.utcnow()
                    status = await engine.sync_once()
                    end_time = datetime.utcnow()
                    
                    # Verify batch processing
                    assert status.records_processed == sync_config.batch_size
                    
                    # Check performance
                    duration = (end_time - start_time).total_seconds()
                    assert duration < 5.0  # Should complete within 5 seconds
                    
    @pytest.mark.asyncio
    async def test_sync_recovery_after_failure(self, sync_config):
        """Test sync recovery after failures."""
        engine = SyncEngine(sync_config)
        
        # Track sync attempts
        sync_attempts = []
        
        async def mock_sync_once(*args, **kwargs):
            attempt = len(sync_attempts)
            sync_attempts.append(attempt)
            
            if attempt < 2:
                # First two attempts fail
                raise Exception("Database connection lost")
            else:
                # Third attempt succeeds
                return MagicMock(state="completed")
                
        with patch.object(engine, 'sync_once', new=mock_sync_once):
            with patch('asyncio.sleep', new_callable=AsyncMock):
                # Run sync loop for a few iterations
                engine._running = True
                
                try:
                    await asyncio.wait_for(engine._sync_loop(), timeout=0.5)
                except asyncio.TimeoutError:
                    pass
                    
                # Should have recovered after failures
                assert len(sync_attempts) >= 3
                
    @pytest.mark.asyncio
    async def test_priority_based_conflict_resolution(self, source_db_config, target_db_config):
        """Test priority-based conflict resolution with custom rules."""
        config = SyncConfig(
            source_db=source_db_config,
            target_db=target_db_config,
            conflict_resolution=ConflictResolutionStrategy.PRIORITY_BASED,
            priority_rules={
                "source": 50,
                "target": 100,  # Target has higher priority
                "users": 200,   # Table-specific priority
            },
        )
        
        engine = SyncEngine(config)
        
        # Create conflicting changes
        source_change = DataChange(
            id="src",
            table_name="users",
            change_type=ChangeType.UPDATE,
            timestamp=datetime.utcnow(),
            data={"id": 1, "name": "Source Name"},
            source_system="source",
        )
        
        target_change = DataChange(
            id="tgt",
            table_name="users",
            change_type=ChangeType.UPDATE,
            timestamp=datetime.utcnow() - timedelta(minutes=5),  # Older
            data={"id": 1, "name": "Target Name"},
            source_system="target",
        )
        
        with patch.object(engine.change_detector, 'detect_changes', new_callable=AsyncMock) as mock_detect:
            mock_detect.return_value = [source_change]
            
            with patch.object(engine, '_check_conflict', new_callable=AsyncMock) as mock_conflict:
                mock_conflict.return_value = target_change
                
                with patch.object(engine, '_apply_change', new_callable=AsyncMock) as mock_apply:
                    await engine.sync_once()
                    
                    # Target should win due to higher priority
                    mock_apply.assert_called_with(target_change, engine.target_conn)