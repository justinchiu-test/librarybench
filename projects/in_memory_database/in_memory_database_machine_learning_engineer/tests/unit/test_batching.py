"""
Unit tests for batch operations.
"""

import time
from typing import Dict, List, Optional, Set, Tuple

import numpy as np
import pytest
from pytest import approx

from feature_store.batching.batch_retriever import BatchOperation, BatchResult, BatchRetriever
from feature_store.batching.parallel import ChunkResult, ParallelProcessor
from feature_store.core import FeatureStore
from feature_store.vectors.base import Distance
from feature_store.vectors.dense import DenseVector


class MockFeatureStore:
    """Mock feature store for testing batch operations."""
    
    def __init__(self):
        """Initialize mock feature store."""
        self.vectors = {}
        self.groups = {}
    
    def add(self, key: str, vector, group: Optional[str] = None):
        """Add a vector to the mock store."""
        self.vectors[key] = vector
        if group:
            if group not in self.groups:
                self.groups[group] = set()
            self.groups[group].add(key)
    
    def get(self, key: str, group: Optional[str] = None, version=None, apply_transformations=False):
        """Get a vector from the mock store."""
        if group:
            if group not in self.groups or key not in self.groups[group]:
                return None
        return self.vectors.get(key)
    
    def query_similar(self, query, k=10, metric=Distance.EUCLIDEAN, group=None):
        """Query similar vectors (simplified mock implementation)."""
        # Return all vectors sorted by distance
        results = []
        vector = query if not isinstance(query, str) else self.vectors.get(query)
        
        if vector is None:
            return []
        
        for key, v in self.vectors.items():
            if group and (group not in self.groups or key not in self.groups[group]):
                continue
            distance = vector.distance(v, metric)
            results.append((key, distance))
        
        # Sort by distance
        results.sort(key=lambda x: x[1])
        return results[:k]


class TestBatchRetriever:
    """Tests for BatchRetriever class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_store = MockFeatureStore()
        
        # Add vectors to the mock store
        for i in range(10):
            key = f"key_{i}"
            vector = DenseVector([float(i), float(i*2), float(i*3)])
            self.mock_store.add(key, vector, "group_a" if i < 5 else "group_b")
        
        # Create batch retriever
        self.retriever = BatchRetriever(feature_store=self.mock_store)
    
    def test_batch_get(self):
        """Test batch retrieval."""
        # Get multiple vectors
        keys = ["key_1", "key_3", "key_5", "key_7", "non_existent"]
        result = self.retriever.batch_get(keys)
        
        # Verify result
        assert isinstance(result, BatchResult)
        assert len(result.vectors) == 4
        assert len(result.missing_keys) == 1
        assert "non_existent" in result.missing_keys
        
        # Verify retrieved vectors
        for key in keys:
            if key != "non_existent":
                assert key in result.vectors
                assert result.vectors[key] == self.mock_store.vectors[key]
    
    def test_batch_get_with_group(self):
        """Test batch retrieval with group filter."""
        # Create batch retriever with group filter
        retriever = BatchRetriever(feature_store=self.mock_store, feature_group="group_a")
        
        # Get vectors
        keys = ["key_1", "key_3", "key_5", "key_7"]
        result = retriever.batch_get(keys)
        
        # Verify result (only keys in group_a should be retrieved)
        assert len(result.vectors) == 2
        assert "key_1" in result.vectors
        assert "key_3" in result.vectors
        assert "key_5" not in result.vectors
        assert "key_7" not in result.vectors
        assert len(result.missing_keys) == 2
        assert "key_5" in result.missing_keys
        assert "key_7" in result.missing_keys
    
    def test_batch_query_similar(self):
        """Test batch similarity query."""
        # Get similar vectors for multiple keys
        keys = ["key_1", "key_5"]
        result = self.retriever.batch_query_similar(keys, k=3)
        
        # Verify result
        assert len(result.vectors) == 2
        assert len(result.query_results) == 2
        assert "key_1" in result.query_results
        assert "key_5" in result.query_results
        
        # Verify query results (should include the query key itself as the closest)
        key1_results = result.query_results["key_1"]
        key5_results = result.query_results["key_5"]
        
        assert len(key1_results) == 3
        assert len(key5_results) == 3
        
        assert key1_results[0][0] == "key_1"  # First result should be the key itself
        assert key1_results[0][1] == approx(0.0)  # Distance to self is 0
        
        assert key5_results[0][0] == "key_5"
        assert key5_results[0][1] == approx(0.0)
    
    def test_large_batch_handling(self):
        """Test handling of large batches."""
        # Set small batch size
        self.retriever.max_batch_size = 2
        
        # Get vectors with batch size exceeding max_batch_size
        keys = ["key_0", "key_1", "key_2", "key_3", "key_4"]
        result = self.retriever.batch_get(keys)
        
        # Verify all vectors are retrieved despite small batch size
        assert len(result.vectors) == 5
        for key in keys:
            assert key in result.vectors
    
    def test_profiling(self):
        """Test profiling mode."""
        # Enable profiling
        self.retriever.enable_profiling()
        
        # Get vectors
        keys = ["key_1", "key_3", "key_5"]
        result = self.retriever.batch_get(keys)
        
        # Verify timing information is present
        assert len(result.timing) > 0
        assert "get_vectors" in result.timing
        
        # Disable profiling
        self.retriever.disable_profiling()
        
        # Get vectors again
        result = self.retriever.batch_get(keys)
        
        # Verify timing information is not present
        assert len(result.timing) == 0


class TestParallelProcessor:
    """Tests for ParallelProcessor class."""

    def test_process_parallel(self):
        """Test parallel processing."""
        processor = ParallelProcessor(n_jobs=2)
        
        # Create sample data
        items = list(range(10))
        
        # Define processing function (square each number)
        def process_fn(chunk):
            return [x ** 2 for x in chunk]
        
        # Process in parallel
        results = processor.process_parallel(items, process_fn)
        
        # Verify results
        assert len(results) == 10
        for i, result in enumerate(results):
            assert result == i ** 2
    
    def test_map_vectors(self):
        """Test mapping function to vectors in parallel."""
        processor = ParallelProcessor(n_jobs=2)
        
        # Create sample vectors
        vectors = {
            f"vec_{i}": DenseVector([float(i), float(i*2)])
            for i in range(5)
        }
        
        # Define mapping function (double each value)
        def map_fn(vector):
            return DenseVector(vector.to_array() * 2)
        
        # Apply map in parallel
        results = processor.map_vectors(vectors, map_fn)
        
        # Verify results
        assert len(results) == 5
        for key, result in results.items():
            i = int(key.split("_")[1])
            expected = np.array([float(i), float(i*2)]) * 2
            assert np.array_equal(result.to_array(), expected)
    
    def test_batch_compute(self):
        """Test batch computation."""
        processor = ParallelProcessor(n_jobs=2)
        
        # Create sample inputs
        inputs = list(range(10))
        
        # Define compute function (fibonacci)
        def fibonacci(n):
            if n <= 1:
                return n
            return fibonacci(n-1) + fibonacci(n-2)
        
        # Compute in parallel
        results = processor.batch_compute(inputs, fibonacci)
        
        # Verify results
        expected = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
        assert results == expected
    
    def test_different_backends(self):
        """Test different parallel backends."""
        # Test threading backend
        processor_threading = ParallelProcessor(n_jobs=2, backend="threading")
        
        # Create sample data
        items = list(range(5))
        
        # Define processing function
        def process_fn(chunk):
            return [x ** 2 for x in chunk]
        
        # Process with threading
        results_threading = processor_threading.process_parallel(items, process_fn)
        
        # Verify results
        assert len(results_threading) == 5
        for i, result in enumerate(results_threading):
            assert result == i ** 2
        
        # Test futures backend
        processor_futures = ParallelProcessor(n_jobs=2, backend="futures")
        
        # Process with futures
        results_futures = processor_futures.process_parallel(items, process_fn)
        
        # Verify results
        assert len(results_futures) == 5
        for i, result in enumerate(results_futures):
            assert result == i ** 2
    
    def test_chunk_sizing(self):
        """Test different chunk sizes."""
        processor = ParallelProcessor(n_jobs=2)
        
        # Create sample data
        items = list(range(10))
        
        # Define processing function that returns chunk info
        def process_fn(chunk):
            return [(len(chunk), x) for x in chunk]
        
        # Process with default chunk size
        results = processor.process_parallel(items, process_fn)
        
        # Should be split into approximately equal chunks
        for chunk_size, x in results:
            assert chunk_size <= 10  # No chunk bigger than input
        
        # Process with explicit chunk size
        processor.chunk_size = 2
        results = processor.process_parallel(items, process_fn)
        
        # All chunks should be of size 2 (except possibly the last)
        for chunk_size, x in results:
            assert chunk_size <= 2