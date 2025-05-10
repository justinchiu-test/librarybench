"""
Vector data types with optimized distance calculations.

This module provides specialized vector types for efficient similarity searches 
and nearest-neighbor queries in feature space. It supports common distance metrics
(Euclidean, cosine, Manhattan, Mahalanobis) and is optimized for ML feature representation.
"""

from feature_store.vectors.base import VectorBase, Distance
from feature_store.vectors.dense import DenseVector
from feature_store.vectors.sparse import SparseVector
from feature_store.vectors.index import VectorIndex

__all__ = ["VectorBase", "DenseVector", "SparseVector", "VectorIndex", "Distance"]