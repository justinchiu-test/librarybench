"""
Batch retriever for efficient vector retrieval.
"""

import time
from typing import Dict, List, Optional, Set, Tuple, Union, Any

import numpy as np
from pydantic import BaseModel, Field

from feature_store.vectors.base import Distance, VectorBase


class BatchResult(BaseModel):
    """Results from a batch retrieval operation."""
    
    vectors: Dict[str, VectorBase] = Field(..., description="Map of key to vector")
    missing_keys: List[str] = Field(default_factory=list, description="Keys that were not found")
    timing: Dict[str, float] = Field(default_factory=dict, description="Timing information")
    
    class Config:
        """Pydantic configuration."""
        
        arbitrary_types_allowed = True


class BatchQueryResult(BatchResult):
    """Results from a batch similarity query operation."""
    
    query_results: Dict[str, List[Tuple[str, float]]] = Field(
        default_factory=dict, 
        description="Map of query key to list of (match_key, distance) pairs"
    )


class BatchOperation(BaseModel):
    """Base class for batch operations."""
    
    max_batch_size: int = Field(10000, description="Maximum number of keys to process in a batch")
    
    def get_batch_size(self, keys: List[str]) -> int:
        """Get the batch size for the given keys.
        
        Args:
            keys: List of keys to process
            
        Returns:
            Batch size to use
        """
        return min(len(keys), self.max_batch_size)


class BatchRetriever(BatchOperation):
    """
    Batch retriever for efficient vector retrieval.
    
    This class provides optimized batch operations for retrieving and
    processing multiple vectors at once.
    """

    feature_store: Any = Field(..., description="FeatureStore instance")
    feature_group: Optional[str] = Field(None, description="Feature group to retrieve from")
    version: Optional[Union[str, float]] = Field(None, description="Version to retrieve")
    apply_transformations: bool = Field(False, description="Whether to apply transformations")
    log_timing: bool = Field(False, description="Whether to log timing information")
    profiling_enabled: bool = Field(False, description="Whether to profile operations")
    
    class Config:
        """Pydantic configuration."""
        
        arbitrary_types_allowed = True
    
    def batch_get(self, keys: List[str]) -> BatchResult:
        """Retrieve multiple vectors in a batch.
        
        Args:
            keys: List of keys to retrieve
            
        Returns:
            BatchResult with retrieved vectors and missing keys
        """
        # Start timing
        start_time = time.time()
        timing = {}
        
        # Deduplicate keys
        unique_keys = list(set(keys))
        
        # Initialize result
        vectors = {}
        missing_keys = []
        
        # Record key preparation time
        if self.profiling_enabled:
            timing["prepare_keys"] = time.time() - start_time
            timing["num_keys"] = len(unique_keys)
        
        # Start retrieval time
        retrieval_start = time.time()
        
        # Process in batches if needed
        batch_size = self.get_batch_size(unique_keys)
        if len(unique_keys) > batch_size:
            # Process in batches
            for i in range(0, len(unique_keys), batch_size):
                batch_keys = unique_keys[i:i+batch_size]
                batch_result = self._get_batch(batch_keys)
                vectors.update(batch_result.vectors)
                missing_keys.extend(batch_result.missing_keys)
                
                # Update timing
                if self.profiling_enabled:
                    for k, v in batch_result.timing.items():
                        if k in timing:
                            timing[k] += v
                        else:
                            timing[k] = v
        else:
            # Process in a single batch
            batch_result = self._get_batch(unique_keys)
            vectors = batch_result.vectors
            missing_keys = batch_result.missing_keys
            
            # Update timing
            if self.profiling_enabled:
                timing.update(batch_result.timing)
        
        # Record total retrieval time
        if self.profiling_enabled:
            timing["retrieval_total"] = time.time() - retrieval_start
            timing["total"] = time.time() - start_time
        
        # Create result
        result = BatchResult(
            vectors=vectors,
            missing_keys=missing_keys,
            timing=timing if self.log_timing else {}
        )
        
        return result
    
    def _get_batch(self, keys: List[str]) -> BatchResult:
        """Retrieve a batch of vectors.
        
        Args:
            keys: List of keys to retrieve
            
        Returns:
            BatchResult with retrieved vectors and missing keys
        """
        # Start timing
        start_time = time.time()
        timing = {}
        
        # Get vectors from feature store
        vectors = {}
        missing_keys = []
        
        for key in keys:
            vector = self.feature_store.get(
                key, 
                group=self.feature_group,
                version=self.version,
                apply_transformations=self.apply_transformations
            )
            
            if vector is not None:
                vectors[key] = vector
            else:
                missing_keys.append(key)
        
        # Record retrieval time
        if self.profiling_enabled:
            timing["get_vectors"] = time.time() - start_time
            timing["num_vectors"] = len(vectors)
            timing["num_missing"] = len(missing_keys)
        
        # Create result
        result = BatchResult(
            vectors=vectors,
            missing_keys=missing_keys,
            timing=timing
        )
        
        return result
    
    def batch_query_similar(
        self, 
        keys: List[str], 
        k: int = 10,
        metric: Distance = Distance.EUCLIDEAN
    ) -> BatchQueryResult:
        """Query similar vectors for multiple keys in a batch.
        
        Args:
            keys: List of keys to query
            k: Number of similar vectors to return
            metric: Distance metric to use
            
        Returns:
            BatchQueryResult with query results
        """
        # Start timing
        start_time = time.time()
        timing = {}
        
        # Deduplicate keys
        unique_keys = list(set(keys))
        
        # Record key preparation time
        if self.profiling_enabled:
            timing["prepare_keys"] = time.time() - start_time
            timing["num_keys"] = len(unique_keys)
        
        # Get the vectors first
        vectors_start = time.time()
        batch_result = self.batch_get(unique_keys)
        
        # Record vector retrieval time
        if self.profiling_enabled:
            timing["get_vectors"] = time.time() - vectors_start
            timing.update(batch_result.timing)
        
        # Initialize query results
        query_results = {}
        
        # Perform similarity queries
        query_start = time.time()
        for key, vector in batch_result.vectors.items():
            results = self.feature_store.query_similar(
                vector,
                k=k,
                metric=metric,
                group=self.feature_group
            )
            query_results[key] = results
        
        # Record query time
        if self.profiling_enabled:
            timing["similarity_query"] = time.time() - query_start
            timing["total"] = time.time() - start_time
        
        # Create result
        result = BatchQueryResult(
            vectors=batch_result.vectors,
            missing_keys=batch_result.missing_keys,
            query_results=query_results,
            timing=timing if self.log_timing else {}
        )
        
        return result
    
    def batch_get_with_versions(
        self, 
        keys: List[str], 
        versions: List[Union[str, float]]
    ) -> Dict[str, Dict[str, VectorBase]]:
        """Retrieve multiple vectors with multiple versions.
        
        Args:
            keys: List of keys to retrieve
            versions: List of versions to retrieve
            
        Returns:
            Nested dictionary: {key: {version: vector}}
        """
        # Start timing
        start_time = time.time()
        
        # Initialize result
        result = {key: {} for key in keys}
        
        # Process each version
        for version in versions:
            # Set the version for this batch
            self.version = version
            
            # Get vectors for this version
            batch_result = self.batch_get(keys)
            
            # Add to result
            for key, vector in batch_result.vectors.items():
                result[key][str(version)] = vector
        
        # Reset version
        self.version = None
        
        return result
    
    def enable_profiling(self) -> None:
        """Enable profiling."""
        self.profiling_enabled = True
        self.log_timing = True
    
    def disable_profiling(self) -> None:
        """Disable profiling."""
        self.profiling_enabled = False
        self.log_timing = False