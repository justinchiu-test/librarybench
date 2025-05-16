"""
Vector index implementation for efficient similarity searches.

This module provides a base vector index for storing and retrieving
high-dimensional vectors with optimized distance calculations.
"""

import math
import heapq
import time
from typing import List, Dict, Tuple, Callable, Optional, Set, Any, Iterator, Union
import random
import uuid

from common.core import InMemoryStorage
from vectordb.core.vector import Vector
from vectordb.core.distance import get_distance_function, euclidean_distance


class VectorIndex(InMemoryStorage[Vector]):
    """
    Base vector index for efficient similarity searches.
    
    This class provides a simple but efficient index for vectors
    with support for nearest neighbor queries using various distance metrics.
    """
    
    def __init__(self, distance_metric: str = "euclidean"):
        """
        Initialize a vector index.
        
        Args:
            distance_metric: The distance metric to use for similarity calculations.
                           Supported metrics: euclidean, squared_euclidean, manhattan, 
                           cosine, angular, chebyshev.
                           
        Raises:
            ValueError: If an unsupported distance metric is provided.
        """
        super().__init__()
        self._distance_function = get_distance_function(distance_metric)
        self._distance_metric = distance_metric
        
    @property
    def distance_metric(self) -> str:
        """Get the distance metric used by this index."""
        return self._distance_metric
        
    @property
    def ids(self) -> List[str]:
        """Get a list of all vector IDs in the index."""
        return [record.id for record in self]
        
    @property
    def last_modified(self) -> float:
        """Get the timestamp of the last modification to the index."""
        return self._last_modified
    
    def add(self, vector: Vector, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a vector to the index.
        
        Args:
            vector: The vector to add
            metadata: Optional metadata to associate with the vector
            
        Returns:
            The ID of the added vector
            
        Raises:
            ValueError: If the vector does not have an ID and cannot be added
        """
        # Generate an ID if the vector doesn't have one
        if vector.id is None:
            vector_id = str(uuid.uuid4())
            # Create a new vector with the generated ID
            vector = Vector(vector.values, vector_id)
        
        # Add metadata to the vector if provided
        if metadata is not None:
            vector.metadata.update(metadata)
            
        # Use the InMemoryStorage add method
        return super().add(vector)
    
    def add_batch(self, vectors: List[Vector], metadatas: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """
        Add multiple vectors to the index in a batch.
        
        Args:
            vectors: List of vectors to add
            metadatas: Optional list of metadata dictionaries, one per vector
            
        Returns:
            List of vector IDs that were added
            
        Raises:
            ValueError: If the lengths of vectors and metadatas don't match
        """
        if metadatas is not None and len(vectors) != len(metadatas):
            raise ValueError("Number of vectors and metadata dictionaries must match")
            
        ids = []
        for i, vector in enumerate(vectors):
            metadata = metadatas[i] if metadatas is not None else None
            ids.append(self.add(vector, metadata))
            
        return ids
    
    def get(self, record_id: str) -> Optional[Vector]:
        """
        Retrieve a vector by its ID.
        
        Args:
            record_id: The ID of the vector to retrieve
            
        Returns:
            The vector if found, None otherwise
        """
        return super().get(record_id)
    
    def get_metadata(self, record_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve metadata for a vector.
        
        Args:
            record_id: The ID of the vector
            
        Returns:
            Metadata dictionary if found, None otherwise
        """
        vector = self.get(record_id)
        if vector is None:
            return None
        return vector.metadata
    
    def update_metadata(self, record_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Update the metadata for a vector.
        
        Args:
            record_id: The ID of the vector
            metadata: The new metadata dictionary
            
        Returns:
            True if the metadata was updated, False if the vector was not found
        """
        vector = self.get(record_id)
        if vector is None:
            return False
        
        vector.metadata.update(metadata)
        vector.updated_at = time.time()
        return True
    
    def distance(self, v1: Union[str, Vector], v2: Union[str, Vector]) -> float:
        """
        Calculate the distance between two vectors.
        
        Args:
            v1: Either a vector ID or a Vector object
            v2: Either a vector ID or a Vector object
            
        Returns:
            The distance between the vectors
            
        Raises:
            ValueError: If either vector ID is not found or vectors have different dimensions
        """
        # Get actual vector objects if IDs were provided
        vec1 = self._get_vector_object(v1)
        vec2 = self._get_vector_object(v2)
        
        return self._distance_function(vec1, vec2)
    
    def nearest(self, query: Union[str, Vector], k: int = 1, filter_fn: Optional[Callable[[str, Dict[str, Any]], bool]] = None) -> List[Tuple[str, float]]:
        """
        Find the k nearest vectors to the query vector.
        
        Args:
            query: Query vector or vector ID
            k: Number of nearest neighbors to return
            filter_fn: Optional function to filter vectors based on ID and metadata
            
        Returns:
            List of (id, distance) tuples for the nearest vectors, sorted by distance
            
        Raises:
            ValueError: If the query vector ID is not found
        """
        if k < 1:
            raise ValueError("k must be at least 1")
            
        if len(self) == 0:
            return []
            
        # Ensure we have a Vector object
        query_vector = self._get_vector_object(query)
        
        # Calculate distances and filter results
        distances = []
        for record in self:
            # Skip if the filter excludes this vector
            if filter_fn is not None and not filter_fn(record.id, record.metadata):
                continue
                
            # Skip if this is the query vector itself
            if isinstance(query, str) and query == record.id:
                continue
                
            dist = self._distance_function(query_vector, record)
            distances.append((record.id, dist))
        
        # Sort by distance and return the k nearest
        return sorted(distances, key=lambda x: x[1])[:k]
    
    def nearest_with_metadata(self, query: Union[str, Vector], k: int = 1, filter_fn: Optional[Callable[[str, Dict[str, Any]], bool]] = None) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Find the k nearest vectors to the query vector, including their metadata.
        
        Args:
            query: Query vector or vector ID
            k: Number of nearest neighbors to return
            filter_fn: Optional function to filter vectors based on ID and metadata
            
        Returns:
            List of (id, distance, metadata) tuples for the nearest vectors, sorted by distance
        """
        nearest_results = self.nearest(query, k, filter_fn)
        
        # Add metadata to each result
        return [(id, dist, self.get(id).metadata) for id, dist in nearest_results]
    
    def _get_vector_object(self, vector_or_id: Union[str, Vector]) -> Vector:
        """
        Get a Vector object from either a vector or an ID.
        
        Args:
            vector_or_id: Either a Vector object or a vector ID
            
        Returns:
            The Vector object
            
        Raises:
            ValueError: If the ID doesn't exist in the index
        """
        if isinstance(vector_or_id, str):
            vector = self.get(vector_or_id)
            if vector is None:
                raise ValueError(f"Vector with ID '{vector_or_id}' not found in the index")
            return vector
        return vector_or_id
    
    def sample(self, n: int, seed: Optional[int] = None) -> List[Vector]:
        """
        Sample n random vectors from the index.
        
        Args:
            n: Number of vectors to sample
            seed: Optional random seed for reproducibility
            
        Returns:
            List of sampled Vector objects
            
        Raises:
            ValueError: If n is greater than the number of vectors in the index
        """
        if n > len(self):
            raise ValueError(f"Cannot sample {n} vectors from an index of size {len(self)}")
            
        if seed is not None:
            random.seed(seed)
            
        all_ids = [record.id for record in self]
        sampled_ids = random.sample(all_ids, n)
        return [self.get(id) for id in sampled_ids]
    
    def remove(self, record_id: str) -> bool:
        """
        Remove a vector from the index.
        
        Args:
            record_id: The ID of the vector to remove
            
        Returns:
            True if the vector was removed, False if it wasn't in the index
        """
        # Use the underlying InMemoryStorage's removal method
        vector = self.get(record_id)
        if vector is None:
            return False
            
        self.delete(record_id)
        return True
    
    def remove_batch(self, record_ids: List[str]) -> Union[List[bool], int]:
        """
        Remove multiple vectors from the index in a batch.
        
        Args:
            record_ids: List of vector IDs to remove
            
        Returns:
            Either the count of successfully removed vectors (for backward compatibility)
            or a list of booleans indicating whether each vector was removed
        """
        results = []
        for record_id in record_ids:
            result = self.remove(record_id)
            results.append(result)
            
        # Return the count of True values for backward compatibility
        return sum(1 for r in results if r)