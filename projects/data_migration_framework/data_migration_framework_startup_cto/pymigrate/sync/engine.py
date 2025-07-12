"""Bi-directional synchronization engine."""

import asyncio
import hashlib
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from uuid import uuid4

from pymigrate.models.config import SyncConfig, ConflictResolutionStrategy
from pymigrate.models.data import (
    DataChange,
    SyncStatus,
    SyncDirection,
    SyncState,
    ConflictReport,
)
from pymigrate.sync.change_detector import ChangeDetector
from pymigrate.sync.conflict_resolver import ConflictResolver
from pymigrate.utils.database import DatabaseConnection

logger = logging.getLogger(__name__)


class SyncEngine:
    """Bi-directional synchronization engine with conflict resolution."""
    
    def __init__(self, config: SyncConfig):
        """Initialize sync engine with configuration."""
        self.config = config
        self.source_conn = DatabaseConnection(config.source_db)
        self.target_conn = DatabaseConnection(config.target_db)
        self.change_detector = ChangeDetector()
        self.conflict_resolver = ConflictResolver(config.conflict_resolution)
        self._sync_task: Optional[asyncio.Task] = None
        self._running = False
        self._sync_history: List[SyncStatus] = []
        
    async def start(self) -> None:
        """Start the synchronization engine."""
        if self._running:
            logger.warning("Sync engine already running")
            return
            
        self._running = True
        self._sync_task = asyncio.create_task(self._sync_loop())
        logger.info("Sync engine started")
        
    async def stop(self) -> None:
        """Stop the synchronization engine."""
        self._running = False
        if self._sync_task:
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass
        logger.info("Sync engine stopped")
        
    async def sync_once(self, direction: SyncDirection = SyncDirection.BIDIRECTIONAL) -> SyncStatus:
        """Perform a single synchronization cycle."""
        sync_id = str(uuid4())
        status = SyncStatus(
            sync_id=sync_id,
            direction=direction,
            state=SyncState.IN_PROGRESS,
            started_at=datetime.utcnow(),
        )
        
        try:
            if direction in (SyncDirection.SOURCE_TO_TARGET, SyncDirection.BIDIRECTIONAL):
                await self._sync_direction(
                    self.source_conn, 
                    self.target_conn, 
                    "source", 
                    status
                )
                
            if direction in (SyncDirection.TARGET_TO_SOURCE, SyncDirection.BIDIRECTIONAL):
                await self._sync_direction(
                    self.target_conn, 
                    self.source_conn, 
                    "target", 
                    status
                )
                
            status.state = SyncState.COMPLETED
            status.completed_at = datetime.utcnow()
            
        except Exception as e:
            status.state = SyncState.FAILED
            status.errors.append(str(e))
            logger.error(f"Sync failed: {e}")
            raise
            
        finally:
            self._sync_history.append(status)
            
        return status
        
    async def _sync_loop(self) -> None:
        """Main synchronization loop."""
        while self._running:
            try:
                await self.sync_once()
                await asyncio.sleep(self.config.sync_interval_ms / 1000.0)
            except Exception as e:
                logger.error(f"Error in sync loop: {e}")
                await asyncio.sleep(5)  # Back off on error
                
    async def _sync_direction(
        self, 
        source_conn: DatabaseConnection, 
        target_conn: DatabaseConnection,
        source_name: str,
        status: SyncStatus
    ) -> None:
        """Sync changes from source to target."""
        # Detect changes
        changes = await self.change_detector.detect_changes(
            source_conn, 
            self.config.batch_size
        )
        
        for change in changes:
            try:
                # Check for conflicts
                conflict = await self._check_conflict(change, target_conn)
                
                if conflict:
                    # Resolve conflict
                    resolution = await self.conflict_resolver.resolve(
                        change, 
                        conflict,
                        self.config.priority_rules
                    )
                    
                    if resolution.resolved:
                        await self._apply_change(resolution.winning_change, target_conn)
                        status.records_synced += 1
                    else:
                        status.conflicts_detected += 1
                        # Log unresolved conflict
                        await self._log_conflict(change, conflict, resolution)
                else:
                    # No conflict, apply change
                    await self._apply_change(change, target_conn)
                    status.records_synced += 1
                    
                status.records_processed += 1
                
            except Exception as e:
                logger.error(f"Error processing change {change.id}: {e}")
                status.errors.append(f"Change {change.id}: {str(e)}")
                
    async def _check_conflict(
        self, 
        change: DataChange, 
        target_conn: DatabaseConnection
    ) -> Optional[DataChange]:
        """Check if a change conflicts with existing data."""
        # Get current data from target
        target_data = await target_conn.get_record(
            change.table_name, 
            change.data.get("id")
        )
        
        if not target_data:
            return None
            
        # Calculate checksums
        source_checksum = self._calculate_checksum(change.data)
        target_checksum = self._calculate_checksum(target_data)
        
        if source_checksum != target_checksum:
            # Data has been modified in target
            return DataChange(
                id=str(uuid4()),
                table_name=change.table_name,
                change_type=change.change_type,
                timestamp=datetime.utcnow(),
                data=target_data,
                source_system="target",
                checksum=target_checksum
            )
            
        return None
        
    async def _apply_change(
        self, 
        change: DataChange, 
        target_conn: DatabaseConnection
    ) -> None:
        """Apply a change to the target database."""
        if change.change_type == "insert":
            await target_conn.insert(change.table_name, change.data)
        elif change.change_type == "update":
            await target_conn.update(
                change.table_name, 
                change.data.get("id"), 
                change.data
            )
        elif change.change_type == "delete":
            await target_conn.delete(change.table_name, change.data.get("id"))
            
    async def _log_conflict(
        self,
        source_change: DataChange,
        target_change: DataChange,
        resolution: Any
    ) -> None:
        """Log an unresolved conflict."""
        conflict = ConflictReport(
            id=str(uuid4()),
            table_name=source_change.table_name,
            record_id=str(source_change.data.get("id")),
            source_change=source_change,
            target_change=target_change,
            detected_at=datetime.utcnow(),
            resolution_strategy=self.config.conflict_resolution.value,
            resolved=resolution.resolved,
            resolution_details=resolution.details if hasattr(resolution, "details") else None
        )
        
        if self.config.enable_audit_log:
            await self._write_audit_log(conflict)
            
    async def _write_audit_log(self, conflict: ConflictReport) -> None:
        """Write conflict to audit log."""
        # In a real implementation, this would write to a persistent audit log
        logger.info(f"Conflict detected: {conflict.model_dump()}")
        
    def _calculate_checksum(self, data: Dict[str, Any]) -> str:
        """Calculate checksum for data."""
        # Sort keys for consistent hashing
        sorted_data = json.dumps(data, sort_keys=True)
        return hashlib.sha256(sorted_data.encode()).hexdigest()
        
    def get_sync_history(self, limit: int = 100) -> List[SyncStatus]:
        """Get synchronization history."""
        return self._sync_history[-limit:]
        
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        if not self._sync_history:
            return {}
            
        recent_syncs = self._sync_history[-100:]
        
        total_records = sum(s.records_processed for s in recent_syncs)
        total_synced = sum(s.records_synced for s in recent_syncs)
        total_conflicts = sum(s.conflicts_detected for s in recent_syncs)
        
        sync_times = [
            (s.completed_at - s.started_at).total_seconds()
            for s in recent_syncs
            if s.completed_at
        ]
        
        return {
            "total_records_processed": total_records,
            "total_records_synced": total_synced,
            "total_conflicts": total_conflicts,
            "success_rate": (total_synced / total_records * 100) if total_records > 0 else 0,
            "average_sync_time_ms": sum(sync_times) / len(sync_times) * 1000 if sync_times else 0,
            "sync_count": len(recent_syncs),
        }