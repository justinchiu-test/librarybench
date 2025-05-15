"""
Change tracking system for efficient synchronization.
"""
from typing import Dict, List, Any, Optional, Set, Tuple
import time
import json
from dataclasses import dataclass
import copy

from common.core.versioning import ChangeTracker as CommonChangeTracker
from common.core.versioning import VersionVector as CommonVersionVector
from common.core.versioning import Change as CommonChange
from common.core.versioning import ChangeType, Version
from common.core.serialization import Serializable


@dataclass
class ChangeRecord(Serializable):
    """Represents a single change to a record."""
    id: int  # Sequential ID for ordering changes
    table_name: str
    primary_key: Tuple  # Primary key values as a tuple
    operation: str  # "insert", "update", or "delete"
    timestamp: float  # Unix timestamp
    client_id: str  # ID of the client that made the change
    old_data: Optional[Dict[str, Any]]  # Previous state (None for inserts)
    new_data: Optional[Dict[str, Any]]  # New state (None for deletes)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for serialization."""
        return {
            "id": self.id,
            "table_name": self.table_name,
            "primary_key": self.primary_key,
            "operation": self.operation,
            "timestamp": self.timestamp,
            "client_id": self.client_id,
            "old_data": self.old_data,
            "new_data": self.new_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChangeRecord':
        """Create a ChangeRecord from a dictionary."""
        return cls(
            id=data["id"],
            table_name=data["table_name"],
            primary_key=tuple(data["primary_key"]),
            operation=data["operation"],
            timestamp=data["timestamp"],
            client_id=data["client_id"],
            old_data=data["old_data"],
            new_data=data["new_data"]
        )
    
    def to_common_change(self) -> CommonChange:
        """Convert to a CommonChange object for the common library."""
        # Map operation to ChangeType
        change_type = None
        if self.operation == "insert":
            change_type = ChangeType.CREATE
        elif self.operation == "update":
            change_type = ChangeType.UPDATE
        elif self.operation == "delete":
            change_type = ChangeType.DELETE
            
        # Create versions as needed
        before_version = None
        if self.old_data:
            before_version = Version(metadata={'client_id': self.client_id})
            
        after_version = None
        if self.new_data:
            after_version = Version(metadata={'client_id': self.client_id})
            
        # Create a unique record_id combining table_name and primary_key
        record_id = f"{self.table_name}:{self.primary_key}"
        
        return CommonChange(
            change_id=str(self.id),
            change_type=change_type,
            record_id=record_id,
            before_version=before_version,
            after_version=after_version,
            timestamp=self.timestamp,
            metadata={'client_id': self.client_id, 'table_name': self.table_name},
            before_data=self.old_data,
            after_data=self.new_data
        )
    
    @classmethod
    def from_common_change(cls, change: CommonChange) -> 'ChangeRecord':
        """Create a ChangeRecord from a CommonChange object."""
        # Extract metadata
        metadata = change.metadata or {}
        client_id = metadata.get('client_id', 'unknown')
        table_name = metadata.get('table_name', 'unknown')
        
        # Extract primary key from record_id (format: "table_name:primary_key")
        record_id_parts = change.record_id.split(':', 1)
        primary_key_str = record_id_parts[1] if len(record_id_parts) > 1 else change.record_id
        
        # Convert primary key string back to tuple (this is approximate)
        try:
            # Try to evaluate as a tuple literal
            primary_key = eval(primary_key_str)
            if not isinstance(primary_key, tuple):
                primary_key = (primary_key_str,)
        except:
            primary_key = (primary_key_str,)
        
        # Map ChangeType to operation
        operation = "unknown"
        if change.change_type == ChangeType.CREATE:
            operation = "insert"
        elif change.change_type == ChangeType.UPDATE:
            operation = "update"
        elif change.change_type == ChangeType.DELETE:
            operation = "delete"
            
        return cls(
            id=int(change.change_id) if change.change_id.isdigit() else 0,
            table_name=table_name,
            primary_key=primary_key,
            operation=operation,
            timestamp=change.timestamp,
            client_id=client_id,
            old_data=change.before_data,
            new_data=change.after_data
        )


class ChangeTracker:
    """
    Tracks changes to database records for efficient synchronization.
    This class is a wrapper around the common library's ChangeTracker
    that maintains compatibility with the existing API.
    """
    def __init__(self, max_history_size: int = 10000):
        self.changes: Dict[str, List[ChangeRecord]] = {}  # Table name -> changes
        self.max_history_size = max_history_size
        self.counters: Dict[str, int] = {}  # Table name -> next change ID
        
        # Internal common library change tracker
        self._common_tracker = CommonChangeTracker()
    
    def record_change(self, 
                     table_name: str, 
                     primary_key: Tuple,
                     operation: str, 
                     old_data: Optional[Dict[str, Any]], 
                     new_data: Optional[Dict[str, Any]],
                     client_id: str) -> ChangeRecord:
        """
        Record a change to a database record.
        
        Args:
            table_name: Name of the table
            primary_key: Primary key values as a tuple
            operation: "insert", "update", or "delete"
            old_data: Previous state (None for inserts)
            new_data: New state (None for deletes)
            client_id: ID of the client that made the change
            
        Returns:
            The created ChangeRecord
        """
        # Initialize table changes if not already done
        if table_name not in self.changes:
            self.changes[table_name] = []
            self.counters[table_name] = 0
        
        # Get the next change ID for this table
        change_id = self.counters[table_name]
        self.counters[table_name] += 1
        
        # Create the change record
        change = ChangeRecord(
            id=change_id,
            table_name=table_name,
            primary_key=primary_key,
            operation=operation,
            timestamp=time.time(),
            client_id=client_id,
            old_data=copy.deepcopy(old_data) if old_data else None,
            new_data=copy.deepcopy(new_data) if new_data else None
        )
        
        # Add to the change log
        self.changes[table_name].append(change)
        
        # Also add to the common library's change tracker
        common_change = change.to_common_change()
        self._record_common_change(common_change)
        
        # Prune history if necessary
        self._prune_history(table_name)
        
        return change
    
    def _record_common_change(self, change: CommonChange) -> None:
        """
        Record a change in the common library's change tracker.
        This handles the appropriate method call based on the change type.
        """
        # The common library's ChangeTracker expects BaseRecord objects,
        # but we work with dictionaries. This is a simplified approach.
        
        # For now, we'll just append the change to the changes list
        # as the Common ChangeTracker's methods expect BaseRecord objects
        self._common_tracker.changes.append(change)
        
        # Update the version vector
        self._common_tracker.version_vector.increment()
        
        # Update current versions
        if change.change_type != ChangeType.DELETE and change.after_version:
            self._common_tracker.current_versions[change.record_id] = change.after_version
    
    def _prune_history(self, table_name: str) -> None:
        """
        Prune change history for a table if it exceeds max_history_size.
        """
        table_changes = self.changes.get(table_name, [])
        if len(table_changes) > self.max_history_size:
            # Keep only the most recent changes
            self.changes[table_name] = table_changes[-self.max_history_size:]
    
    def get_changes_since(self, 
                         table_name: str, 
                         since_id: int, 
                         exclude_client_id: Optional[str] = None) -> List[ChangeRecord]:
        """
        Get all changes to a table since a given change ID.
        
        Args:
            table_name: Name of the table
            since_id: Get changes with ID greater than this
            exclude_client_id: Optionally exclude changes made by this client
            
        Returns:
            List of changes since the given ID
        """
        table_changes = self.changes.get(table_name, [])
        
        # Filter changes by ID and optionally by client ID
        filtered_changes = [
            change for change in table_changes
            if change.id > since_id and (exclude_client_id is None or change.client_id != exclude_client_id)
        ]
        
        return filtered_changes
    
    def get_latest_change_id(self, table_name: str) -> int:
        """
        Get the ID of the latest change for a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Latest change ID, or -1 if no changes exist
        """
        if table_name not in self.changes or not self.changes[table_name]:
            return -1
        
        return self.changes[table_name][-1].id
    
    def serialize_changes(self, changes: List[ChangeRecord]) -> str:
        """
        Serialize changes to JSON.
        
        Args:
            changes: List of changes to serialize
            
        Returns:
            JSON string representation
        """
        change_dicts = [change.to_dict() for change in changes]
        return json.dumps(change_dicts)
    
    def deserialize_changes(self, json_str: str) -> List[ChangeRecord]:
        """
        Deserialize changes from JSON.
        
        Args:
            json_str: JSON string representation
            
        Returns:
            List of ChangeRecord objects
        """
        change_dicts = json.loads(json_str)
        return [ChangeRecord.from_dict(change_dict) for change_dict in change_dicts]
    
    def merge_changes(self, other_tracker: 'ChangeTracker') -> List[Tuple[ChangeRecord, ChangeRecord]]:
        """
        Merge changes from another change tracker and detect conflicts.
        
        Args:
            other_tracker: The change tracker to merge with
            
        Returns:
            List of conflicting changes
        """
        # Use the common library's merge functionality
        conflicts = self._common_tracker.merge(other_tracker._common_tracker)
        
        # Convert conflicts back to ChangeRecord format
        change_conflicts = []
        for local, other in conflicts:
            local_change = ChangeRecord.from_common_change(local)
            other_change = ChangeRecord.from_common_change(other)
            change_conflicts.append((local_change, other_change))
            
        # Now update our changes dictionary with the merged changes
        # This is a simplified approach that doesn't handle all edge cases
        for table_name, other_changes in other_tracker.changes.items():
            if table_name not in self.changes:
                self.changes[table_name] = []
                self.counters[table_name] = 0
                
            # Add any changes that are not already in our list
            for other_change in other_changes:
                if not any(c.id == other_change.id and c.client_id == other_change.client_id 
                           for c in self.changes[table_name]):
                    # Ensure correct ID sequencing
                    if self.counters[table_name] <= other_change.id:
                        self.counters[table_name] = other_change.id + 1
                    
                    self.changes[table_name].append(copy.deepcopy(other_change))
                    
            # Sort changes by ID to maintain ordering
            self.changes[table_name].sort(key=lambda c: c.id)
            
            # Prune if necessary
            self._prune_history(table_name)
            
        return change_conflicts
    
    def clear_history(self, table_name: Optional[str] = None) -> None:
        """
        Clear change history for a specific table or all tables.
        
        Args:
            table_name: Name of the table, or None to clear all tables
        """
        if table_name:
            if table_name in self.changes:
                self.changes[table_name] = []
        else:
            self.changes.clear()
            
        # Also clear the common tracker's history
        self._common_tracker.changes = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for serialization."""
        changes_dict = {}
        for table_name, changes in self.changes.items():
            changes_dict[table_name] = [change.to_dict() for change in changes]
            
        return {
            "changes": changes_dict,
            "counters": self.counters,
            "max_history_size": self.max_history_size,
            "common_tracker": self._common_tracker.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChangeTracker':
        """Create a ChangeTracker from a dictionary."""
        tracker = cls(max_history_size=data.get("max_history_size", 10000))
        
        # Restore changes
        changes_dict = data.get("changes", {})
        for table_name, change_dicts in changes_dict.items():
            tracker.changes[table_name] = [
                ChangeRecord.from_dict(change_dict) for change_dict in change_dicts
            ]
            
        # Restore counters
        tracker.counters = data.get("counters", {})
        
        # Restore common tracker if available
        common_tracker_dict = data.get("common_tracker")
        if common_tracker_dict:
            tracker._common_tracker = CommonChangeTracker.from_dict(common_tracker_dict)
            
        return tracker


class VersionVector(Serializable):
    """
    Tracks the version of data across multiple clients using a vector clock.
    Used for detecting conflicts during synchronization.
    
    This class is now a wrapper around the common library's VersionVector
    that maintains compatibility with the existing API.
    """
    def __init__(self, client_id: str, initial_value: int = 0):
        self.vector: Dict[str, int] = {client_id: initial_value}
        self.client_id = client_id
        
        # Internal common library version vector
        self._common_vector = CommonVersionVector(node_id=client_id)
        if initial_value > 0:
            # Set the initial value
            self._common_vector.vector[client_id] = initial_value
    
    def increment(self) -> None:
        """Increment the version for the current client."""
        self.vector[self.client_id] = self.vector.get(self.client_id, 0) + 1
        self._common_vector.increment()
    
    def update(self, other: 'VersionVector') -> None:
        """Merge with another version vector, taking the max value for each client."""
        for client_id, version in other.vector.items():
            self.vector[client_id] = max(self.vector.get(client_id, 0), version)
        
        # Update the common version vector
        self._common_vector.merge(other._common_vector)
    
    def dominates(self, other: 'VersionVector') -> bool:
        """
        Check if this version vector dominates another.
        
        Returns True if this vector is strictly greater than or equal to the other
        in all dimensions, and strictly greater in at least one dimension.
        """
        # Use the common library's compare method
        comparison = self._common_vector.compare(other._common_vector)
        return comparison > 0  # comparison == 1 means this vector happened-after
    
    def concurrent_with(self, other: 'VersionVector') -> bool:
        """
        Check if this version vector is concurrent with another.
        
        Returns True if neither vector dominates the other, indicating
        that they represent concurrent modifications.
        """
        # Use the common library's compare method
        comparison = self._common_vector.compare(other._common_vector)
        return comparison == 0  # comparison == 0 means vectors are concurrent
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for serialization."""
        return {
            "vector": dict(self.vector),
            "client_id": self.client_id,
            "common_vector": self._common_vector.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], client_id: str) -> 'VersionVector':
        """Create a VersionVector from a dictionary."""
        vector = cls(client_id, 0)
        vector.vector = dict(data.get("vector", {}))
        
        # Restore common vector if available
        common_vector_dict = data.get("common_vector")
        if common_vector_dict:
            vector._common_vector = CommonVersionVector.from_dict(common_vector_dict)
        else:
            # Create from scratch based on the vector
            vector._common_vector = CommonVersionVector(node_id=client_id)
            for c_id, val in vector.vector.items():
                vector._common_vector.vector[c_id] = val
                
        return vector