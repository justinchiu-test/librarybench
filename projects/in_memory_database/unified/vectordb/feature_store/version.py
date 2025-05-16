"""
Version management for feature values.

This module provides mechanisms for tracking feature versions
and maintaining history to ensure reproducibility of model predictions.
"""

import time
import uuid
from typing import Dict, Any, List, Optional, Set, Tuple, Union, TypeVar, Generic
from datetime import datetime
import copy

from common.core.versioning import Version as CommonVersion, ChangeTracker, ChangeType
from common.core.base import BaseRecord
from common.core.serialization import Serializable

T = TypeVar('T')

class Version:
    """
    Represents a specific version of a feature value.
    
    This class encapsulates a feature value with its version metadata,
    including timestamp, version number, and creation information.
    
    It adapts the common library's Version class for ML feature store use.
    """
    
    def __init__(
        self,
        value: Any,
        version_id: Optional[str] = None,
        timestamp: Optional[float] = None,
        created_by: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a version.
        
        Args:
            value: The feature value
            version_id: Optional unique identifier for this version
            timestamp: Optional creation timestamp (defaults to current time)
            created_by: Optional identifier of the creator
            description: Optional description of this version
            metadata: Optional additional metadata
        """
        self.value = value
        self._created_by = created_by
        self._description = description
        self._metadata = metadata or {}
            
        # Create common version
        cv_metadata = {}
        if created_by:
            cv_metadata['created_by'] = created_by
        if description:
            cv_metadata['description'] = description
        if metadata:
            cv_metadata.update(metadata)
            
        self._common_version = CommonVersion(
            version_id=version_id,
            timestamp=timestamp,
            metadata=cv_metadata
        )
        
    @property
    def version_id(self) -> str:
        """Get the version ID."""
        return self._common_version.version_id
    
    @property
    def timestamp(self) -> float:
        """Get the version timestamp."""
        return self._common_version.timestamp
    
    @property
    def created_by(self) -> Optional[str]:
        """Get the creator identifier."""
        return self._created_by
    
    @property
    def description(self) -> Optional[str]:
        """Get the version description."""
        return self._description
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Get the version metadata."""
        return self._metadata
        
    @property
    def created_at(self) -> datetime:
        """Get the creation time as a datetime object."""
        # Use UTC timestamp to avoid timezone issues
        return datetime.utcfromtimestamp(self.timestamp).replace(microsecond=0)
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert this version to a dictionary.
        
        Returns:
            Dictionary representation of this version
        """
        result = {
            "version_id": self.version_id,
            "value": self.value,
            "timestamp": self.timestamp,
            "created_by": self.created_by,
            "description": self.description,
            "metadata": self.metadata
        }
        
        return result
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Version':
        """
        Create a Version from a dictionary.
        
        Args:
            data: Dictionary containing version data
            
        Returns:
            A new Version instance
        """
        return cls(
            value=data["value"],
            version_id=data["version_id"],
            timestamp=data["timestamp"],
            created_by=data.get("created_by"),
            description=data.get("description"),
            metadata=data.get("metadata", {})
        )
    
    def to_common_version(self) -> CommonVersion:
        """
        Get the underlying common Version object.
        
        Returns:
            The common library Version object
        """
        return self._common_version
    
    @classmethod
    def from_common_version(cls, common_version: CommonVersion, value: Any) -> 'Version':
        """
        Create a Version from a common Version object.
        
        Args:
            common_version: Common library Version object
            value: The feature value
            
        Returns:
            A new Version instance
        """
        metadata = copy.deepcopy(common_version.metadata)
        created_by = metadata.pop('created_by', None)
        description = metadata.pop('description', None)
        
        return cls(
            value=value,
            version_id=common_version.version_id,
            timestamp=common_version.timestamp,
            created_by=created_by,
            description=description,
            metadata=metadata
        )
        
    def __eq__(self, other: object) -> bool:
        """Check if two versions are equal."""
        if not isinstance(other, Version):
            return False
        return self.version_id == other.version_id
        
    def __lt__(self, other: 'Version') -> bool:
        """Compare versions by timestamp."""
        return self.timestamp < other.timestamp
        
    def __repr__(self) -> str:
        """String representation of this version."""
        date_str = self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        return f"Version(id={self.version_id}, timestamp={date_str})"


class VersionManager:
    """
    Manages versioned feature values.
    
    This class tracks the history of values for features, allowing
    retrieval of specific versions and maintaining a complete history.
    It adapts the common library's ChangeTracker for feature value versioning.
    """
    
    def __init__(self, max_versions_per_feature: Optional[int] = None):
        """
        Initialize a version manager.
        
        Args:
            max_versions_per_feature: Optional maximum number of versions to retain per feature
        """
        # Map of entity_id -> feature_name -> list of versions (most recent first)
        self._versions: Dict[str, Dict[str, List[Version]]] = {}
        
        # Map of entity_id -> feature_name -> current version_id
        self._current_versions: Dict[str, Dict[str, str]] = {}
        
        # Optional limit on the number of versions to retain
        self._max_versions = max_versions_per_feature
        
        # Underlying change tracker from common library
        self._change_tracker = ChangeTracker()
        
    def add_version(
        self,
        entity_id: str,
        feature_name: str,
        value: Any,
        version_id: Optional[str] = None,
        timestamp: Optional[float] = None,
        created_by: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Version:
        """
        Add a new version of a feature.
        
        Args:
            entity_id: ID of the entity this feature belongs to
            feature_name: Name of the feature
            value: Value of the feature
            version_id: Optional unique identifier for this version
            timestamp: Optional creation timestamp
            created_by: Optional identifier of the creator
            description: Optional description of this version
            metadata: Optional additional metadata
            
        Returns:
            The created Version object
        """
        # Create new version
        version = Version(
            value=value,
            version_id=version_id,
            timestamp=timestamp,
            created_by=created_by,
            description=description,
            metadata=metadata
        )
        
        # Initialize maps if needed
        if entity_id not in self._versions:
            self._versions[entity_id] = {}
            self._current_versions[entity_id] = {}
            
        if feature_name not in self._versions[entity_id]:
            self._versions[entity_id][feature_name] = []
            # This is a new feature, record a CREATE change
            feature_record_id = f"{entity_id}:{feature_name}"
            # Create a mock record for the change tracker
            feature_record = type('FeatureRecord', (BaseRecord, Serializable), {
                'id': feature_record_id,
                'to_dict': lambda self: {'id': self.id, 'value': value, 'entity_id': entity_id, 'feature_name': feature_name}
            })()
            # Record the create operation in the change tracker
            self._change_tracker.record_create(feature_record)
        else:
            # This is an update to an existing feature, record an UPDATE change
            feature_record_id = f"{entity_id}:{feature_name}"
            old_value = self._versions[entity_id][feature_name][0].value if self._versions[entity_id][feature_name] else None
            
            # Create mock records for the change tracker
            old_feature_record = type('FeatureRecord', (BaseRecord, Serializable), {
                'id': feature_record_id,
                'to_dict': lambda self: {'id': self.id, 'value': old_value, 'entity_id': entity_id, 'feature_name': feature_name}
            })()
            
            new_feature_record = type('FeatureRecord', (BaseRecord, Serializable), {
                'id': feature_record_id,
                'to_dict': lambda self: {'id': self.id, 'value': value, 'entity_id': entity_id, 'feature_name': feature_name}
            })()
            
            # Record the update operation in the change tracker
            self._change_tracker.record_update(old_feature_record, new_feature_record)
        
        # Add to version history (most recent first)
        self._versions[entity_id][feature_name].insert(0, version)
        
        # Update current version
        self._current_versions[entity_id][feature_name] = version.version_id
        
        # Enforce version limit if applicable
        if self._max_versions is not None and len(self._versions[entity_id][feature_name]) > self._max_versions:
            self._versions[entity_id][feature_name] = self._versions[entity_id][feature_name][:self._max_versions]
        
        return version
    
    def get_version(
        self,
        entity_id: str,
        feature_name: str,
        version_id: Optional[str] = None,
        version_number: Optional[int] = None,
        timestamp: Optional[float] = None
    ) -> Optional[Version]:
        """
        Get a specific version of a feature.
        
        Args:
            entity_id: ID of the entity
            feature_name: Name of the feature
            version_id: Optional specific version ID to retrieve
            version_number: Optional version number (0 is most recent, 1 is previous, etc.)
            timestamp: Optional timestamp to get the version at a specific time
            
        Returns:
            The Version object if found, None otherwise
            
        Note:
            If multiple identifiers are provided, version_id takes precedence,
            followed by version_number, then timestamp.
        """
        if entity_id not in self._versions or feature_name not in self._versions[entity_id]:
            return None
        
        versions = self._versions[entity_id][feature_name]
        
        # Case 1: Find by version ID
        if version_id is not None:
            for version in versions:
                if version.version_id == version_id:
                    return version
            return None
        
        # Case 2: Find by version number
        if version_number is not None:
            if 0 <= version_number < len(versions):
                return versions[version_number]
            return None
        
        # Case 3: Find by timestamp (closest version at or before the timestamp)
        if timestamp is not None:
            # Sort by timestamp if needed
            sorted_versions = sorted(versions, key=lambda v: v.timestamp, reverse=True)
            for version in sorted_versions:
                if version.timestamp <= timestamp:
                    return version
            return None
        
        # Default: get the most recent version
        return versions[0] if versions else None
    
    def get_value(
        self,
        entity_id: str,
        feature_name: str,
        version_id: Optional[str] = None,
        version_number: Optional[int] = None,
        timestamp: Optional[float] = None,
        default: Any = None
    ) -> Any:
        """
        Get the value of a specific feature version.
        
        Args:
            entity_id: ID of the entity
            feature_name: Name of the feature
            version_id: Optional specific version ID to retrieve
            version_number: Optional version number (0 is most recent, 1 is previous, etc.)
            timestamp: Optional timestamp to get the value at a specific time
            default: Value to return if the version is not found
            
        Returns:
            The feature value if found, default otherwise
        """
        version = self.get_version(
            entity_id=entity_id,
            feature_name=feature_name,
            version_id=version_id,
            version_number=version_number,
            timestamp=timestamp
        )
        
        return version.value if version is not None else default
    
    def get_current(
        self,
        entity_id: str,
        feature_name: str,
        default: Any = None
    ) -> Any:
        """
        Get the current value of a feature.
        
        Args:
            entity_id: ID of the entity
            feature_name: Name of the feature
            default: Value to return if the feature is not found
            
        Returns:
            The current feature value if found, default otherwise
        """
        return self.get_value(entity_id, feature_name, default=default)
    
    def get_history(
        self,
        entity_id: str,
        feature_name: str,
        limit: Optional[int] = None,
        since_timestamp: Optional[float] = None,
        until_timestamp: Optional[float] = None
    ) -> List[Version]:
        """
        Get the version history of a feature.
        
        Args:
            entity_id: ID of the entity
            feature_name: Name of the feature
            limit: Optional maximum number of versions to return
            since_timestamp: Optional filter for versions after this time
            until_timestamp: Optional filter for versions before this time
            
        Returns:
            List of Version objects, sorted by timestamp (most recent first)
        """
        if entity_id not in self._versions or feature_name not in self._versions[entity_id]:
            return []
        
        versions = self._versions[entity_id][feature_name]
        
        # Apply timestamp filters
        if since_timestamp is not None or until_timestamp is not None:
            filtered_versions = []
            for v in versions:
                if since_timestamp is not None and v.timestamp < since_timestamp:
                    continue
                if until_timestamp is not None and v.timestamp > until_timestamp:
                    continue
                filtered_versions.append(v)
            versions = filtered_versions
        
        # Apply limit
        if limit is not None and limit > 0:
            versions = versions[:limit]
            
        return versions
    
    def get_versions_at(
        self,
        entity_id: str,
        feature_names: List[str],
        timestamp: float
    ) -> Dict[str, Version]:
        """
        Get versions of multiple features at a specific point in time.
        
        Args:
            entity_id: ID of the entity
            feature_names: List of feature names to retrieve
            timestamp: The point in time to retrieve versions for
            
        Returns:
            Dictionary of feature_name -> Version objects
        """
        result = {}
        for feature_name in feature_names:
            version = self.get_version(entity_id, feature_name, timestamp=timestamp)
            if version is not None:
                result[feature_name] = version
                
        return result
    
    def delete_history(
        self,
        entity_id: str,
        feature_name: Optional[str] = None
    ) -> int:
        """
        Delete version history for an entity or feature.
        
        Args:
            entity_id: ID of the entity
            feature_name: Optional feature name (if None, all features for the entity are deleted)
            
        Returns:
            Number of versions deleted
        """
        if entity_id not in self._versions:
            return 0
            
        deleted_count = 0
        
        if feature_name is not None:
            # Delete a specific feature
            if feature_name in self._versions[entity_id]:
                # Record deletion in the change tracker
                feature_record_id = f"{entity_id}:{feature_name}"
                # Get the current value
                current_value = self._versions[entity_id][feature_name][0].value if self._versions[entity_id][feature_name] else None
                
                # Create a mock record for the change tracker
                feature_record = type('FeatureRecord', (BaseRecord, Serializable), {
                    'id': feature_record_id,
                    'to_dict': lambda self: {'id': self.id, 'value': current_value, 'entity_id': entity_id, 'feature_name': feature_name}
                })()
                
                # Record the delete operation in the change tracker
                self._change_tracker.record_delete(feature_record)
                
                deleted_count = len(self._versions[entity_id][feature_name])
                del self._versions[entity_id][feature_name]
                
                if feature_name in self._current_versions[entity_id]:
                    del self._current_versions[entity_id][feature_name]
                    
                # Clean up empty dictionaries
                if not self._versions[entity_id]:
                    del self._versions[entity_id]
                    del self._current_versions[entity_id]
        else:
            # Delete all features for the entity
            for feature_name, versions in self._versions[entity_id].items():
                # Record deletion in the change tracker for each feature
                feature_record_id = f"{entity_id}:{feature_name}"
                current_value = versions[0].value if versions else None
                
                # Create a mock record for the change tracker
                feature_record = type('FeatureRecord', (BaseRecord, Serializable), {
                    'id': feature_record_id,
                    'to_dict': lambda self: {'id': self.id, 'value': current_value, 'entity_id': entity_id, 'feature_name': feature_name}
                })()
                
                # Record the delete operation in the change tracker
                self._change_tracker.record_delete(feature_record)
                
                deleted_count += len(versions)
                
            del self._versions[entity_id]
            del self._current_versions[entity_id]
            
        return deleted_count
    
    def get_entities(self) -> List[str]:
        """
        Get all entity IDs in the version manager.
        
        Returns:
            List of entity IDs
        """
        return list(self._versions.keys())
    
    def get_features(self, entity_id: str) -> List[str]:
        """
        Get all feature names for an entity.
        
        Args:
            entity_id: ID of the entity
            
        Returns:
            List of feature names
        """
        if entity_id not in self._versions:
            return []
            
        return list(self._versions[entity_id].keys())
    
    def has_feature(self, entity_id: str, feature_name: str) -> bool:
        """
        Check if a feature exists for an entity.
        
        Args:
            entity_id: ID of the entity
            feature_name: Name of the feature
            
        Returns:
            True if the feature exists, False otherwise
        """
        return entity_id in self._versions and feature_name in self._versions[entity_id]
        
    def get_changes_since(self, since_timestamp: float) -> List[Dict[str, Any]]:
        """
        Get all feature changes since the specified timestamp.
        
        Args:
            since_timestamp: Timestamp to filter changes from
            
        Returns:
            List of change information dictionaries
        """
        # Use the common ChangeTracker to get changes
        common_changes = self._change_tracker.get_changes_since(since_timestamp)
        
        # Transform common changes to feature-specific format
        feature_changes = []
        for change in common_changes:
            # Parse entity_id and feature_name from record_id
            if change.record_id and ":" in change.record_id:
                entity_id, feature_name = change.record_id.split(":", 1)
                
                feature_change = {
                    "change_id": change.change_id,
                    "entity_id": entity_id,
                    "feature_name": feature_name,
                    "change_type": change.change_type.value if change.change_type else None,
                    "timestamp": change.timestamp
                }
                
                # Add value data if available
                if change.change_type == ChangeType.CREATE or change.change_type == ChangeType.UPDATE:
                    if change.after_data and "value" in change.after_data:
                        feature_change["value"] = change.after_data["value"]
                
                feature_changes.append(feature_change)
                
        return feature_changes