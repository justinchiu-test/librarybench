"""
Version store for maintaining feature history with efficient retrieval.
"""

import time
from typing import Dict, List, Optional, Set, Tuple, Union, cast

from pydantic import BaseModel, Field, validator

from feature_store.vectors.base import VectorBase
from feature_store.versioning.lineage import LineageTracker
from feature_store.versioning.timeline import Timeline


class FeatureGroup(BaseModel):
    """A group of related features."""
    
    name: str = Field(..., description="Group name")
    description: str = Field("", description="Group description")
    features: Set[str] = Field(default_factory=set, description="Feature keys in this group")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Additional metadata")


class VersionStore(BaseModel):
    """
    Store for maintaining feature history with efficient retrieval.
    
    This class manages the versions of all features, providing efficient access
    to historical values and metadata.
    """

    # Map of feature key to timeline
    timelines: Dict[str, Timeline] = Field(default_factory=dict)
    
    # Lineage tracker for dependencies
    lineage: LineageTracker = Field(default_factory=LineageTracker)
    
    # Feature groups
    groups: Dict[str, FeatureGroup] = Field(default_factory=dict)
    
    # Map of feature key to group name
    _feature_to_group: Dict[str, str] = Field(default_factory=dict)
    
    def add_feature(
        self, 
        feature_key: str, 
        vector: VectorBase,
        group: Optional[str] = None,
        tag: Optional[str] = None,
        timestamp: Optional[float] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """Add a new feature or a new version of an existing feature.
        
        Args:
            feature_key: Unique identifier for the feature
            vector: Feature vector
            group: Optional group to add the feature to
            tag: Optional tag for this version
            timestamp: Unix timestamp for this version (default: current time)
            metadata: Optional metadata for this version
            
        Returns:
            Version ID
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Check if feature exists
        if feature_key not in self.timelines:
            # Create new timeline
            self.timelines[feature_key] = Timeline()
            
            # Register with lineage tracker
            self.lineage.register_feature(feature_key, metadata, timestamp)
        
        # Add to feature group if specified
        if group is not None:
            self.add_feature_to_group(feature_key, group)
        
        # Add to timeline
        return self.timelines[feature_key].add_version(
            vector=vector,
            timestamp=timestamp,
            tag=tag,
            metadata=metadata
        )
    
    def get_feature(
        self, 
        feature_key: str, 
        version: Optional[Union[str, float]] = None
    ) -> Optional[VectorBase]:
        """Get a feature vector by key and version.
        
        Args:
            feature_key: Feature key
            version: Version to retrieve (tag, timestamp, or None for latest)
            
        Returns:
            Feature vector if found, None otherwise
        """
        if feature_key not in self.timelines:
            return None
        
        timeline = self.timelines[feature_key]
        
        if version is None:
            # Get latest version
            version_info = timeline.get_latest_version()
        elif isinstance(version, float):
            # Get version at timestamp
            version_info = timeline.get_version_at_time(version)
        else:
            # Get version by ID or tag
            version_info = timeline.get_version(version)
        
        if version_info is None:
            return None
        
        return version_info.vector
    
    def add_feature_to_group(self, feature_key: str, group_name: str) -> None:
        """Add a feature to a group.
        
        If the group doesn't exist, it will be created.
        
        Args:
            feature_key: Feature key
            group_name: Group name
            
        Raises:
            ValueError: If feature doesn't exist
        """
        if feature_key not in self.timelines:
            raise ValueError(f"Feature not found: {feature_key}")
        
        # Create group if it doesn't exist
        if group_name not in self.groups:
            self.groups[group_name] = FeatureGroup(name=group_name)
        
        # Remove from previous group if any
        if feature_key in self._feature_to_group:
            old_group = self._feature_to_group[feature_key]
            self.groups[old_group].features.remove(feature_key)
        
        # Add to new group
        self.groups[group_name].features.add(feature_key)
        self._feature_to_group[feature_key] = group_name
    
    def get_features_in_group(self, group_name: str) -> List[str]:
        """Get all features in a group.
        
        Args:
            group_name: Group name
            
        Returns:
            List of feature keys in the group
            
        Raises:
            ValueError: If group doesn't exist
        """
        if group_name not in self.groups:
            raise ValueError(f"Group not found: {group_name}")
        
        return list(self.groups[group_name].features)
    
    def get_feature_group(self, feature_key: str) -> Optional[FeatureGroup]:
        """Get the group for a feature.
        
        Args:
            feature_key: Feature key
            
        Returns:
            FeatureGroup if found, None otherwise
        """
        if feature_key not in self._feature_to_group:
            return None
        
        group_name = self._feature_to_group[feature_key]
        return self.groups[group_name]
    
    def create_group(
        self, 
        name: str, 
        description: str = "", 
        metadata: Optional[Dict[str, str]] = None
    ) -> FeatureGroup:
        """Create a new feature group.
        
        Args:
            name: Group name
            description: Group description
            metadata: Additional metadata
            
        Returns:
            The created FeatureGroup
            
        Raises:
            ValueError: If group already exists
        """
        if name in self.groups:
            raise ValueError(f"Group already exists: {name}")
        
        group = FeatureGroup(
            name=name,
            description=description,
            metadata=metadata or {}
        )
        self.groups[name] = group
        return group
    
    def add_tag(self, feature_key: str, version_id: str, tag: str) -> bool:
        """Add a tag to a feature version.
        
        Args:
            feature_key: Feature key
            version_id: Version ID to tag
            tag: Tag to add
            
        Returns:
            True if successful, False if feature or version not found
        """
        if feature_key not in self.timelines:
            return False
        
        return self.timelines[feature_key].add_tag(version_id, tag)
    
    def get_version_metadata(
        self, 
        feature_key: str, 
        version: Union[str, float]
    ) -> Optional[Dict[str, str]]:
        """Get metadata for a feature version.
        
        Args:
            feature_key: Feature key
            version: Version ID, tag, or timestamp
            
        Returns:
            Metadata dictionary if found, None otherwise
        """
        if feature_key not in self.timelines:
            return None
        
        timeline = self.timelines[feature_key]
        
        if isinstance(version, float):
            # Get version at timestamp
            version_info = timeline.get_version_at_time(version)
        else:
            # Get version by ID or tag
            version_info = timeline.get_version(version)
        
        if version_info is None:
            return None
        
        return version_info.metadata
    
    def get_version_history(
        self, 
        feature_key: str, 
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> List[Tuple[str, float]]:
        """Get version history for a feature.
        
        Args:
            feature_key: Feature key
            start_time: Start of time range (default: earliest version)
            end_time: End of time range (default: latest version)
            
        Returns:
            List of (version_id, timestamp) tuples, ordered by timestamp
        """
        if feature_key not in self.timelines:
            return []
        
        timeline = self.timelines[feature_key]
        
        # Get all versions in the timeline
        all_versions = sorted(
            [(v.version_id, v.timestamp) for v in timeline.versions.values()],
            key=lambda x: x[1]
        )
        
        if not all_versions:
            return []
        
        # Apply time range filter if specified
        if start_time is None:
            start_time = all_versions[0][1]
        if end_time is None:
            end_time = all_versions[-1][1]
        
        return [
            (vid, ts) for vid, ts in all_versions
            if start_time <= ts <= end_time
        ]
    
    def get_all_features(self) -> List[str]:
        """Get all feature keys.
        
        Returns:
            List of all feature keys
        """
        return list(self.timelines.keys())
    
    def get_all_groups(self) -> List[str]:
        """Get all group names.
        
        Returns:
            List of all group names
        """
        return list(self.groups.keys())
    
    def feature_exists(self, feature_key: str) -> bool:
        """Check if a feature exists.
        
        Args:
            feature_key: Feature key
            
        Returns:
            True if the feature exists, False otherwise
        """
        return feature_key in self.timelines
    
    def group_exists(self, group_name: str) -> bool:
        """Check if a group exists.
        
        Args:
            group_name: Group name
            
        Returns:
            True if the group exists, False otherwise
        """
        return group_name in self.groups
    
    def add_dependency(
        self, 
        source: str, 
        target: str, 
        dependency_type: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> None:
        """Add a dependency between features.
        
        This is a convenience method that delegates to the lineage tracker.
        
        Args:
            source: Source feature key (dependent)
            target: Target feature key (dependency)
            dependency_type: Type of dependency
            metadata: Additional metadata for the dependency
            
        Raises:
            ValueError: If either feature does not exist
        """
        from feature_store.versioning.lineage import DependencyType
        
        try:
            dep_type = DependencyType(dependency_type)
        except ValueError:
            raise ValueError(f"Invalid dependency type: {dependency_type}")
        
        self.lineage.add_dependency(source, target, dep_type, metadata)
    
    def get_feature_dependencies(self, feature_key: str) -> List[Dict[str, str]]:
        """Get all dependencies of a feature.
        
        Args:
            feature_key: Feature key
            
        Returns:
            List of dependency information dictionaries
            
        Raises:
            ValueError: If feature does not exist
        """
        deps = self.lineage.get_feature_dependencies(feature_key)
        return [
            {
                "source": dep.source,
                "target": dep.target,
                "type": dep.type.value,
                "timestamp": str(dep.timestamp),
                **dep.metadata
            }
            for dep in deps
        ]
    
    def get_feature_lineage(self, feature_key: str, max_depth: int = -1) -> Dict[str, List[str]]:
        """Get the lineage graph of a feature.
        
        Args:
            feature_key: Feature key
            max_depth: Maximum depth to traverse (-1 for unlimited)
            
        Returns:
            Dictionary mapping feature keys to lists of dependency feature keys
            
        Raises:
            ValueError: If feature does not exist
        """
        lineage = self.lineage.get_lineage(feature_key, max_depth)
        return {k: list(v) for k, v in lineage.items()}
    
    def clear(self) -> None:
        """Clear all version data."""
        self.timelines.clear()
        self.lineage.clear()
        self.groups.clear()
        self._feature_to_group.clear()