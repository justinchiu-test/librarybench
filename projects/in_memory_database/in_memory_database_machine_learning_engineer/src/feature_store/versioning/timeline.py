"""
Timeline for managing feature version history with temporal tracking.
"""

import time
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union, cast

import numpy as np
from pydantic import BaseModel, Field

from feature_store.vectors.base import VectorBase


class VersionType(Enum):
    """Types of version identifiers."""
    
    TIMESTAMP = "timestamp"  # Unix timestamp
    TAG = "tag"              # Named tag (e.g., "v1", "production")


class VersionInfo(BaseModel):
    """Information about a specific version of a feature."""
    
    version_id: str = Field(..., description="Version identifier (timestamp or tag)")
    version_type: VersionType = Field(..., description="Type of version identifier")
    timestamp: float = Field(..., description="Unix timestamp when this version was created")
    vector: VectorBase = Field(..., description="Feature vector for this version")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        """Pydantic configuration."""
        
        arbitrary_types_allowed = True


class Timeline(BaseModel):
    """
    Timeline for managing feature version history with temporal tracking.
    
    This class tracks the history of feature values over time, allowing retrieval
    of specific versions by timestamp or tag.
    """

    # Map of version_id to VersionInfo for tracking all versions
    versions: Dict[str, VersionInfo] = Field(default_factory=dict)
    
    # List of version IDs sorted by timestamp (for efficient range queries)
    _sorted_versions: List[str] = Field(default_factory=list)
    
    # Map of tag name to version_id for quick tag lookups
    _tag_index: Dict[str, str] = Field(default_factory=dict)
    
    class Config:
        """Pydantic configuration."""
        
        arbitrary_types_allowed = True
    
    def add_version(
        self, 
        vector: VectorBase, 
        timestamp: Optional[float] = None,
        tag: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """Add a new version to the timeline.
        
        Args:
            vector: Feature vector for this version
            timestamp: Unix timestamp for this version (default: current time)
            tag: Optional tag for this version
            metadata: Optional metadata for this version
            
        Returns:
            Version ID (timestamp or tag)
            
        Raises:
            ValueError: If tag already exists
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Create version ID (either tag or timestamp)
        if tag is not None:
            if tag in self._tag_index:
                raise ValueError(f"Tag already exists: {tag}")
            version_id = tag
            version_type = VersionType.TAG
        else:
            version_id = str(timestamp)
            version_type = VersionType.TIMESTAMP
        
        # Create version info
        version_info = VersionInfo(
            version_id=version_id,
            version_type=version_type,
            timestamp=timestamp,
            vector=vector,
            metadata=metadata or {}
        )
        
        # Add to versions map
        self.versions[version_id] = version_info
        
        # Update sorted list of versions
        self._update_sorted_versions(timestamp, version_id)
        
        # Update tag index if this is a tagged version
        if tag is not None:
            self._tag_index[tag] = version_id
        
        return version_id
    
    def _update_sorted_versions(self, timestamp: float, version_id: str) -> None:
        """Update the sorted list of versions with a new version.
        
        Args:
            timestamp: Timestamp for the new version
            version_id: Version ID for the new version
        """
        # Find the position to insert (binary search)
        pos = 0
        while pos < len(self._sorted_versions):
            other_id = self._sorted_versions[pos]
            other_info = self.versions[other_id]
            if timestamp < other_info.timestamp:
                break
            pos += 1
        
        # Insert at the correct position
        self._sorted_versions.insert(pos, version_id)
    
    def get_version(self, version_id: str) -> Optional[VersionInfo]:
        """Get a specific version by ID.
        
        Args:
            version_id: Version ID (timestamp or tag)
            
        Returns:
            VersionInfo if found, None otherwise
        """
        # Direct lookup
        if version_id in self.versions:
            return self.versions[version_id]
        
        # Check tag index
        if version_id in self._tag_index:
            return self.versions[self._tag_index[version_id]]
        
        return None
    
    def get_version_at_time(self, timestamp: float) -> Optional[VersionInfo]:
        """Get the version that was active at a specific timestamp.
        
        Finds the latest version created before or at the given timestamp.
        
        Args:
            timestamp: Unix timestamp to query
            
        Returns:
            VersionInfo for the active version, or None if no version exists
        """
        if not self._sorted_versions:
            return None
        
        # Binary search for the last version at or before the timestamp
        left, right = 0, len(self._sorted_versions) - 1
        result_idx = -1
        
        while left <= right:
            mid = (left + right) // 2
            mid_id = self._sorted_versions[mid]
            mid_info = self.versions[mid_id]
            
            if mid_info.timestamp <= timestamp:
                result_idx = mid
                left = mid + 1
            else:
                right = mid - 1
        
        if result_idx == -1:
            return None
        
        return self.versions[self._sorted_versions[result_idx]]
    
    def get_latest_version(self) -> Optional[VersionInfo]:
        """Get the latest version.
        
        Returns:
            VersionInfo for the latest version, or None if no versions exist
        """
        if not self._sorted_versions:
            return None
        
        return self.versions[self._sorted_versions[-1]]
    
    def get_versions_in_range(
        self, 
        start_time: float, 
        end_time: float
    ) -> List[VersionInfo]:
        """Get all versions within a time range.
        
        Args:
            start_time: Start of time range (inclusive)
            end_time: End of time range (inclusive)
            
        Returns:
            List of VersionInfo objects within the range, ordered by timestamp
        """
        result = []
        
        for version_id in self._sorted_versions:
            version_info = self.versions[version_id]
            if start_time <= version_info.timestamp <= end_time:
                result.append(version_info)
        
        return result
    
    def get_version_by_tag(self, tag: str) -> Optional[VersionInfo]:
        """Get a version by tag.
        
        Args:
            tag: Tag to look up
            
        Returns:
            VersionInfo if found, None otherwise
        """
        if tag not in self._tag_index:
            return None
        
        return self.versions[self._tag_index[tag]]
    
    def get_all_tags(self) -> Dict[str, float]:
        """Get all available tags with their timestamps.
        
        Returns:
            Dictionary mapping tag names to timestamps
        """
        return {
            tag: self.versions[version_id].timestamp
            for tag, version_id in self._tag_index.items()
        }
    
    def add_tag(self, version_id: str, tag: str) -> bool:
        """Add a tag to an existing version.
        
        Args:
            version_id: Version ID to tag
            tag: Tag to add
            
        Returns:
            True if successful, False if version not found
            
        Raises:
            ValueError: If tag already exists
        """
        if tag in self._tag_index:
            raise ValueError(f"Tag already exists: {tag}")
        
        if version_id not in self.versions:
            return False
        
        self._tag_index[tag] = version_id
        return True
    
    def remove_tag(self, tag: str) -> bool:
        """Remove a tag.
        
        Args:
            tag: Tag to remove
            
        Returns:
            True if successful, False if tag not found
        """
        if tag not in self._tag_index:
            return False
        
        del self._tag_index[tag]
        return True
    
    def num_versions(self) -> int:
        """Get the number of versions.
        
        Returns:
            Number of versions
        """
        return len(self.versions)
    
    def __len__(self) -> int:
        """Get the number of versions.
        
        Returns:
            Number of versions
        """
        return len(self.versions)
    
    def __contains__(self, version_id: str) -> bool:
        """Check if a version ID exists.
        
        Args:
            version_id: Version ID to check
            
        Returns:
            True if the version exists, False otherwise
        """
        return version_id in self.versions or version_id in self._tag_index