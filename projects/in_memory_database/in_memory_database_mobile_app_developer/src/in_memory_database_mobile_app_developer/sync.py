"""Differential sync protocol implementation for MobileSyncDB."""

import time
import hashlib
import json
import uuid
import logging
from typing import Dict, List, Any, Optional, Tuple, Set, Union, Callable

from .database import MobileDBEngine, Record
from .exceptions import SyncError, ConflictError, NetworkError, CorruptDataError


logger = logging.getLogger(__name__)


class SyncBatch:
    """Represents a batch of changes for synchronization."""

    def __init__(
        self,
        table_name: str,
        records: List[Tuple[str, Record]],
        checksum: Optional[str] = None,
        batch_id: Optional[str] = None,
        is_last_batch: bool = False,
    ):
        """Initialize a sync batch."""
        self.table_name = table_name
        self.records = records
        self.batch_id = batch_id or str(uuid.uuid4())
        self.checksum = checksum or self._generate_checksum()
        self.created_at = time.time()
        self.is_last_batch = is_last_batch

    def _generate_checksum(self) -> str:
        """Generate a checksum for the batch data."""
        data_str = ""
        for pk, record in self.records:
            data_str += f"{pk}:{record.version}:{record.updated_at}"
        return hashlib.sha256(data_str.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Convert the batch to a dictionary for transfer."""
        return {
            "batch_id": self.batch_id,
            "table_name": self.table_name,
            "records": [
                {
                    "pk": pk,
                    "data": record.data,
                    "version": record.version,
                    "updated_at": record.updated_at,
                    "created_at": record.created_at,
                    "is_deleted": record.is_deleted,
                    "client_id": record.client_id,
                    "conflict_info": record.conflict_info,
                }
                for pk, record in self.records
            ],
            "checksum": self.checksum,
            "created_at": self.created_at,
            "is_last_batch": self.is_last_batch,
        }

    @classmethod
    def from_dict(cls, batch_dict: Dict[str, Any]) -> "SyncBatch":
        """Create a SyncBatch from a dictionary."""
        records = []
        for record_dict in batch_dict["records"]:
            pk = record_dict["pk"]
            record = Record(
                data=record_dict["data"],
                version=record_dict["version"],
                updated_at=record_dict["updated_at"],
                created_at=record_dict["created_at"],
                is_deleted=record_dict.get("is_deleted", False),
                client_id=record_dict.get("client_id"),
                conflict_info=record_dict.get("conflict_info"),
            )
            records.append((pk, record))

        return cls(
            table_name=batch_dict["table_name"],
            records=records,
            checksum=batch_dict["checksum"],
            batch_id=batch_dict["batch_id"],
            is_last_batch=batch_dict.get("is_last_batch", False),
        )

    def verify_checksum(self) -> bool:
        """Verify that the checksum matches the data."""
        calculated = self._generate_checksum()
        return calculated == self.checksum


class SyncSession:
    """Represents a synchronization session between client and server."""

    def __init__(
        self,
        client_id: str,
        db: MobileDBEngine,
        batch_size: int = 100,
        resume_token: Optional[str] = None,
    ):
        """Initialize a sync session."""
        self.client_id = client_id
        self.db = db
        self.batch_size = batch_size
        self.session_id = resume_token or str(uuid.uuid4())
        self.started_at = time.time()
        self.last_activity = time.time()
        self.table_progress: Dict[str, int] = {}  # tracks how many records sent for each table
        self.completed_tables: Set[str] = set()
        self.in_progress = False
        self.completed = False
        self.error: Optional[str] = None
        
        # Register client if not already registered
        if not db.get_client_session(client_id):
            db.register_client(client_id)

    def start_sync(self) -> Dict[str, Any]:
        """Start a new synchronization session."""
        if self.in_progress:
            raise SyncError("Sync session already in progress")
        
        self.in_progress = True
        self.last_activity = time.time()
        
        return {
            "session_id": self.session_id,
            "started_at": self.started_at,
            "client_id": self.client_id,
        }

    def get_next_batch(self, table_name: str) -> Optional[SyncBatch]:
        """Get the next batch of changes for a table."""
        if not self.in_progress:
            raise SyncError("Sync session not in progress")
        
        self.last_activity = time.time()
        
        # Get the client's last sync timestamp for this table
        last_sync = self.db.get_client_sync_state(self.client_id, table_name) or 0.0
        
        # Get changes since last sync
        all_changes = self.db.get_changes_since(table_name, last_sync, self.client_id)
        
        # Check if we've already sent some records for this table
        offset = self.table_progress.get(table_name, 0)
        
        # Get the next batch of records
        batch_records = all_changes[offset:offset + self.batch_size]
        
        if not batch_records:
            # No more changes for this table
            self.completed_tables.add(table_name)
            return None
        
        # Update progress for this table
        self.table_progress[table_name] = offset + len(batch_records)
        
        # Check if this is the last batch for this table
        is_last_batch = offset + len(batch_records) >= len(all_changes)
        
        # Create the batch
        batch = SyncBatch(
            table_name=table_name,
            records=batch_records,
            is_last_batch=is_last_batch,
        )
        
        return batch

    def apply_batch(self, batch: SyncBatch) -> Dict[str, Any]:
        """Apply a batch of changes from the client."""
        if not self.in_progress:
            raise SyncError("Sync session not in progress")
        
        self.last_activity = time.time()
        
        # Verify the batch checksum
        if not batch.verify_checksum():
            raise CorruptDataError("Batch checksum verification failed")
        
        # Get the table
        table = self.db.get_table(batch.table_name)
        
        # Track conflicts that occurred during application
        conflicts = []
        applied_count = 0
        
        # Process each record in the batch
        for pk, record in batch.records:
            try:
                # Check if the record exists
                try:
                    existing = table.get_with_metadata(pk)
                    
                    # Record exists, check for conflicts
                    if existing.version > record.version:
                        # Local version is newer, potential conflict
                        conflicts.append({
                            "pk": pk,
                            "client_version": record.version,
                            "server_version": existing.version,
                            "client_updated_at": record.updated_at,
                            "server_updated_at": existing.updated_at,
                        })
                        continue
                    
                    # Update the existing record
                    table.update(pk, record.data, self.client_id)
                    applied_count += 1
                
                except RecordNotFoundError:
                    # Record doesn't exist, insert it
                    table.insert(record.data, self.client_id)
                    applied_count += 1
            
            except Exception as e:
                logger.error(f"Error applying change for record {pk}: {str(e)}")
                conflicts.append({
                    "pk": pk,
                    "error": str(e),
                })
        
        # Update the client's sync state for this table
        if batch.is_last_batch:
            self.db.update_client_sync_state(self.client_id, batch.table_name, time.time())
            self.completed_tables.add(batch.table_name)
        
        # Check if all tables are complete
        if self.check_all_tables_complete():
            self.completed = True
            self.in_progress = False
        
        return {
            "batch_id": batch.batch_id,
            "applied_count": applied_count,
            "conflicts": conflicts,
            "table_name": batch.table_name,
            "is_complete": batch.is_last_batch,
        }

    def check_all_tables_complete(self) -> bool:
        """Check if all tables have been synchronized."""
        all_tables = set(self.db.tables.keys())
        return self.completed_tables == all_tables

    def complete_sync(self) -> Dict[str, Any]:
        """Complete the synchronization session."""
        if not self.in_progress:
            raise SyncError("Sync session not in progress")
        
        self.in_progress = False
        self.completed = True
        self.last_activity = time.time()
        
        total_duration = self.last_activity - self.started_at
        
        return {
            "session_id": self.session_id,
            "client_id": self.client_id,
            "started_at": self.started_at,
            "completed_at": self.last_activity,
            "duration": total_duration,
            "tables_synced": list(self.completed_tables),
        }

    def get_resume_info(self) -> Dict[str, Any]:
        """Get information for resuming a sync session."""
        return {
            "session_id": self.session_id,
            "client_id": self.client_id,
            "started_at": self.started_at,
            "last_activity": self.last_activity,
            "table_progress": self.table_progress,
            "completed_tables": list(self.completed_tables),
        }


class SyncManager:
    """Manages synchronization between server and clients."""

    def __init__(self, db: MobileDBEngine, batch_size: int = 100, session_timeout: int = 3600):
        """Initialize the sync manager."""
        self.db = db
        self.batch_size = batch_size
        self.session_timeout = session_timeout  # in seconds
        self.active_sessions: Dict[str, SyncSession] = {}

    def start_sync_session(self, client_id: str, resume_token: Optional[str] = None) -> Dict[str, Any]:
        """Start a new synchronization session for a client."""
        # Check if there's an existing session to resume
        if resume_token and resume_token in self.active_sessions:
            session = self.active_sessions[resume_token]
            if session.client_id != client_id:
                raise SyncError("Resume token does not match client ID")
            if time.time() - session.last_activity > self.session_timeout:
                del self.active_sessions[resume_token]
                session = SyncSession(client_id, self.db, self.batch_size)
            else:
                return session.start_sync()
        else:
            session = SyncSession(client_id, self.db, self.batch_size, resume_token)
        
        self.active_sessions[session.session_id] = session
        return session.start_sync()

    def get_next_batch(self, session_id: str, table_name: str) -> Optional[Dict[str, Any]]:
        """Get the next batch of changes for a table."""
        if session_id not in self.active_sessions:
            raise SyncError("Invalid or expired session ID")
        
        session = self.active_sessions[session_id]
        
        if time.time() - session.last_activity > self.session_timeout:
            del self.active_sessions[session_id]
            raise SyncError("Sync session has expired")
        
        batch = session.get_next_batch(table_name)
        if batch is None:
            return None
        
        return batch.to_dict()

    def apply_batch(self, session_id: str, batch_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a batch of changes from a client."""
        if session_id not in self.active_sessions:
            raise SyncError("Invalid or expired session ID")
        
        session = self.active_sessions[session_id]
        
        if time.time() - session.last_activity > self.session_timeout:
            del self.active_sessions[session_id]
            raise SyncError("Sync session has expired")
        
        batch = SyncBatch.from_dict(batch_dict)
        return session.apply_batch(batch)

    def complete_sync(self, session_id: str) -> Dict[str, Any]:
        """Complete a synchronization session."""
        if session_id not in self.active_sessions:
            raise SyncError("Invalid or expired session ID")
        
        session = self.active_sessions[session_id]
        
        if time.time() - session.last_activity > self.session_timeout:
            del self.active_sessions[session_id]
            raise SyncError("Sync session has expired")
        
        result = session.complete_sync()
        del self.active_sessions[session_id]
        return result

    def get_sync_status(self, session_id: str) -> Dict[str, Any]:
        """Get the status of a synchronization session."""
        if session_id not in self.active_sessions:
            raise SyncError("Invalid or expired session ID")
        
        session = self.active_sessions[session_id]
        
        if time.time() - session.last_activity > self.session_timeout:
            del self.active_sessions[session_id]
            raise SyncError("Sync session has expired")
        
        return {
            "session_id": session.session_id,
            "client_id": session.client_id,
            "started_at": session.started_at,
            "last_activity": session.last_activity,
            "completed_tables": list(session.completed_tables),
            "in_progress": session.in_progress,
            "completed": session.completed,
        }

    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sync sessions."""
        now = time.time()
        expired_sessions = [
            session_id for session_id, session in self.active_sessions.items()
            if now - session.last_activity > self.session_timeout
        ]
        
        for session_id in expired_sessions:
            del self.active_sessions[session_id]
        
        return len(expired_sessions)

    def get_resume_token(self, session_id: str) -> Dict[str, Any]:
        """Get a resume token for a sync session."""
        if session_id not in self.active_sessions:
            raise SyncError("Invalid or expired session ID")
        
        session = self.active_sessions[session_id]
        
        if time.time() - session.last_activity > self.session_timeout:
            del self.active_sessions[session_id]
            raise SyncError("Sync session has expired")
        
        return session.get_resume_info()


class SyncClientSession:
    """Client-side implementation of a synchronization session."""

    def __init__(
        self,
        client_id: str,
        server_connection: "ServerConnection",
        local_db: MobileDBEngine,
    ):
        """Initialize a client-side sync session."""
        self.client_id = client_id
        self.server = server_connection
        self.local_db = local_db
        self.session_id: Optional[str] = None
        self.started_at: Optional[float] = None
        self.in_progress = False
        self.resume_token: Optional[str] = None

    async def start_sync(self) -> Dict[str, Any]:
        """Start a synchronization session with the server."""
        if self.in_progress:
            raise SyncError("Sync already in progress")
        
        try:
            response = await self.server.start_sync(self.client_id, self.resume_token)
            self.session_id = response["session_id"]
            self.started_at = response["started_at"]
            self.in_progress = True
            return response
        except Exception as e:
            raise NetworkError(f"Failed to start sync: {str(e)}")

    async def sync_table(self, table_name: str) -> Dict[str, Any]:
        """Synchronize a specific table with the server."""
        if not self.in_progress or not self.session_id:
            raise SyncError("No active sync session")
        
        # First, push local changes to the server
        push_results = await self._push_local_changes(table_name)
        
        # Then, pull remote changes from the server
        pull_results = await self._pull_remote_changes(table_name)
        
        return {
            "table_name": table_name,
            "pushed_changes": push_results["applied_count"],
            "pulled_changes": pull_results["applied_count"],
            "conflicts": push_results["conflicts"] + pull_results["conflicts"],
            "complete": True,
        }

    async def _push_local_changes(self, table_name: str) -> Dict[str, Any]:
        """Push local changes to the server."""
        if not self.in_progress or not self.session_id:
            raise SyncError("No active sync session")
        
        # Get last sync timestamp for this table
        last_sync = self.local_db.get_client_sync_state(self.client_id, table_name) or 0.0
        
        # Get local changes since last sync
        changes = self.local_db.get_changes_since(table_name, last_sync)
        
        if not changes:
            return {"applied_count": 0, "conflicts": []}
        
        # Prepare batch of changes
        batch = SyncBatch(
            table_name=table_name,
            records=changes,
            is_last_batch=True,
        )
        
        # Send changes to server
        try:
            result = await self.server.apply_batch(self.session_id, batch.to_dict())
            return result
        except Exception as e:
            raise NetworkError(f"Failed to push changes: {str(e)}")

    async def _pull_remote_changes(self, table_name: str) -> Dict[str, Any]:
        """Pull remote changes from the server."""
        if not self.in_progress or not self.session_id:
            raise SyncError("No active sync session")
        
        total_applied = 0
        all_conflicts = []
        
        try:
            # Keep pulling batches until no more changes
            while True:
                batch_dict = await self.server.get_next_batch(self.session_id, table_name)
                if not batch_dict:
                    break
                
                batch = SyncBatch.from_dict(batch_dict)
                
                # Apply the batch locally
                conflicts = []
                applied_count = 0
                
                # Process each record in the batch
                for pk, record in batch.records:
                    try:
                        table = self.local_db.get_table(table_name)
                        try:
                            existing = table.get_with_metadata(pk)
                            
                            # Local version exists, check for conflicts
                            if existing.version > record.version and existing.updated_at > record.updated_at:
                                # Local version is newer, potential conflict
                                conflicts.append({
                                    "pk": pk,
                                    "client_version": existing.version,
                                    "server_version": record.version,
                                    "client_updated_at": existing.updated_at,
                                    "server_updated_at": record.updated_at,
                                })
                                continue
                            
                            # Update the existing record
                            table.update(pk, record.data, "server")
                            applied_count += 1
                        
                        except RecordNotFoundError:
                            # Record doesn't exist locally, insert it
                            table.insert(record.data, "server")
                            applied_count += 1
                    
                    except Exception as e:
                        conflicts.append({
                            "pk": pk,
                            "error": str(e),
                        })
                
                total_applied += applied_count
                all_conflicts.extend(conflicts)
                
                # If this was the last batch, update sync state
                if batch.is_last_batch:
                    self.local_db.update_client_sync_state(self.client_id, table_name, time.time())
                    break
        
        except Exception as e:
            raise NetworkError(f"Failed to pull changes: {str(e)}")
        
        return {
            "applied_count": total_applied,
            "conflicts": all_conflicts,
        }

    async def complete_sync(self) -> Dict[str, Any]:
        """Complete the synchronization session."""
        if not self.in_progress or not self.session_id:
            raise SyncError("No active sync session")
        
        try:
            result = await self.server.complete_sync(self.session_id)
            self.in_progress = False
            self.session_id = None
            self.resume_token = None
            return result
        except Exception as e:
            # If we can't complete the sync normally, get a resume token
            try:
                resume_info = await self.server.get_resume_token(self.session_id)
                self.resume_token = resume_info["session_id"]
            except Exception:
                pass
            
            self.in_progress = False
            self.session_id = None
            raise NetworkError(f"Failed to complete sync: {str(e)}")

    async def sync_all_tables(self) -> Dict[str, Any]:
        """Synchronize all tables with the server."""
        if not self.in_progress:
            await self.start_sync()
        
        results = {}
        tables = self.local_db.tables.keys()
        
        for table_name in tables:
            try:
                result = await self.sync_table(table_name)
                results[table_name] = result
            except Exception as e:
                results[table_name] = {"error": str(e)}
        
        try:
            completion = await self.complete_sync()
            results["sync_summary"] = completion
        except Exception as e:
            results["sync_summary"] = {"error": str(e)}
        
        return results


class ServerConnection:
    """Handles communication with the sync server."""

    def __init__(self, server_url: str, timeout: int = 30):
        """Initialize server connection."""
        self.server_url = server_url
        self.timeout = timeout

    async def start_sync(self, client_id: str, resume_token: Optional[str] = None) -> Dict[str, Any]:
        """Start a sync session with the server."""
        # Note: In a real implementation, this would make an HTTP request
        # This is a placeholder that would be replaced with actual HTTP communication
        raise NotImplementedError("ServerConnection is an abstract class")

    async def get_next_batch(self, session_id: str, table_name: str) -> Optional[Dict[str, Any]]:
        """Get the next batch of changes from the server."""
        raise NotImplementedError("ServerConnection is an abstract class")

    async def apply_batch(self, session_id: str, batch: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a batch of changes to the server."""
        raise NotImplementedError("ServerConnection is an abstract class")

    async def complete_sync(self, session_id: str) -> Dict[str, Any]:
        """Complete a sync session with the server."""
        raise NotImplementedError("ServerConnection is an abstract class")

    async def get_resume_token(self, session_id: str) -> Dict[str, Any]:
        """Get a resume token for a sync session."""
        raise NotImplementedError("ServerConnection is an abstract class")