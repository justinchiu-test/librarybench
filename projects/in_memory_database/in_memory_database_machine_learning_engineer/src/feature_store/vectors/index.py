"""
Vector indexing for efficient similarity searches.
"""

import logging
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, Union, cast

import faiss
import numpy as np
from pydantic import BaseModel, Field, validator

from feature_store.vectors.base import Distance, VectorBase
from feature_store.vectors.dense import DenseVector
from feature_store.vectors.sparse import SparseVector

logger = logging.getLogger(__name__)


class IndexType(Enum):
    """Supported vector index types."""
    
    FLAT = auto()  # Exact search, no indexing
    IVF = auto()   # Inverted file index
    HNSW = auto()  # Hierarchical Navigable Small World
    LSH = auto()   # Locality-Sensitive Hashing
    PQ = auto()    # Product Quantization


class VectorIndex(BaseModel):
    """
    Index for efficient similarity searches with vectors.
    
    This class provides sub-linear time complexity for nearest neighbor
    search operations using the FAISS library.
    """

    dimensionality: int = Field(..., description="Dimensionality of vectors in the index")
    metric: Distance = Field(Distance.EUCLIDEAN, description="Distance metric used by the index")
    index_type: IndexType = Field(IndexType.FLAT, description="Type of index to use")
    
    # Internal state
    _index: Optional[faiss.Index] = None
    _id_map: Dict[int, str] = Field(default_factory=dict)
    _vec_map: Dict[str, VectorBase] = Field(default_factory=dict)
    _next_id: int = Field(default=0)
    
    class Config:
        """Pydantic configuration."""
        
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        """Initialize a vector index.
        
        Args:
            **data: Fields to initialize with
        """
        super().__init__(**data)
        self._initialize_index()
    
    def _initialize_index(self) -> None:
        """Initialize the FAISS index based on configuration."""
        metric_str = self._get_faiss_metric()
        
        if self.index_type == IndexType.FLAT:
            self._index = faiss.IndexFlat(self.dimensionality, metric_str)
        
        elif self.index_type == IndexType.IVF:
            # IVF with 100 centroids for medium-sized datasets
            quantizer = faiss.IndexFlat(self.dimensionality, metric_str)
            self._index = faiss.IndexIVFFlat(
                quantizer, self.dimensionality, 100, metric_str
            )
            self._index.nprobe = 10  # Number of centroids to visit during search
        
        elif self.index_type == IndexType.HNSW:
            # HNSW index for efficient approximate search
            self._index = faiss.IndexHNSWFlat(self.dimensionality, 32, metric_str)
            self._index.hnsw.efConstruction = 40  # Build-time exploration factor
            self._index.hnsw.efSearch = 16  # Search-time exploration factor
        
        elif self.index_type == IndexType.LSH:
            # LSH index for very large datasets
            bits_per_dim = 2  # 2 bits per dimension for a good trade-off
            nbits = self.dimensionality * bits_per_dim
            self._index = faiss.IndexLSH(self.dimensionality, nbits)
        
        elif self.index_type == IndexType.PQ:
            # Product Quantization for memory-efficient storage
            # Using 8 sub-vectors and 8 bits per sub-vector
            nbits = 8
            m = min(self.dimensionality // 4, 16)  # Number of sub-vectors
            self._index = faiss.IndexPQ(self.dimensionality, m, nbits, metric_str)
        
        else:
            raise ValueError(f"Unsupported index type: {self.index_type}")
        
        # Initialize the index if it's an IVF index
        if isinstance(self._index, faiss.IndexIVFFlat) and not self._index.is_trained:
            logger.info("IVF index needs to be trained before use.")
    
    def _get_faiss_metric(self) -> int:
        """Convert our Distance enum to FAISS metric.
        
        Returns:
            FAISS metric constant
        """
        if self.metric == Distance.EUCLIDEAN:
            return faiss.METRIC_L2
        elif self.metric in (Distance.COSINE, Distance.DOT_PRODUCT):
            return faiss.METRIC_INNER_PRODUCT
        else:
            # FAISS doesn't support Manhattan or Mahalanobis directly
            # We'll fall back to Euclidean
            logger.warning(
                f"Distance metric {self.metric} not directly supported by FAISS. "
                f"Falling back to Euclidean distance."
            )
            return faiss.METRIC_L2
    
    def add(self, key: str, vector: VectorBase) -> None:
        """Add a vector to the index.
        
        Args:
            key: Unique identifier for the vector
            vector: Vector to add
            
        Raises:
            ValueError: If the vector dimension doesn't match the index
            ValueError: If the key already exists in the index
        """
        if len(vector) != self.dimensionality:
            raise ValueError(f"Vector dimensionality ({len(vector)}) "
                           f"doesn't match index dimensionality ({self.dimensionality})")
        
        if key in self._vec_map:
            raise ValueError(f"Key already exists in index: {key}")
        
        # Normalize vector for cosine similarity if needed
        vec_data = vector.to_array()
        if self.metric == Distance.COSINE:
            norm = np.linalg.norm(vec_data)
            if norm > 0:
                vec_data = vec_data / norm
        
        # For dot product, we use negative values since FAISS maximizes dot product
        if self.metric == Distance.DOT_PRODUCT:
            vec_data = -vec_data
        
        # Add to FAISS index
        vec_data = np.array([vec_data], dtype=np.float32)
        
        # Train IVF index if needed
        if isinstance(self._index, faiss.IndexIVF) and not self._index.is_trained:
            if self._next_id >= 100:  # Enough vectors to train
                # Collect all vectors for training
                train_data = np.zeros((len(self._vec_map), self.dimensionality), dtype=np.float32)
                for i, vec in enumerate(self._vec_map.values()):
                    train_data[i] = vec.to_array()
                self._index.train(train_data)
                logger.info("IVF index trained.")
            else:
                # Not enough vectors to train yet, use flat index temporarily
                logger.debug("Not enough vectors to train IVF index yet.")
        
        # Add to index
        self._index.add(vec_data)
        
        # Update mappings
        self._id_map[self._next_id] = key
        self._vec_map[key] = vector
        self._next_id += 1
    
    def remove(self, key: str) -> None:
        """Remove a vector from the index.
        
        Args:
            key: Unique identifier for the vector to remove
            
        Raises:
            KeyError: If the key doesn't exist in the index
            RuntimeError: If removing from the index is not supported
        """
        if key not in self._vec_map:
            raise KeyError(f"Key not found in index: {key}")
        
        # Find the internal ID for this key
        internal_id = None
        for id_val, k in self._id_map.items():
            if k == key:
                internal_id = id_val
                break
        
        if internal_id is None:
            raise RuntimeError(f"Internal ID not found for key: {key}")
        
        # Check if this index type supports removal
        if (hasattr(self._index, 'remove_ids') and 
            callable(getattr(self._index, 'remove_ids'))):
            # Convert to numpy array of IDs to remove
            ids_to_remove = np.array([internal_id], dtype=np.int64)
            self._index.remove_ids(ids_to_remove)
        else:
            # For index types that don't support removal, we need to rebuild
            logger.warning(
                f"Index type {self.index_type} doesn't support direct removal. "
                f"Rebuilding the entire index."
            )
            self._rebuild_without_key(key)
        
        # Update mappings
        del self._vec_map[key]
        del self._id_map[internal_id]
    
    def _rebuild_without_key(self, key_to_remove: str) -> None:
        """Rebuild the index without the specified key.
        
        Args:
            key_to_remove: Key to exclude from the rebuilt index
        """
        # Save the current vectors except the one to remove
        saved_vectors = {k: v for k, v in self._vec_map.items() if k != key_to_remove}
        
        # Reset the index
        self._index = None
        self._id_map = {}
        self._vec_map = {}
        self._next_id = 0
        
        # Reinitialize the index
        self._initialize_index()
        
        # Re-add all vectors
        for k, v in saved_vectors.items():
            self.add(k, v)
    
    def search(
        self, 
        query: Union[VectorBase, np.ndarray], 
        k: int = 10,
        metric: Optional[Distance] = None
    ) -> List[Tuple[str, float]]:
        """Search for the k nearest vectors to the query.
        
        Args:
            query: Query vector or array
            k: Number of nearest neighbors to return
            metric: Override the index's distance metric (only for post-processing)
            
        Returns:
            List of (key, distance) pairs, ordered by increasing distance
            
        Raises:
            ValueError: If the query dimension doesn't match the index
        """
        if isinstance(query, VectorBase):
            if len(query) != self.dimensionality:
                raise ValueError(f"Query dimensionality ({len(query)}) "
                               f"doesn't match index dimensionality ({self.dimensionality})")
            query_vector = query.to_array()
        elif isinstance(query, np.ndarray):
            if len(query) != self.dimensionality:
                raise ValueError(f"Query dimensionality ({len(query)}) "
                               f"doesn't match index dimensionality ({self.dimensionality})")
            query_vector = query
        else:
            raise TypeError(f"Query must be a VectorBase or numpy array, got {type(query)}")
        
        # Handle empty index
        if len(self._vec_map) == 0:
            return []
        
        # Limit k to the number of vectors in the index
        k = min(k, len(self._vec_map))
        
        # Normalize query for cosine similarity if needed
        if self.metric == Distance.COSINE:
            norm = np.linalg.norm(query_vector)
            if norm > 0:
                query_vector = query_vector / norm
        
        # For dot product, we use negative values since FAISS maximizes dot product
        if self.metric == Distance.DOT_PRODUCT:
            query_vector = -query_vector
        
        # Prepare query for FAISS
        query_vector = np.array([query_vector], dtype=np.float32)
        
        # Search with FAISS
        distances, indices = self._index.search(query_vector, k)
        
        # Convert results to list of (key, distance) pairs
        results = []
        for i in range(min(len(indices[0]), k)):
            idx = indices[0][i]
            # Skip invalid indices (can happen with some index types)
            if idx < 0 or idx >= self._next_id or idx not in self._id_map:
                continue
                
            key = self._id_map[idx]
            distance = distances[0][i]
            
            # For cosine and dot product, convert back to proper distance
            if self.metric == Distance.COSINE:
                # FAISS returns negative cosine similarity, convert to cosine distance
                distance = 1.0 - (-distance)
            elif self.metric == Distance.DOT_PRODUCT:
                # FAISS returns negative dot product, negate to get actual value
                distance = -distance
            
            # If a different metric was requested, recalculate distances
            if metric is not None and metric != self.metric:
                vec = self._vec_map[key]
                if isinstance(query, VectorBase):
                    distance = query.distance(vec, metric)
                else:
                    distance = VectorBase.calculate_distance(query, vec.to_array(), metric)
            
            results.append((key, float(distance)))
        
        # Sort by distance (important if we recalculated distances)
        results.sort(key=lambda x: x[1])
        
        return results
    
    def get(self, key: str) -> Optional[VectorBase]:
        """Get a vector by key.
        
        Args:
            key: Key of the vector to retrieve
            
        Returns:
            The vector if found, None otherwise
        """
        return self._vec_map.get(key)
    
    def contains(self, key: str) -> bool:
        """Check if a key exists in the index.
        
        Args:
            key: Key to check
            
        Returns:
            True if the key exists, False otherwise
        """
        return key in self._vec_map
    
    def keys(self) -> List[str]:
        """Get all keys in the index.
        
        Returns:
            List of all keys
        """
        return list(self._vec_map.keys())
    
    def clear(self) -> None:
        """Clear the index."""
        self._index = None
        self._id_map = {}
        self._vec_map = {}
        self._next_id = 0
        self._initialize_index()
    
    def __len__(self) -> int:
        """Get the number of vectors in the index.
        
        Returns:
            Number of vectors
        """
        return len(self._vec_map)
    
    def __contains__(self, key: str) -> bool:
        """Check if a key exists in the index.
        
        Args:
            key: Key to check
            
        Returns:
            True if the key exists, False otherwise
        """
        return self.contains(key)