"""
Batch operation engine with vectorized retrieval.

This module provides tools for efficient batch operations, dramatically improving
throughput for batch inference scenarios through vectorized operations and
optimized memory access patterns.
"""

from feature_store.batching.batch_retriever import BatchRetriever
from feature_store.batching.parallel import ParallelProcessor

__all__ = ["BatchRetriever", "ParallelProcessor"]