"""
Versioning utilities for the common library.

This module provides classes and functions for tracking changes and managing
versions of data, which is essential for both vectordb and syncdb implementations.
"""

from typing import Any, Dict, List, Optional, Set, TypeVar, Generic, Tuple
import time
import json
import uuid
import copy
from enum import Enum
from collections import defaultdict

from .base import BaseRecord
from .serialization import Serializable

T = TypeVar('T', bound=BaseRecord)

class ChangeType(Enum):
    """
    Enum representing types of changes that can be tracked.
    """
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class Version:
    """
    Represents a version of a record or collection.
    
    This class encapsulates version information, including a version number,
    timestamp, and optional metadata.
    """
    
    def __init__(
        self,
        version_id: Optional[str] = None,
        timestamp: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize a version.
        
        Args:
            version_id: Unique identifier for the version. If None, a new UUID will be generated.
            timestamp: Timestamp when the version was created. If None, current time is used.
            metadata: Optional metadata associated with the version.
        """
        self.version_id = version_id if version_id is not None else str(uuid.uuid4())
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the version to a dictionary representation.
        
        Returns:
            A dictionary containing the version's data.
        """
        return {
            'version_id': self.version_id,
            'timestamp': self.timestamp,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Version':
        """
        Create a version from a dictionary representation.
        
        Args:
            data: Dictionary containing version data.
        
        Returns:
            A new Version instance.
        """
        return cls(
            version_id=data.get('version_id'),
            timestamp=data.get('timestamp'),
            metadata=data.get('metadata')
        )
    
    def to_json(self) -> str:
        """
        Convert the version to a JSON string.
        
        Returns:
            JSON representation of the version.
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Version':
        """
        Create a version from a JSON string.
        
        Args:
            json_str: JSON string representing the version.
        
        Returns:
            A new Version instance.
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __eq__(self, other: object) -> bool:
        """
        Check if two versions are equal by comparing their version IDs.
        
        Args:
            other: The object to compare with.
            
        Returns:
            True if the versions have the same version ID, False otherwise.
        """
        if not isinstance(other, Version):
            return False
        return self.version_id == other.version_id
    
    def __lt__(self, other: 'Version') -> bool:
        """
        Compare versions based on their timestamps.
        
        Args:
            other: The version to compare with.
            
        Returns:
            True if this version's timestamp is earlier than the other's.
        """
        return self.timestamp < other.timestamp


class Change(Serializable):
    """
    Represents a change to a record.
    
    This class encapsulates information about a change, including the type of change,
    the record ID, the version before and after the change, and optional metadata.
    """
    
    def __init__(
        self,
        change_id: Optional[str] = None,
        change_type: Optional[ChangeType] = None,
        record_id: Optional[str] = None,
        before_version: Optional[Version] = None,
        after_version: Optional[Version] = None,
        timestamp: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        before_data: Optional[Dict[str, Any]] = None,
        after_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize a change.
        
        Args:
            change_id: Unique identifier for the change. If None, a new UUID will be generated.
            change_type: Type of change (CREATE, UPDATE, DELETE).
            record_id: ID of the record that was changed.
            before_version: Version of the record before the change.
            after_version: Version of the record after the change.
            timestamp: Timestamp when the change occurred. If None, current time is used.
            metadata: Optional metadata associated with the change.
            before_data: Optional data representation of the record before the change.
            after_data: Optional data representation of the record after the change.
        """
        self.change_id = change_id if change_id is not None else str(uuid.uuid4())
        self.change_type = change_type
        self.record_id = record_id
        self.before_version = before_version
        self.after_version = after_version
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.metadata = metadata or {}
        self.before_data = before_data
        self.after_data = after_data
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the change to a dictionary representation.
        
        Returns:
            A dictionary containing the change's data.
        """
        result = {
            'change_id': self.change_id,
            'change_type': self.change_type.value if self.change_type else None,
            'record_id': self.record_id,
            'timestamp': self.timestamp,
            'metadata': self.metadata
        }
        
        if self.before_version:
            result['before_version'] = self.before_version.to_dict()
        
        if self.after_version:
            result['after_version'] = self.after_version.to_dict()
        
        if self.before_data:
            result['before_data'] = self.before_data
        
        if self.after_data:
            result['after_data'] = self.after_data
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Change':
        """
        Create a change from a dictionary representation.
        
        Args:
            data: Dictionary containing change data.
        
        Returns:
            A new Change instance.
        """
        change_type_str = data.get('change_type')
        change_type = ChangeType(change_type_str) if change_type_str else None
        
        before_version_data = data.get('before_version')
        before_version = Version.from_dict(before_version_data) if before_version_data else None
        
        after_version_data = data.get('after_version')
        after_version = Version.from_dict(after_version_data) if after_version_data else None
        
        return cls(
            change_id=data.get('change_id'),
            change_type=change_type,
            record_id=data.get('record_id'),
            before_version=before_version,
            after_version=after_version,
            timestamp=data.get('timestamp'),
            metadata=data.get('metadata'),
            before_data=data.get('before_data'),
            after_data=data.get('after_data')
        )


class VersionVector:
    """
    Implements a version vector for distributed version tracking.
    
    A version vector is a map from node IDs to counters, which can be used to
    establish a partial ordering of events in a distributed system.
    """
    
    def __init__(self, node_id: Optional[str] = None) -> None:
        """
        Initialize a version vector.
        
        Args:
            node_id: ID of the node that owns this vector. If None, a new UUID will be generated.
        """
        self.node_id = node_id if node_id is not None else str(uuid.uuid4())
        self.vector: Dict[str, int] = defaultdict(int)
        self.vector[self.node_id] = 0
    
    def increment(self) -> None:
        """
        Increment the counter for this node's ID.
        """
        self.vector[self.node_id] += 1
    
    def merge(self, other: 'VersionVector') -> None:
        """
        Merge another version vector into this one.
        
        The merge operation takes the maximum counter value for each node ID.
        
        Args:
            other: The version vector to merge with.
        """
        for node_id, counter in other.vector.items():
            self.vector[node_id] = max(self.vector[node_id], counter)
    
    def compare(self, other: 'VersionVector') -> int:
        """
        Compare this version vector with another.
        
        Returns:
            -1 if this vector is less than the other (happens-before)
            0 if the vectors are concurrent (neither happens-before)
            1 if this vector is greater than the other (happened-after)
        """
        less = False
        greater = False
        
        # Check all node IDs in both vectors
        all_node_ids = set(self.vector.keys()) | set(other.vector.keys())
        
        for node_id in all_node_ids:
            self_counter = self.vector.get(node_id, 0)
            other_counter = other.vector.get(node_id, 0)
            
            if self_counter < other_counter:
                less = True
            elif self_counter > other_counter:
                greater = True
        
        if less and not greater:
            return -1  # happens-before
        elif greater and not less:
            return 1   # happened-after
        else:
            return 0   # concurrent
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the version vector to a dictionary representation.
        
        Returns:
            A dictionary containing the version vector's data.
        """
        return {
            'node_id': self.node_id,
            'vector': dict(self.vector)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VersionVector':
        """
        Create a version vector from a dictionary representation.
        
        Args:
            data: Dictionary containing version vector data.
        
        Returns:
            A new VersionVector instance.
        """
        vector = cls(node_id=data.get('node_id'))
        vector.vector = defaultdict(int, data.get('vector', {}))
        return vector
    
    def to_json(self) -> str:
        """
        Convert the version vector to a JSON string.
        
        Returns:
            JSON representation of the version vector.
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'VersionVector':
        """
        Create a version vector from a JSON string.
        
        Args:
            json_str: JSON string representing the version vector.
        
        Returns:
            A new VersionVector instance.
        """
        data = json.loads(json_str)
        return cls.from_dict(data)


class ChangeTracker(Generic[T]):
    """
    Tracks changes to records over time.
    
    This class maintains a history of changes to records, allowing for
    versioning, conflict detection, and synchronization.
    """
    
    def __init__(self, node_id: Optional[str] = None) -> None:
        """
        Initialize a change tracker.
        
        Args:
            node_id: ID of the node that owns this tracker. If None, a new UUID will be generated.
        """
        self.node_id = node_id if node_id is not None else str(uuid.uuid4())
        self.version_vector = VersionVector(node_id=self.node_id)
        self.changes: List[Change] = []
        self.current_versions: Dict[str, Version] = {}
    
    def record_create(self, record: T) -> None:
        """
        Record a creation change.
        
        Args:
            record: The record that was created.
        """
        self.version_vector.increment()
        version = Version(metadata={'node_id': self.node_id})
        
        change = Change(
            change_type=ChangeType.CREATE,
            record_id=record.id,
            after_version=version,
            after_data=record.to_dict()
        )
        
        self.changes.append(change)
        self.current_versions[record.id] = version
    
    def record_update(self, before_record: T, after_record: T) -> None:
        """
        Record an update change.
        
        Args:
            before_record: The record before the update.
            after_record: The record after the update.
        """
        if before_record.id != after_record.id:
            raise ValueError("Record IDs must match for an update")
        
        self.version_vector.increment()
        before_version = self.current_versions.get(
            before_record.id, 
            Version(metadata={'node_id': self.node_id})
        )
        after_version = Version(metadata={'node_id': self.node_id})
        
        change = Change(
            change_type=ChangeType.UPDATE,
            record_id=after_record.id,
            before_version=before_version,
            after_version=after_version,
            before_data=before_record.to_dict(),
            after_data=after_record.to_dict()
        )
        
        self.changes.append(change)
        self.current_versions[after_record.id] = after_version
    
    def record_delete(self, record: T) -> None:
        """
        Record a deletion change.
        
        Args:
            record: The record that was deleted.
        """
        self.version_vector.increment()
        before_version = self.current_versions.get(
            record.id,
            Version(metadata={'node_id': self.node_id})
        )
        
        change = Change(
            change_type=ChangeType.DELETE,
            record_id=record.id,
            before_version=before_version,
            before_data=record.to_dict()
        )
        
        self.changes.append(change)
        
        # We keep the last version in current_versions to track the deletion
        self.current_versions[record.id] = Version(
            metadata={'node_id': self.node_id, 'deleted': True}
        )
    
    def get_changes_since(self, since_timestamp: float) -> List[Change]:
        """
        Get all changes since a specific timestamp.
        
        Args:
            since_timestamp: The timestamp to filter changes from.
        
        Returns:
            A list of changes that occurred after the specified timestamp.
        """
        return [
            change for change in self.changes 
            if change.timestamp > since_timestamp
        ]
    
    def get_changes_for_record(self, record_id: str) -> List[Change]:
        """
        Get all changes for a specific record.
        
        Args:
            record_id: The ID of the record to get changes for.
        
        Returns:
            A list of changes for the specified record.
        """
        return [
            change for change in self.changes 
            if change.record_id == record_id
        ]
    
    def detect_conflicts(self, other_changes: List[Change]) -> List[Tuple[Change, Change]]:
        """
        Detect conflicts between this tracker's changes and another set of changes.
        
        Conflicts occur when the same record has concurrent updates.
        
        Args:
            other_changes: List of changes to check against.
        
        Returns:
            A list of tuples containing conflicting changes.
        """
        conflicts = []
        
        # Group changes by record ID
        local_changes_by_record = defaultdict(list)
        for change in self.changes:
            local_changes_by_record[change.record_id].append(change)
        
        other_changes_by_record = defaultdict(list)
        for change in other_changes:
            other_changes_by_record[change.record_id].append(change)
        
        # Check for conflicts in records that have changes in both sets
        for record_id in set(local_changes_by_record.keys()) & set(other_changes_by_record.keys()):
            local_latest = max(local_changes_by_record[record_id], key=lambda c: c.timestamp)
            other_latest = max(other_changes_by_record[record_id], key=lambda c: c.timestamp)
            
            # If both changes have after versions, check if they're concurrent
            if (local_latest.after_version and other_latest.after_version and
                local_latest.after_version.timestamp != other_latest.after_version.timestamp):
                # Simple conflict detection based on timestamp
                # In a real system, we would use version vectors for more accurate detection
                conflicts.append((local_latest, other_latest))
        
        return conflicts
    
    def merge(self, other_tracker: 'ChangeTracker') -> List[Tuple[Change, Change]]:
        """
        Merge changes from another tracker into this one.
        
        Args:
            other_tracker: The tracker to merge changes from.
        
        Returns:
            A list of conflicting changes that require resolution.
        """
        # Detect conflicts first
        conflicts = self.detect_conflicts(other_tracker.changes)
        
        # Merge changes that don't conflict
        for change in other_tracker.changes:
            if not any(change in conflict for conflict in conflicts for conflict in conflict):
                if change not in self.changes:
                    self.changes.append(copy.deepcopy(change))
        
        # Merge version vectors
        self.version_vector.merge(other_tracker.version_vector)
        
        # Update current versions for non-conflicting records
        for record_id, version in other_tracker.current_versions.items():
            if record_id not in self.current_versions:
                self.current_versions[record_id] = copy.deepcopy(version)
            else:
                # If we have both versions, take the latest one
                if self.current_versions[record_id].timestamp < version.timestamp:
                    self.current_versions[record_id] = copy.deepcopy(version)
        
        return conflicts
    
    def clear_history_before(self, timestamp: float) -> None:
        """
        Clear change history before a specific timestamp.
        
        This can be used to prune old changes and save memory.
        
        Args:
            timestamp: The timestamp before which changes should be cleared.
        """
        self.changes = [
            change for change in self.changes 
            if change.timestamp >= timestamp
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the change tracker to a dictionary representation.
        
        Returns:
            A dictionary containing the change tracker's data.
        """
        return {
            'node_id': self.node_id,
            'version_vector': self.version_vector.to_dict(),
            'changes': [change.to_dict() for change in self.changes],
            'current_versions': {
                record_id: version.to_dict() 
                for record_id, version in self.current_versions.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChangeTracker':
        """
        Create a change tracker from a dictionary representation.
        
        Args:
            data: Dictionary containing change tracker data.
        
        Returns:
            A new ChangeTracker instance.
        """
        tracker = cls(node_id=data.get('node_id'))
        
        tracker.version_vector = VersionVector.from_dict(
            data.get('version_vector', {'node_id': tracker.node_id})
        )
        
        tracker.changes = [
            Change.from_dict(change_data) 
            for change_data in data.get('changes', [])
        ]
        
        tracker.current_versions = {
            record_id: Version.from_dict(version_data)
            for record_id, version_data in data.get('current_versions', {}).items()
        }
        
        return tracker
    
    def to_json(self) -> str:
        """
        Convert the change tracker to a JSON string.
        
        Returns:
            JSON representation of the change tracker.
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ChangeTracker':
        """
        Create a change tracker from a JSON string.
        
        Args:
            json_str: JSON string representing the change tracker.
        
        Returns:
            A new ChangeTracker instance.
        """
        data = json.loads(json_str)
        return cls.from_dict(data)