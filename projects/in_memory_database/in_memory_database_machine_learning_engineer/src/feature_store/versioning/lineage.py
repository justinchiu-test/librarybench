"""
Lineage tracking for feature derivation and dependencies.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Union, cast

from pydantic import BaseModel, Field


class DependencyType(Enum):
    """Types of dependencies between features."""
    
    DERIVED_FROM = "derived_from"       # Feature was derived from another feature
    COMPUTED_WITH = "computed_with"     # Feature was computed using another feature
    PART_OF = "part_of"                 # Feature is part of a larger feature group
    DEPENDENT_ON = "dependent_on"       # Generic dependency


class Dependency(BaseModel):
    """A dependency between features."""
    
    source: str = Field(..., description="Source feature key")
    target: str = Field(..., description="Target feature key")
    type: DependencyType = Field(..., description="Type of dependency")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Additional metadata")
    timestamp: float = Field(..., description="Unix timestamp when this dependency was created")
    transformation_id: Optional[str] = Field(None, description="ID of transformation if applicable")


class LineageNode(BaseModel):
    """Information about a feature and its dependencies."""
    
    feature_key: str = Field(..., description="Feature key")
    parents: Set[str] = Field(default_factory=set, description="Parent features (dependencies)")
    children: Set[str] = Field(default_factory=set, description="Child features (dependents)")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Additional metadata")
    created_at: float = Field(..., description="Unix timestamp when this feature was created")


class LineageTracker(BaseModel):
    """
    Tracker for feature derivation and dependencies.
    
    This class maintains a graph of feature dependencies, allowing analysis of
    feature lineage and impact of changes.
    """

    # Map of feature key to node data
    nodes: Dict[str, LineageNode] = Field(default_factory=dict)
    
    # Map of (source, target) to dependency data
    edges: Dict[Tuple[str, str], Dependency] = Field(default_factory=dict)
    
    def register_feature(
        self, 
        feature_key: str, 
        metadata: Optional[Dict[str, str]] = None,
        timestamp: Optional[float] = None
    ) -> None:
        """Register a new feature.
        
        Args:
            feature_key: Unique identifier for the feature
            metadata: Additional metadata for the feature
            timestamp: Unix timestamp when this feature was created (default: current time)
            
        Raises:
            ValueError: If feature already exists
        """
        if feature_key in self.nodes:
            raise ValueError(f"Feature already registered: {feature_key}")
        
        if timestamp is None:
            timestamp = datetime.now().timestamp()
        
        self.nodes[feature_key] = LineageNode(
            feature_key=feature_key,
            metadata=metadata or {},
            created_at=timestamp
        )
    
    def add_dependency(
        self,
        source: str,
        target: str,
        dependency_type: DependencyType,
        metadata: Optional[Dict[str, str]] = None,
        transformation_id: Optional[str] = None,
        timestamp: Optional[float] = None
    ) -> None:
        """Add a dependency between features.
        
        Args:
            source: Source feature key (dependent)
            target: Target feature key (dependency)
            dependency_type: Type of dependency
            metadata: Additional metadata for the dependency
            transformation_id: ID of transformation if applicable
            timestamp: Unix timestamp when this dependency was created (default: current time)
            
        Raises:
            ValueError: If either feature does not exist
            ValueError: If dependency already exists
        """
        if source not in self.nodes:
            raise ValueError(f"Source feature not registered: {source}")
        
        if target not in self.nodes:
            raise ValueError(f"Target feature not registered: {target}")
        
        edge_key = (source, target)
        if edge_key in self.edges:
            raise ValueError(f"Dependency already exists: {source} -> {target}")
        
        if timestamp is None:
            timestamp = datetime.now().timestamp()
        
        # Create dependency
        dependency = Dependency(
            source=source,
            target=target,
            type=dependency_type,
            metadata=metadata or {},
            timestamp=timestamp,
            transformation_id=transformation_id
        )
        
        # Update graph
        self.edges[edge_key] = dependency
        self.nodes[source].parents.add(target)
        self.nodes[target].children.add(source)
    
    def get_feature_dependencies(self, feature_key: str) -> List[Dependency]:
        """Get all dependencies of a feature.
        
        Args:
            feature_key: Feature key
            
        Returns:
            List of dependencies where this feature is the source
            
        Raises:
            ValueError: If feature does not exist
        """
        if feature_key not in self.nodes:
            raise ValueError(f"Feature not registered: {feature_key}")
        
        return [
            dep for (src, _), dep in self.edges.items()
            if src == feature_key
        ]
    
    def get_feature_dependents(self, feature_key: str) -> List[Dependency]:
        """Get all features that depend on this feature.
        
        Args:
            feature_key: Feature key
            
        Returns:
            List of dependencies where this feature is the target
            
        Raises:
            ValueError: If feature does not exist
        """
        if feature_key not in self.nodes:
            raise ValueError(f"Feature not registered: {feature_key}")
        
        return [
            dep for (_, tgt), dep in self.edges.items()
            if tgt == feature_key
        ]
    
    def get_dependency(self, source: str, target: str) -> Optional[Dependency]:
        """Get the dependency between two features.
        
        Args:
            source: Source feature key
            target: Target feature key
            
        Returns:
            Dependency if it exists, None otherwise
        """
        return self.edges.get((source, target))
    
    def remove_dependency(self, source: str, target: str) -> bool:
        """Remove a dependency between features.
        
        Args:
            source: Source feature key
            target: Target feature key
            
        Returns:
            True if dependency was removed, False if it didn't exist
        """
        edge_key = (source, target)
        if edge_key not in self.edges:
            return False
        
        # Remove from graph
        del self.edges[edge_key]
        self.nodes[source].parents.remove(target)
        self.nodes[target].children.remove(source)
        
        return True
    
    def get_lineage(self, feature_key: str, max_depth: int = -1) -> Dict[str, Set[str]]:
        """Get the lineage graph of a feature.
        
        This includes all ancestors (dependencies) of the feature up to the
        specified depth.
        
        Args:
            feature_key: Feature key
            max_depth: Maximum depth to traverse (-1 for unlimited)
            
        Returns:
            Dictionary mapping feature keys to sets of dependency feature keys
            
        Raises:
            ValueError: If feature does not exist
        """
        if feature_key not in self.nodes:
            raise ValueError(f"Feature not registered: {feature_key}")
        
        # Build lineage graph using BFS
        lineage: Dict[str, Set[str]] = {feature_key: set()}
        queue: List[Tuple[str, int]] = [(feature_key, 0)]
        visited: Set[str] = {feature_key}
        
        while queue:
            current, depth = queue.pop(0)
            
            if max_depth >= 0 and depth >= max_depth:
                continue
            
            # Add parents to lineage
            for parent in self.nodes[current].parents:
                lineage[current].add(parent)
                
                if parent not in visited:
                    visited.add(parent)
                    queue.append((parent, depth + 1))
                    lineage[parent] = set()
        
        return lineage
    
    def get_impact(self, feature_key: str, max_depth: int = -1) -> Dict[str, Set[str]]:
        """Get the impact graph of a feature.
        
        This includes all descendants (dependents) of the feature up to the
        specified depth.
        
        Args:
            feature_key: Feature key
            max_depth: Maximum depth to traverse (-1 for unlimited)
            
        Returns:
            Dictionary mapping feature keys to sets of dependent feature keys
            
        Raises:
            ValueError: If feature does not exist
        """
        if feature_key not in self.nodes:
            raise ValueError(f"Feature not registered: {feature_key}")
        
        # Build impact graph using BFS
        impact: Dict[str, Set[str]] = {feature_key: set()}
        queue: List[Tuple[str, int]] = [(feature_key, 0)]
        visited: Set[str] = {feature_key}
        
        while queue:
            current, depth = queue.pop(0)
            
            if max_depth >= 0 and depth >= max_depth:
                continue
            
            # Add children to impact
            for child in self.nodes[current].children:
                impact[current].add(child)
                
                if child not in visited:
                    visited.add(child)
                    queue.append((child, depth + 1))
                    impact[child] = set()
        
        return impact
    
    def get_all_features(self) -> List[str]:
        """Get all registered features.
        
        Returns:
            List of all feature keys
        """
        return list(self.nodes.keys())
    
    def get_feature_metadata(self, feature_key: str) -> Dict[str, str]:
        """Get metadata for a feature.
        
        Args:
            feature_key: Feature key
            
        Returns:
            Metadata dictionary
            
        Raises:
            ValueError: If feature does not exist
        """
        if feature_key not in self.nodes:
            raise ValueError(f"Feature not registered: {feature_key}")
        
        return self.nodes[feature_key].metadata
    
    def update_feature_metadata(
        self, 
        feature_key: str, 
        metadata: Dict[str, str]
    ) -> None:
        """Update metadata for a feature.
        
        Args:
            feature_key: Feature key
            metadata: New metadata (will be merged with existing)
            
        Raises:
            ValueError: If feature does not exist
        """
        if feature_key not in self.nodes:
            raise ValueError(f"Feature not registered: {feature_key}")
        
        # Merge with existing metadata
        self.nodes[feature_key].metadata.update(metadata)
    
    def clear(self) -> None:
        """Clear all lineage data."""
        self.nodes.clear()
        self.edges.clear()
    
    def __len__(self) -> int:
        """Get the number of features.
        
        Returns:
            Number of features
        """
        return len(self.nodes)