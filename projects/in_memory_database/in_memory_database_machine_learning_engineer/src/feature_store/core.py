"""
Main FeatureStore class integrating all components.
"""

import json
import os
import time
from typing import Dict, List, Optional, Set, Tuple, Union, cast, Any

import numpy as np
from pydantic import BaseModel, Field, validator

from feature_store.batching.batch_retriever import BatchRetriever
from feature_store.batching.parallel import ParallelProcessor
from feature_store.experimentation.experiment import Experiment, ExperimentGroup, ExperimentStatus
from feature_store.transformations.base import Transformation
from feature_store.transformations.pipeline import TransformationPipeline
from feature_store.vectors.base import Distance, VectorBase
from feature_store.vectors.dense import DenseVector
from feature_store.vectors.index import IndexType, VectorIndex
from feature_store.vectors.sparse import SparseVector
from feature_store.versioning.lineage import DependencyType, LineageTracker
from feature_store.versioning.timeline import Timeline
from feature_store.versioning.version_store import FeatureGroup, VersionStore


class MemoryUsage(BaseModel):
    """Memory usage statistics."""
    
    total_bytes: int = Field(0, description="Total memory usage in bytes")
    vectors_bytes: int = Field(0, description="Memory used by vectors in bytes")
    indices_bytes: int = Field(0, description="Memory used by indices in bytes")
    versions_bytes: int = Field(0, description="Memory used by versions in bytes")
    transformations_bytes: int = Field(0, description="Memory used by transformations in bytes")
    experiments_bytes: int = Field(0, description="Memory used by experiments in bytes")
    
    @property
    def total_mb(self) -> float:
        """Get total memory usage in MB.
        
        Returns:
            Memory usage in MB
        """
        return self.total_bytes / (1024 * 1024)
    
    @property
    def vectors_mb(self) -> float:
        """Get vector memory usage in MB.
        
        Returns:
            Memory usage in MB
        """
        return self.vectors_bytes / (1024 * 1024)
    
    @property
    def indices_mb(self) -> float:
        """Get index memory usage in MB.
        
        Returns:
            Memory usage in MB
        """
        return self.indices_bytes / (1024 * 1024)
    
    @property
    def versions_mb(self) -> float:
        """Get version memory usage in MB.
        
        Returns:
            Memory usage in MB
        """
        return self.versions_bytes / (1024 * 1024)
    
    @property
    def transformations_mb(self) -> float:
        """Get transformation memory usage in MB.
        
        Returns:
            Memory usage in MB
        """
        return self.transformations_bytes / (1024 * 1024)
    
    @property
    def experiments_mb(self) -> float:
        """Get experiment memory usage in MB.
        
        Returns:
            Memory usage in MB
        """
        return self.experiments_bytes / (1024 * 1024)


class FeatureStore(BaseModel):
    """
    Main FeatureStore class integrating all components.
    
    This class provides the main API for the feature store, integrating all
    components: vectors, versioning, transformations, batching, and experimentation.
    """

    # Vector storage
    vector_indices: Dict[str, VectorIndex] = Field(default_factory=dict)
    
    # Version storage
    version_store: VersionStore = Field(default_factory=VersionStore)
    
    # Transformation registry
    transformations: Dict[str, Dict[str, Transformation]] = Field(default_factory=dict)
    
    # Experiment registry
    experiments: Dict[str, Experiment] = Field(default_factory=dict)
    experiment_groups: Dict[str, ExperimentGroup] = Field(default_factory=dict)
    
    # Configuration
    max_memory_bytes: Optional[int] = Field(None, description="Maximum memory usage in bytes")
    default_index_type: IndexType = Field(IndexType.FLAT, description="Default index type")
    auto_create_groups: bool = Field(True, description="Whether to auto-create feature groups")
    cache_enabled: bool = Field(True, description="Whether to enable caching")
    
    # Performance tracking
    _last_memory_check: float = Field(0, description="Timestamp of last memory check")
    _memory_check_interval: float = Field(60.0, description="Interval between memory checks in seconds")
    
    class Config:
        """Pydantic configuration."""
        
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        """Initialize a FeatureStore instance.
        
        Args:
            **data: Fields to initialize with
        """
        super().__init__(**data)
        
        # Create default index for all vectors
        if "all" not in self.vector_indices:
            self._create_index("all", 0, IndexType.FLAT)
    
    def _check_memory_usage(self) -> None:
        """Check memory usage and enforce limit if configured."""
        # Check if we need to check memory usage
        now = time.time()
        if now - self._last_memory_check < self._memory_check_interval:
            return
        
        # Update timestamp
        self._last_memory_check = now
        
        # Skip if no memory limit is set
        if self.max_memory_bytes is None:
            return
        
        # Get current memory usage
        usage = self.get_memory_usage()
        
        # Check if we're over the limit
        if usage.total_bytes > self.max_memory_bytes:
            raise MemoryError(f"Memory usage ({usage.total_mb:.2f} MB) exceeds "
                            f"limit ({self.max_memory_bytes / (1024 * 1024):.2f} MB)")
    
    def get_memory_usage(self) -> MemoryUsage:
        """Get memory usage statistics.
        
        Returns:
            MemoryUsage object with statistics
        """
        # This is an approximation based on the number and size of objects
        # A more accurate measurement would require deep inspection of objects
        
        # Initialize usage
        usage = MemoryUsage()
        
        # Estimate vector memory usage
        vectors_count = 0
        avg_vector_dims = 0
        for index in self.vector_indices.values():
            vectors_count += len(index)
            # Estimate average vector dimensionality
            if len(index) > 0:
                # Sample a vector to get dimensionality
                sample_key = next(iter(index.keys()))
                sample_vector = index.get(sample_key)
                if sample_vector is not None:
                    avg_vector_dims = max(avg_vector_dims, sample_vector.dimensionality)
        
        # Estimate bytes per vector (assuming float32)
        bytes_per_vector = avg_vector_dims * 4  # 4 bytes per float32
        usage.vectors_bytes = vectors_count * bytes_per_vector
        
        # Estimate index memory usage (rough approximation)
        usage.indices_bytes = len(self.vector_indices) * vectors_count * 16  # 16 bytes per index entry
        
        # Estimate version memory usage
        version_count = sum(len(timeline.versions) for timeline in self.version_store.timelines.values())
        usage.versions_bytes = version_count * bytes_per_vector  # Each version stores a vector
        
        # Estimate transformation memory usage (very rough)
        usage.transformations_bytes = len(self.transformations) * 1024  # 1KB per transformation
        
        # Estimate experiment memory usage (very rough)
        usage.experiments_bytes = len(self.experiments) * 1024  # 1KB per experiment
        
        # Calculate total
        usage.total_bytes = (
            usage.vectors_bytes +
            usage.indices_bytes +
            usage.versions_bytes +
            usage.transformations_bytes +
            usage.experiments_bytes
        )
        
        return usage
    
    def _create_index(
        self, 
        group: str, 
        dimensions: int, 
        index_type: Optional[IndexType] = None
    ) -> VectorIndex:
        """Create a vector index for a feature group.
        
        Args:
            group: Feature group name
            dimensions: Dimensionality of vectors
            index_type: Type of index to create
            
        Returns:
            Created VectorIndex
        """
        if index_type is None:
            index_type = self.default_index_type
        
        # Create the index
        index = VectorIndex(
            dimensionality=dimensions,
            index_type=index_type,
            metric=Distance.EUCLIDEAN  # Default metric, can be overridden in queries
        )
        
        # Store the index
        self.vector_indices[group] = index
        
        return index
    
    def _get_index_for_group(
        self, 
        group: Optional[str], 
        dimensions: Optional[int] = None
    ) -> VectorIndex:
        """Get the vector index for a feature group.
        
        Args:
            group: Feature group name (None for default)
            dimensions: Dimensionality of vectors (for auto-creation)
            
        Returns:
            VectorIndex for the group
            
        Raises:
            ValueError: If the group doesn't exist and dimensions is not provided
        """
        # Use default group if not specified
        if group is None:
            group = "all"
        
        # Check if the group exists
        if group in self.vector_indices:
            return self.vector_indices[group]
        
        # Auto-create the group if dimensions is provided
        if dimensions is not None:
            return self._create_index(group, dimensions)
        
        raise ValueError(f"Feature group '{group}' doesn't exist and dimensions not provided")
    
    def _prepare_add(
        self, 
        key: str, 
        vector: VectorBase, 
        group: Optional[str] = None
    ) -> Tuple[str, VectorIndex]:
        """Prepare for adding a vector.
        
        Args:
            key: Unique identifier for the vector
            vector: Vector to add
            group: Feature group name (None for default)
            
        Returns:
            Tuple of (group name, vector index)
        """
        # Use default group if not specified
        if group is None:
            group = "all"
        
        # Check if the group exists, create if not
        if group not in self.vector_indices:
            if not self.auto_create_groups:
                raise ValueError(f"Feature group '{group}' doesn't exist")
            
            # Create the group and index
            self._create_index(group, vector.dimensionality)
        
        # Get the index
        index = self.vector_indices[group]
        
        # Check if dimensions match
        if index.dimensionality != vector.dimensionality:
            raise ValueError(f"Vector dimensionality ({vector.dimensionality}) doesn't match "
                           f"index dimensionality ({index.dimensionality})")
        
        return group, index
    
    def add(
        self, 
        key: str, 
        vector: VectorBase, 
        group: Optional[str] = None,
        version: Optional[str] = None,
        timestamp: Optional[float] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """Add a vector to the feature store.
        
        Args:
            key: Unique identifier for the vector
            vector: Vector to add
            group: Feature group name (None for default)
            version: Optional version tag
            timestamp: Unix timestamp for this version (default: current time)
            metadata: Optional metadata for this version
            
        Returns:
            Version ID
            
        Raises:
            ValueError: If vector dimensions don't match group
        """
        # Check memory usage
        self._check_memory_usage()
        
        # Prepare for adding
        group_name, index = self._prepare_add(key, vector, group)
        
        # Add to vector index
        if index.contains(key):
            # Update existing vector
            index.remove(key)
        index.add(key, vector)
        
        # Add to version store
        version_id = self.version_store.add_feature(
            feature_key=key,
            vector=vector,
            group=group_name,
            tag=version,
            timestamp=timestamp,
            metadata=metadata
        )
        
        return version_id
    
    def get(
        self, 
        key: str, 
        version: Optional[Union[str, float]] = None,
        group: Optional[str] = None,
        apply_transformations: bool = False
    ) -> Optional[VectorBase]:
        """Get a vector from the feature store.
        
        Args:
            key: Unique identifier for the vector
            version: Version to retrieve (tag, timestamp, or None for latest)
            group: Feature group to retrieve from (None for any)
            apply_transformations: Whether to apply transformations
            
        Returns:
            Vector if found, None otherwise
        """
        # Use version store to get vector
        vector = self.version_store.get_feature(key, version)
        
        # If not found and group is specified, try the index
        if vector is None and group is not None:
            if group in self.vector_indices:
                index = self.vector_indices[group]
                vector = index.get(key)
        
        # Apply transformations if requested
        if vector is not None and apply_transformations:
            vector = self._apply_transformations(vector, group)
        
        return vector
    
    def _apply_transformations(
        self, 
        vector: VectorBase, 
        group: Optional[str] = None
    ) -> VectorBase:
        """Apply transformations to a vector.
        
        Args:
            vector: Vector to transform
            group: Feature group name (None for default)
            
        Returns:
            Transformed vector
        """
        # Use default group if not specified
        if group is None:
            group = "all"
        
        # Check if transformations exist for this group
        if group not in self.transformations:
            return vector
        
        # Build a pipeline from all transformations for this group
        transforms = list(self.transformations[group].values())
        
        if not transforms:
            return vector
        
        # If there's only one transformation, apply it directly
        if len(transforms) == 1:
            return transforms[0].transform(vector)
        
        # Otherwise, create a pipeline
        pipeline = TransformationPipeline(
            name="pipeline",
            steps=transforms,
            cache_enabled=self.cache_enabled
        )
        
        # Apply the pipeline
        return pipeline.transform(vector)
    
    def remove(self, key: str, group: Optional[str] = None) -> bool:
        """Remove a vector from the feature store.
        
        Args:
            key: Unique identifier for the vector
            group: Feature group name (None for all groups)
            
        Returns:
            True if the vector was removed, False otherwise
        """
        removed = False
        
        # If group is specified, remove only from that group
        if group is not None:
            if group in self.vector_indices:
                index = self.vector_indices[group]
                if index.contains(key):
                    index.remove(key)
                    removed = True
        else:
            # Remove from all indices
            for index in self.vector_indices.values():
                if index.contains(key):
                    index.remove(key)
                    removed = True
        
        # Note: We don't remove from version store to preserve history
        
        return removed
    
    def query_similar(
        self, 
        query: Union[str, VectorBase],
        k: int = 10,
        metric: Distance = Distance.EUCLIDEAN,
        group: Optional[str] = None
    ) -> List[Tuple[str, float]]:
        """Query for similar vectors.
        
        Args:
            query: Query key or vector
            k: Number of results to return
            metric: Distance metric to use
            group: Feature group to query (None for all)
            
        Returns:
            List of (key, distance) pairs, ordered by increasing distance
        """
        # Check if the query is a key or a vector
        if isinstance(query, str):
            # Query is a key, get the vector
            vector = self.get(query)
            if vector is None:
                return []
        else:
            # Query is a vector
            vector = query
        
        # Use default group if not specified
        if group is None:
            group = "all"
        
        # Check if the group exists
        if group not in self.vector_indices:
            return []
        
        # Get the index
        index = self.vector_indices[group]
        
        # Query the index
        return index.search(vector, k, metric)
    
    def create_group(
        self, 
        name: str, 
        description: str = "", 
        dimensions: int = 0, 
        index_type: Optional[IndexType] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> None:
        """Create a new feature group.
        
        Args:
            name: Group name
            description: Group description
            dimensions: Dimensionality of vectors in the group
            index_type: Type of index to create
            metadata: Additional metadata
            
        Raises:
            ValueError: If group already exists
        """
        # Check if group already exists
        if name in self.vector_indices:
            raise ValueError(f"Feature group '{name}' already exists")
        
        # Create index
        self._create_index(name, dimensions, index_type)
        
        # Create version store group
        self.version_store.create_group(
            name=name,
            description=description,
            metadata=metadata or {}
        )
    
    def register_transformation(
        self, 
        group: str, 
        transformation: Transformation,
        name: Optional[str] = None
    ) -> None:
        """Register a transformation for a feature group.
        
        Args:
            group: Feature group name
            transformation: Transformation to register
            name: Name for the transformation (defaults to transformation.name)
            
        Raises:
            ValueError: If transformation is not fitted
        """
        # Check if transformation is fitted
        if not transformation.is_fitted:
            raise ValueError("Transformation must be fitted before registration")
        
        # Use transformation name if not specified
        if name is None:
            name = transformation.name
        
        # Initialize group if needed
        if group not in self.transformations:
            self.transformations[group] = {}
        
        # Register transformation
        self.transformations[group][name] = transformation
    
    def get_transformation(
        self, 
        group: str, 
        name: str
    ) -> Optional[Transformation]:
        """Get a transformation for a feature group.
        
        Args:
            group: Feature group name
            name: Transformation name
            
        Returns:
            Transformation if found, None otherwise
        """
        if group not in self.transformations:
            return None
        
        return self.transformations[group].get(name)
    
    def list_transformations(self, group: str) -> List[str]:
        """List transformations for a feature group.
        
        Args:
            group: Feature group name
            
        Returns:
            List of transformation names
        """
        if group not in self.transformations:
            return []
        
        return list(self.transformations[group].keys())
    
    def clear_transformations(self, group: str) -> None:
        """Clear all transformations for a feature group.
        
        Args:
            group: Feature group name
        """
        if group in self.transformations:
            self.transformations[group].clear()
    
    def create_experiment(
        self, 
        name: str, 
        groups: List[str], 
        weights: Optional[List[float]] = None,
        description: str = "",
        metadata: Optional[Dict[str, str]] = None,
        activate: bool = True
    ) -> Experiment:
        """Create a new experiment.
        
        Args:
            name: Experiment name
            groups: List of group names
            weights: Weights for each group (must sum to 1, default: equal weights)
            description: Experiment description
            metadata: Additional metadata
            activate: Whether to activate the experiment immediately
            
        Returns:
            Created Experiment
            
        Raises:
            ValueError: If experiment already exists
        """
        # Check if experiment already exists
        if name in self.experiments:
            raise ValueError(f"Experiment '{name}' already exists")
        
        # Use equal weights if not specified
        if weights is None:
            weights = [1.0 / len(groups) for _ in groups]
        
        # Create experiment
        experiment = Experiment.create_percentage_based(
            name=name,
            groups=groups,
            weights=weights,
            description=description,
            metadata=metadata or {}
        )
        
        # Activate if requested
        if activate:
            experiment.activate()
        
        # Store experiment
        self.experiments[name] = experiment
        
        return experiment
    
    def get_experiment(self, name: str) -> Optional[Experiment]:
        """Get an experiment by name.
        
        Args:
            name: Experiment name
            
        Returns:
            Experiment if found, None otherwise
        """
        return self.experiments.get(name)
    
    def get_experiment_group(
        self, 
        key: str, 
        experiment: str
    ) -> Optional[str]:
        """Get the experiment group for a key.
        
        Args:
            key: Key to check
            experiment: Experiment name
            
        Returns:
            Group name if experiment exists and is active, None otherwise
        """
        exp = self.experiments.get(experiment)
        if exp is None or exp.status != ExperimentStatus.ACTIVE:
            return None
        
        return exp.get_group(key)
    
    def add_to_experiment_group(
        self, 
        group_name: str, 
        experiment_name: str
    ) -> None:
        """Add an experiment to an experiment group.
        
        Args:
            group_name: Group name
            experiment_name: Experiment name
            
        Raises:
            ValueError: If experiment doesn't exist
            ValueError: If group doesn't exist
        """
        # Check if experiment exists
        if experiment_name not in self.experiments:
            raise ValueError(f"Experiment '{experiment_name}' doesn't exist")
        
        # Check if group exists, create if not
        if group_name not in self.experiment_groups:
            self.experiment_groups[group_name] = ExperimentGroup(name=group_name)
        
        # Add experiment to group
        self.experiment_groups[group_name].add_experiment(experiment_name)
    
    def create_batch_retriever(
        self, 
        group: Optional[str] = None,
        version: Optional[Union[str, float]] = None,
        apply_transformations: bool = False
    ) -> BatchRetriever:
        """Create a batch retriever for efficient batch operations.
        
        Args:
            group: Feature group name (None for default)
            version: Version to retrieve (tag, timestamp, or None for latest)
            apply_transformations: Whether to apply transformations
            
        Returns:
            BatchRetriever instance
        """
        return BatchRetriever(
            feature_store=self,
            feature_group=group,
            version=version,
            apply_transformations=apply_transformations
        )
    
    def create_parallel_processor(
        self, 
        n_jobs: int = -1,
        backend: str = "threading"
    ) -> ParallelProcessor:
        """Create a parallel processor for parallel operations.
        
        Args:
            n_jobs: Number of parallel jobs (-1 for all cores)
            backend: Parallelization backend (threading or multiprocessing)
            
        Returns:
            ParallelProcessor instance
        """
        return ParallelProcessor(
            n_jobs=n_jobs,
            backend=backend
        )
    
    def batch_get(
        self, 
        keys: List[str], 
        group: Optional[str] = None,
        version: Optional[Union[str, float]] = None,
        apply_transformations: bool = False
    ) -> Dict[str, VectorBase]:
        """Retrieve multiple vectors in a batch.
        
        Args:
            keys: List of keys to retrieve
            group: Feature group name (None for default)
            version: Version to retrieve (tag, timestamp, or None for latest)
            apply_transformations: Whether to apply transformations
            
        Returns:
            Dictionary mapping keys to vectors (missing keys are omitted)
        """
        # Create batch retriever
        retriever = self.create_batch_retriever(
            group=group,
            version=version,
            apply_transformations=apply_transformations
        )
        
        # Retrieve vectors
        result = retriever.batch_get(keys)
        
        return result.vectors
    
    def batch_query_similar(
        self, 
        keys: List[str], 
        k: int = 10,
        metric: Distance = Distance.EUCLIDEAN,
        group: Optional[str] = None
    ) -> Dict[str, List[Tuple[str, float]]]:
        """Query similar vectors for multiple keys in a batch.
        
        Args:
            keys: List of keys to query
            k: Number of similar vectors to return
            metric: Distance metric to use
            group: Feature group to query (None for default)
            
        Returns:
            Dictionary mapping query keys to lists of (match_key, distance) pairs
        """
        # Create batch retriever
        retriever = self.create_batch_retriever(group=group)
        
        # Perform batch query
        result = retriever.batch_query_similar(keys, k, metric)
        
        return result.query_results
    
    def add_dependency(
        self, 
        source: str, 
        target: str, 
        dependency_type: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> None:
        """Add a dependency between features.
        
        Args:
            source: Source feature key
            target: Target feature key
            dependency_type: Type of dependency
            metadata: Additional metadata
            
        Raises:
            ValueError: If either feature doesn't exist
        """
        self.version_store.add_dependency(source, target, dependency_type, metadata)
    
    def get_feature_lineage(
        self, 
        feature_key: str, 
        max_depth: int = -1
    ) -> Dict[str, List[str]]:
        """Get the lineage graph of a feature.
        
        Args:
            feature_key: Feature key
            max_depth: Maximum depth to traverse (-1 for unlimited)
            
        Returns:
            Dictionary mapping feature keys to lists of dependency feature keys
            
        Raises:
            ValueError: If feature doesn't exist
        """
        return self.version_store.get_feature_lineage(feature_key, max_depth)
    
    def export_to_file(self, file_path: str) -> None:
        """Export the feature store to a file.
        
        Args:
            file_path: Path to save to
            
        Raises:
            IOError: If file cannot be written
        """
        # Create export data
        data = self.export_to_dict()
        
        # Write to file
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
    
    def export_to_dict(self) -> Dict[str, Any]:
        """Export the feature store to a dictionary.
        
        Returns:
            Dictionary representation of the feature store
        """
        # Export metadata
        data = {
            "version": "1.0.0",
            "timestamp": time.time(),
            "config": {
                "max_memory_bytes": self.max_memory_bytes,
                "default_index_type": self.default_index_type.name,
                "auto_create_groups": self.auto_create_groups,
                "cache_enabled": self.cache_enabled
            },
            "groups": [],
            "experiments": []
        }
        
        # Export feature groups
        for group_name in self.vector_indices.keys():
            group_data = {
                "name": group_name,
                "dimensions": self.vector_indices[group_name].dimensionality,
                "index_type": self.vector_indices[group_name].index_type.name,
                "feature_count": len(self.vector_indices[group_name])
            }
            
            # Add version store metadata if available
            if self.version_store.group_exists(group_name):
                version_group = self.version_store.groups[group_name]
                group_data["description"] = version_group.description
                group_data["metadata"] = version_group.metadata
            
            data["groups"].append(group_data)
        
        # Export experiments
        for experiment_name, experiment in self.experiments.items():
            exp_data = experiment.get_state_dict()
            data["experiments"].append(exp_data)
        
        return data
    
    @classmethod
    def import_from_file(cls, file_path: str) -> "FeatureStore":
        """Import a feature store from a file.
        
        Args:
            file_path: Path to load from
            
        Returns:
            Imported FeatureStore
            
        Raises:
            IOError: If file cannot be read
            ValueError: If file format is invalid
        """
        # Read from file
        with open(file_path, "r") as f:
            data = json.load(f)
        
        return cls.import_from_dict(data)
    
    @classmethod
    def import_from_dict(cls, data: Dict[str, Any]) -> "FeatureStore":
        """Import a feature store from a dictionary.
        
        Args:
            data: Dictionary representation of the feature store
            
        Returns:
            Imported FeatureStore
            
        Raises:
            ValueError: If data format is invalid
        """
        # Check version
        if "version" not in data:
            raise ValueError("Invalid data format: missing version")
        
        # Create feature store with config
        config = data.get("config", {})
        store = cls(
            max_memory_bytes=config.get("max_memory_bytes"),
            default_index_type=IndexType[config.get("default_index_type", "FLAT")],
            auto_create_groups=config.get("auto_create_groups", True),
            cache_enabled=config.get("cache_enabled", True)
        )
        
        # Import feature groups
        for group_data in data.get("groups", []):
            store.create_group(
                name=group_data["name"],
                description=group_data.get("description", ""),
                dimensions=group_data["dimensions"],
                index_type=IndexType[group_data["index_type"]],
                metadata=group_data.get("metadata", {})
            )
        
        # Import experiments
        for exp_data in data.get("experiments", []):
            experiment = Experiment.from_state_dict(exp_data)
            store.experiments[experiment.name] = experiment
        
        return store