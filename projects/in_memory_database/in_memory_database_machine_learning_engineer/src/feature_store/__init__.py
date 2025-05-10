"""
FeatureStore: A specialized in-memory database optimized for machine learning workflows.

This package provides efficient storage and retrieval of feature vectors,
with built-in support for similarity searches, versioning, batch operations,
and A/B testing.
"""

from feature_store.core import FeatureStore
from feature_store.vectors import DenseVector, SparseVector, VectorBase

__all__ = [
    "FeatureStore",
    "DenseVector",
    "SparseVector",
    "VectorBase",
]