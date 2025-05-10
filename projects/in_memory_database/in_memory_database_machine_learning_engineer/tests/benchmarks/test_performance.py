"""
Performance benchmarks for the feature store.
"""

import time
from typing import Dict, List, Optional, Set, Tuple

import numpy as np
import pytest
from pytest import approx

from feature_store.batching.parallel import ParallelProcessor
from feature_store.core import FeatureStore
from feature_store.transformations.pipeline import TransformationPipeline
from feature_store.transformations.scaling import StandardScaler, MinMaxScaler
from feature_store.vectors.base import Distance
from feature_store.vectors.dense import DenseVector
from feature_store.vectors.index import IndexType
from feature_store.vectors.sparse import SparseVector


class TestVectorIndexPerformance:
    """Performance benchmarks for vector index operations."""
    
    @pytest.mark.parametrize("index_type", [
        IndexType.FLAT,
        IndexType.HNSW,
        IndexType.IVF,
    ])
    @pytest.mark.parametrize("dims", [32, 128, 512])
    @pytest.mark.parametrize("num_vectors", [1000, 10000])
    def test_index_query_performance(self, benchmark, index_type, dims, num_vectors):
        """Benchmark query performance for different index types and dimensions."""
        # Skip larger combinations to keep tests reasonably fast
        if num_vectors == 10000 and dims == 512:
            pytest.skip("Skipping large dimension + large vector count combination")
        
        # Create feature store with specified index type
        store = FeatureStore(default_index_type=index_type)
        
        # Create vector group
        store.create_group(
            "benchmark_vectors",
            dimensions=dims,
            index_type=index_type
        )
        
        # Add random vectors
        for i in range(num_vectors):
            key = f"vec_{i}"
            vector = DenseVector(np.random.randn(dims).astype(np.float32))
            store.add(key, vector, group="benchmark_vectors")
        
        # Create query vector
        query_vector = DenseVector(np.random.randn(dims).astype(np.float32))
        
        # Benchmark query
        def query_func():
            return store.query_similar(
                query_vector, 
                k=10, 
                group="benchmark_vectors"
            )
        
        # Run benchmark
        results = benchmark(query_func)
        
        # Verify results
        assert len(results) == 10


class TestBatchOperationsPerformance:
    """Performance benchmarks for batch operations."""
    
    @pytest.mark.parametrize("batch_size", [10, 100, 1000])
    def test_batch_retrieval_scaling(self, benchmark, batch_size):
        """Benchmark batch retrieval performance scaling."""
        # Create feature store
        store = FeatureStore()
        
        # Add vectors
        for i in range(max(batch_size, 1000)):  # Ensure we have enough vectors
            key = f"batch_test_{i}"
            vector = DenseVector(np.random.randn(32).astype(np.float32))
            store.add(key, vector)
        
        # Create test keys
        keys = [f"batch_test_{i}" for i in range(batch_size)]
        
        # Benchmark batch retrieval
        def batch_func():
            return store.batch_get(keys)
        
        # Run benchmark
        results = benchmark(batch_func)
        
        # Verify results
        assert len(results) == batch_size
    
    @pytest.mark.parametrize("n_jobs", [1, 2, 4])
    def test_parallel_processing_scaling(self, benchmark, n_jobs):
        """Benchmark parallel processing performance scaling."""
        # Create processor
        processor = ParallelProcessor(n_jobs=n_jobs, backend="threading")
        
        # Create test data
        items = list(range(1000))
        
        # Define processing function (simulate some work)
        def process_fn(chunk):
            results = []
            for x in chunk:
                # Simulate some CPU-bound work
                result = 0
                for i in range(10000):
                    result += (x * i) % 10
                results.append(result)
            return results
        
        # Benchmark parallel processing
        def parallel_func():
            return processor.process_parallel(items, process_fn)
        
        # Run benchmark
        results = benchmark(parallel_func)
        
        # Verify results
        assert len(results) == 1000


class TestTransformationPerformance:
    """Performance benchmarks for transformations."""
    
    @pytest.mark.parametrize("num_transforms", [1, 2, 4])
    @pytest.mark.parametrize("dims", [10, 100])
    def test_transformation_pipeline_overhead(self, benchmark, num_transforms, dims):
        """Benchmark transformation pipeline overhead."""
        # Create vectors for fitting
        vectors = [DenseVector(np.random.randn(dims).astype(np.float32)) for _ in range(100)]
        
        # Create transformations
        transforms = []
        for i in range(num_transforms):
            if i % 2 == 0:
                transform = StandardScaler(name=f"scaler_{i}")
            else:
                transform = MinMaxScaler(name=f"normalizer_{i}")
            transform.fit(vectors)
            transforms.append(transform)
        
        # Create pipeline
        pipeline = TransformationPipeline(
            name="benchmark_pipeline",
            steps=transforms,
            cache_enabled=True
        )
        
        # Create test vector
        test_vector = DenseVector(np.random.randn(dims).astype(np.float32))
        
        # Benchmark transformation
        def transform_func():
            return pipeline.transform(test_vector)
        
        # Run benchmark
        result = benchmark(transform_func)
        
        # Verify result
        assert result is not None
        assert len(result) == dims
    
    def test_cache_effectiveness(self, benchmark):
        """Benchmark the effectiveness of transformation caching."""
        # Create vectors for fitting
        dims = 100
        vectors = [DenseVector(np.random.randn(dims).astype(np.float32)) for _ in range(100)]
        
        # Create transformations
        scaler = StandardScaler(name="scaler")
        normalizer = MinMaxScaler(name="normalizer")
        scaler.fit(vectors)
        normalizer.fit(vectors)
        
        # Create pipeline with caching enabled
        pipeline = TransformationPipeline(
            name="cache_pipeline",
            steps=[scaler, normalizer],
            cache_enabled=True
        )
        
        # Create test vector
        test_vector = DenseVector(np.random.randn(dims).astype(np.float32))
        
        # First transformation (no cache)
        pipeline.transform(test_vector)
        
        # Clear the pipeline's cache to measure uncached performance
        pipeline.clear_cache()
        
        # Benchmark transformation without cache
        def transform_no_cache():
            pipeline.clear_cache()
            return pipeline.transform(test_vector)
        
        result_no_cache = benchmark(transform_no_cache)
        
        # Now benchmark with cache
        def transform_with_cache():
            return pipeline.transform(test_vector)
        
        # This should reuse the cached result
        benchmark.extra_info["cached"] = True  # Mark this run for comparison
        result_with_cache = benchmark(transform_with_cache)
        
        # Both should return the same result
        assert np.array_equal(result_no_cache.to_array(), result_with_cache.to_array())


class TestFeatureStoreScaling:
    """Performance benchmarks for feature store scaling."""
    
    @pytest.mark.parametrize("num_vectors", [1000, 10000])
    @pytest.mark.parametrize("num_versions", [1, 5, 10])
    def test_versioning_overhead(self, benchmark, num_vectors, num_versions):
        """Benchmark versioning overhead with increasing versions."""
        # Create feature store
        store = FeatureStore()
        
        # Add vectors with versions
        for i in range(num_vectors):
            key = f"version_test_{i}"
            
            for v in range(num_versions):
                # Create slightly different vector for each version
                vector = DenseVector(
                    (np.random.randn(10) + v * 0.1).astype(np.float32)
                )
                
                # Add with version tag
                store.add(
                    key, 
                    vector, 
                    tag=f"v{v+1}",
                    timestamp=float(time.time() + v * 10)  # Ensure increasing timestamps
                )
        
        # Pick a random key for testing
        test_key = f"version_test_{np.random.randint(0, num_vectors)}"
        
        # Benchmark latest version retrieval
        def get_latest():
            return store.get(test_key)
        
        # Run benchmark for latest version
        latest_result = benchmark(get_latest)
        assert latest_result is not None
        
        # Benchmark specific version retrieval
        version = f"v{np.random.randint(1, num_versions+1)}"
        
        def get_version():
            return store.get(test_key, version=version)
        
        # Run benchmark for specific version
        version_result = benchmark(get_version)
        assert version_result is not None
    
    def test_experiment_assignment_scaling(self, benchmark):
        """Benchmark experiment assignment performance scaling."""
        # Create feature store
        store = FeatureStore()
        
        # Create experiment with many groups
        groups = [f"group_{i}" for i in range(20)]
        weights = [1.0/20] * 20
        
        experiment = store.create_experiment(
            name="scaling_test",
            groups=groups,
            weights=weights
        )
        
        # Generate random user IDs
        user_ids = [f"user_{i}" for i in range(1000)]
        
        # Benchmark group assignment
        def assign_groups():
            results = {}
            for user_id in user_ids:
                results[user_id] = store.get_experiment_group(user_id, "scaling_test")
            return results
        
        # Run benchmark
        results = benchmark(assign_groups)
        
        # Verify results
        assert len(results) == 1000
        for user_id, group in results.items():
            assert group in groups


class TestVectorOperationsPerformance:
    """Performance benchmarks for vector operations."""
    
    @pytest.mark.parametrize("dims", [100, 1000, 10000])
    @pytest.mark.parametrize("density", [0.01, 0.1, 1.0])
    def test_sparse_vs_dense_performance(self, benchmark, dims, density):
        """Benchmark sparse vs dense vector performance."""
        if dims == 10000 and density > 0.01:
            pytest.skip("Skipping high-dimensional dense vector tests")
        
        # Create dense vector
        dense_data = np.random.randn(dims).astype(np.float32)
        if density < 1.0:
            # Set some elements to zero for fair comparison
            zero_indices = np.random.choice(
                dims, 
                size=int(dims * (1 - density)), 
                replace=False
            )
            dense_data[zero_indices] = 0
        
        dense_vector = DenseVector(dense_data)
        
        # Create equivalent sparse vector
        nonzero_indices = np.nonzero(dense_data)[0]
        nonzero_values = dense_data[nonzero_indices]
        
        sparse_vector = SparseVector(
            indices=nonzero_indices.astype(np.int32),
            values=nonzero_values,
            dimensionality=dims
        )
        
        # Create second vector for distance calculations
        dense_data2 = np.random.randn(dims).astype(np.float32)
        if density < 1.0:
            # Set some elements to zero for fair comparison
            zero_indices = np.random.choice(
                dims, 
                size=int(dims * (1 - density)), 
                replace=False
            )
            dense_data2[zero_indices] = 0
        
        dense_vector2 = DenseVector(dense_data2)
        
        nonzero_indices2 = np.nonzero(dense_data2)[0]
        nonzero_values2 = dense_data2[nonzero_indices2]
        
        sparse_vector2 = SparseVector(
            indices=nonzero_indices2.astype(np.int32),
            values=nonzero_values2,
            dimensionality=dims
        )
        
        # Benchmark dense vector dot product
        def dense_dot():
            return dense_vector.dot(dense_vector2)
        
        dense_result = benchmark(dense_dot)
        
        # Benchmark sparse vector dot product
        def sparse_dot():
            return sparse_vector.dot(sparse_vector2)
        
        benchmark.extra_info["sparse"] = True
        sparse_result = benchmark(sparse_dot)
        
        # Results should be approximately equal
        assert dense_result == approx(sparse_result)
    
    @pytest.mark.parametrize("metric", [
        Distance.EUCLIDEAN,
        Distance.COSINE,
        Distance.MANHATTAN,
        Distance.DOT_PRODUCT
    ])
    def test_distance_metric_performance(self, benchmark, metric):
        """Benchmark performance of different distance metrics."""
        # Create vectors
        dims = 1000
        v1 = DenseVector(np.random.randn(dims).astype(np.float32))
        v2 = DenseVector(np.random.randn(dims).astype(np.float32))
        
        # Benchmark distance calculation
        def calc_distance():
            return v1.distance(v2, metric)
        
        result = benchmark(calc_distance)
        
        # Just verify we got a result
        assert isinstance(result, float)