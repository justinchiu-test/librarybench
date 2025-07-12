"""Change detection for database synchronization."""

import asyncio
import hashlib
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Set
from uuid import uuid4

from pymigrate.models.data import DataChange, ChangeType
from pymigrate.utils.database import DatabaseConnection

import logging

logger = logging.getLogger(__name__)


class ChangeDetector:
    """Detects changes in database for synchronization."""
    
    def __init__(self):
        """Initialize change detector."""
        self._last_sync_timestamps: Dict[str, datetime] = {}
        self._processed_changes: Set[str] = set()
        self._change_log_tables: Set[str] = set()
        
    async def detect_changes(
        self, 
        connection: DatabaseConnection, 
        batch_size: int = 1000
    ) -> List[DataChange]:
        """Detect changes in the database since last sync."""
        changes = []
        
        # Get all tracked tables
        tables = await connection.get_tracked_tables()
        
        for table in tables:
            # Check if table has change log
            if table in self._change_log_tables:
                # Use change data capture
                table_changes = await self._detect_from_change_log(
                    connection, table, batch_size
                )
            else:
                # Use timestamp-based detection
                table_changes = await self._detect_from_timestamps(
                    connection, table, batch_size
                )
                
            changes.extend(table_changes)
            
        return changes
        
    async def _detect_from_change_log(
        self,
        connection: DatabaseConnection,
        table: str,
        batch_size: int
    ) -> List[DataChange]:
        """Detect changes using change data capture logs."""
        changes = []
        
        # Get last processed log ID for this table
        last_log_id = await connection.get_last_processed_log_id(table)
        
        # Query change log
        log_entries = await connection.query_change_log(
            table, 
            after_id=last_log_id,
            limit=batch_size
        )
        
        for entry in log_entries:
            # Skip if already processed
            change_id = f"{table}:{entry['log_id']}"
            if change_id in self._processed_changes:
                continue
                
            change = DataChange(
                id=str(uuid4()),
                table_name=table,
                change_type=ChangeType(entry["operation"]),
                timestamp=entry["timestamp"],
                data=entry["data"],
                metadata={
                    "log_id": entry["log_id"],
                    "transaction_id": entry.get("transaction_id"),
                },
                source_system=connection.database_name,
                checksum=self._calculate_checksum(entry["data"])
            )
            
            changes.append(change)
            self._processed_changes.add(change_id)
            
        # Update last processed log ID
        if log_entries:
            await connection.update_last_processed_log_id(
                table, 
                log_entries[-1]["log_id"]
            )
            
        return changes
        
    async def _detect_from_timestamps(
        self,
        connection: DatabaseConnection,
        table: str,
        batch_size: int
    ) -> List[DataChange]:
        """Detect changes using timestamp comparison."""
        changes = []
        
        # Get last sync timestamp for this table
        last_sync = self._last_sync_timestamps.get(table)
        
        # Query for modified records
        modified_records = await connection.query_modified_records(
            table,
            since=last_sync,
            limit=batch_size
        )
        
        current_timestamp = datetime.utcnow()
        
        for record in modified_records:
            # Determine change type
            if last_sync and record.get("created_at", datetime.min) > last_sync:
                change_type = ChangeType.INSERT
            else:
                change_type = ChangeType.UPDATE
                
            change = DataChange(
                id=str(uuid4()),
                table_name=table,
                change_type=change_type,
                timestamp=record.get("updated_at", current_timestamp),
                data=record,
                metadata={
                    "detection_method": "timestamp",
                },
                source_system=connection.database_name,
                checksum=self._calculate_checksum(record)
            )
            
            changes.append(change)
            
        # Detect deletions (if supported by the database)
        if connection.supports_soft_delete:
            deleted_records = await connection.query_deleted_records(
                table,
                since=last_sync,
                limit=batch_size
            )
            
            for record in deleted_records:
                change = DataChange(
                    id=str(uuid4()),
                    table_name=table,
                    change_type=ChangeType.DELETE,
                    timestamp=record.get("deleted_at", current_timestamp),
                    data=record,
                    metadata={
                        "detection_method": "soft_delete",
                    },
                    source_system=connection.database_name,
                    checksum=self._calculate_checksum(record)
                )
                
                changes.append(change)
                
        # Update last sync timestamp
        self._last_sync_timestamps[table] = current_timestamp
        
        return changes
        
    async def setup_change_tracking(
        self, 
        connection: DatabaseConnection,
        tables: List[str]
    ) -> None:
        """Setup change tracking for specified tables."""
        for table in tables:
            try:
                # Check if database supports native CDC
                if await connection.supports_cdc():
                    await connection.enable_cdc(table)
                    self._change_log_tables.add(table)
                else:
                    # Ensure timestamp columns exist
                    await connection.ensure_timestamp_columns(table)
                    
                logger.info(f"Change tracking enabled for table: {table}")
                
            except Exception as e:
                logger.error(f"Failed to setup tracking for {table}: {e}")
                
    def _calculate_checksum(self, data: Dict[str, Any]) -> str:
        """Calculate checksum for data integrity."""
        # Remove system columns that might change
        cleaned_data = {
            k: v for k, v in data.items()
            if k not in ("created_at", "updated_at", "deleted_at", "_version")
        }
        
        sorted_data = json.dumps(cleaned_data, sort_keys=True, default=str)
        return hashlib.sha256(sorted_data.encode()).hexdigest()
        
    def reset_tracking(self, table: Optional[str] = None) -> None:
        """Reset change tracking state."""
        if table:
            self._last_sync_timestamps.pop(table, None)
            # Remove processed changes for this table
            self._processed_changes = {
                c for c in self._processed_changes
                if not c.startswith(f"{table}:")
            }
        else:
            self._last_sync_timestamps.clear()
            self._processed_changes.clear()
            
    def get_tracking_status(self) -> Dict[str, Any]:
        """Get current tracking status."""
        return {
            "tracked_tables": list(self._last_sync_timestamps.keys()),
            "change_log_tables": list(self._change_log_tables),
            "processed_changes_count": len(self._processed_changes),
            "last_sync_times": {
                table: ts.isoformat() 
                for table, ts in self._last_sync_timestamps.items()
            }
        }