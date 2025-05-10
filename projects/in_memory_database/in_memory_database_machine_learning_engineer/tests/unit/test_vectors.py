"""
Unit tests for vector operations.
"""

import math
import random
import unittest
from typing import List, Tuple

import numpy as np
import pytest
from pytest import approx

from feature_store.vectors.base import Distance, VectorBase
from feature_store.vectors.dense import DenseVector
from feature_store.vectors.index import IndexType, VectorIndex
from feature_store.vectors.sparse import SparseVector


class TestDenseVector:
    """Tests for DenseVector class."""

    def test_creation(self):
        """Test vector creation from different input types."""
        # Create from list
        v1 = DenseVector([1.0, 2.0, 3.0])
        assert v1.dimensionality == 3
        assert np.array_equal(v1.to_array(), np.array([1.0, 2.0, 3.0], dtype=np.float32))
        
        # Create from numpy array
        v2 = DenseVector(np.array([4.0, 5.0, 6.0]))
        assert v2.dimensionality == 3
        assert np.array_equal(v2.to_array(), np.array([4.0, 5.0, 6.0], dtype=np.float32))
        
        # Check dimensionality
        assert len(v1) == 3
        assert len(v2) == 3
    
    def test_getitem(self):
        """Test indexing and slicing."""
        v = DenseVector([1.0, 2.0, 3.0, 4.0, 5.0])
        
        # Index access
        assert v[0] == 1.0
        assert v[2] == 3.0
        assert v[4] == 5.0
        
        # Slice access
        sliced = v[1:4]
        assert isinstance(sliced, DenseVector)
        assert np.array_equal(sliced.to_array(), np.array([2.0, 3.0, 4.0], dtype=np.float32))
    
    def test_arithmetic(self):
        """Test vector arithmetic operations."""
        v1 = DenseVector([1.0, 2.0, 3.0])
        v2 = DenseVector([4.0, 5.0, 6.0])
        
        # Addition
        v_sum = v1 + v2
        assert np.array_equal(v_sum.to_array(), np.array([5.0, 7.0, 9.0], dtype=np.float32))
        
        # Subtraction
        v_diff = v2 - v1
        assert np.array_equal(v_diff.to_array(), np.array([3.0, 3.0, 3.0], dtype=np.float32))
        
        # Scalar multiplication
        v_mul = v1 * 2.0
        assert np.array_equal(v_mul.to_array(), np.array([2.0, 4.0, 6.0], dtype=np.float32))
        
        # Right scalar multiplication
        v_rmul = 3.0 * v1
        assert np.array_equal(v_rmul.to_array(), np.array([3.0, 6.0, 9.0], dtype=np.float32))
        
        # Division
        v_div = v2 / 2.0
        assert np.array_equal(v_div.to_array(), np.array([2.0, 2.5, 3.0], dtype=np.float32))
    
    def test_dot_product(self):
        """Test dot product."""
        v1 = DenseVector([1.0, 2.0, 3.0])
        v2 = DenseVector([4.0, 5.0, 6.0])
        
        # Dot product
        assert v1.dot(v2) == 32.0
    
    def test_norms(self):
        """Test vector norms."""
        v = DenseVector([3.0, 4.0])
        
        # L1 norm
        assert v.norm(1) == 7.0
        
        # L2 norm
        assert v.norm(2) == 5.0
        
        # L3 norm
        assert v.norm(3) == approx((3**3 + 4**3)**(1/3))
    
    def test_distances(self):
        """Test distance calculations."""
        v1 = DenseVector([1.0, 0.0])
        v2 = DenseVector([0.0, 1.0])
        
        # Euclidean distance
        assert v1.distance(v2, Distance.EUCLIDEAN) == approx(math.sqrt(2))
        
        # Manhattan distance
        assert v1.distance(v2, Distance.MANHATTAN) == 2.0
        
        # Cosine distance
        assert v1.distance(v2, Distance.COSINE) == approx(1.0)
        
        # Dot product distance
        assert v1.distance(v2, Distance.DOT_PRODUCT) == approx(0.0)
    
    def test_equality(self):
        """Test vector equality."""
        v1 = DenseVector([1.0, 2.0, 3.0])
        v2 = DenseVector([1.0, 2.0, 3.0])
        v3 = DenseVector([1.0, 2.0, 3.1])
        
        # Equal vectors
        assert v1 == v2
        
        # Unequal vectors
        assert v1 != v3


class TestSparseVector:
    """Tests for SparseVector class."""

    def test_creation(self):
        """Test vector creation from different input types."""
        # Create from indices and values
        indices = [0, 2, 4]
        values = [1.0, 3.0, 5.0]
        v1 = SparseVector(indices=indices, values=values, dimensionality=5)
        assert v1.dimensionality == 5
        assert np.array_equal(v1.indices, np.array(indices, dtype=np.int32))
        assert np.array_equal(v1.values, np.array(values, dtype=np.float32))
        
        # Create from dictionary
        data = {0: 1.0, 2: 3.0, 4: 5.0}
        v2 = SparseVector.from_dict(data, dimensionality=5)
        assert v2.dimensionality == 5
        assert np.array_equal(v2.indices, np.array(indices, dtype=np.int32))
        assert np.array_equal(v2.values, np.array(values, dtype=np.float32))
        
        # Check dimensionality
        assert len(v1) == 5
        assert len(v2) == 5
    
    def test_conversion(self):
        """Test conversion to array and dictionary."""
        indices = [0, 2, 4]
        values = [1.0, 3.0, 5.0]
        v = SparseVector(indices=indices, values=values, dimensionality=5)
        
        # To array
        expected_array = np.array([1.0, 0.0, 3.0, 0.0, 5.0], dtype=np.float32)
        assert np.array_equal(v.to_array(), expected_array)
        
        # To dictionary
        expected_dict = {0: 1.0, 2: 3.0, 4: 5.0}
        assert v.to_dict() == expected_dict
    
    def test_getitem(self):
        """Test indexing and slicing."""
        indices = [0, 2, 4]
        values = [1.0, 3.0, 5.0]
        v = SparseVector(indices=indices, values=values, dimensionality=5)
        
        # Index access (present)
        assert v[0] == 1.0
        assert v[2] == 3.0
        assert v[4] == 5.0
        
        # Index access (absent)
        assert v[1] == 0.0
        assert v[3] == 0.0
        
        # Slice access
        sliced = v[1:4]
        assert isinstance(sliced, DenseVector)
        assert np.array_equal(sliced.to_array(), np.array([0.0, 3.0, 0.0], dtype=np.float32))
    
    def test_arithmetic(self):
        """Test vector arithmetic operations."""
        v1 = SparseVector(indices=[0, 2], values=[1.0, 3.0], dimensionality=3)
        v2 = SparseVector(indices=[1, 2], values=[2.0, 4.0], dimensionality=3)
        
        # Addition
        v_sum = v1 + v2
        assert isinstance(v_sum, SparseVector)
        assert np.array_equal(v_sum.to_array(), np.array([1.0, 2.0, 7.0], dtype=np.float32))
        
        # Subtraction
        v_diff = v1 - v2
        assert isinstance(v_diff, SparseVector)
        assert np.array_equal(v_diff.to_array(), np.array([1.0, -2.0, -1.0], dtype=np.float32))
        
        # Scalar multiplication
        v_mul = v1 * 2.0
        assert isinstance(v_mul, SparseVector)
        assert np.array_equal(v_mul.to_array(), np.array([2.0, 0.0, 6.0], dtype=np.float32))
        
        # Division
        v_div = v1 / 2.0
        assert isinstance(v_div, SparseVector)
        assert np.array_equal(v_div.to_array(), np.array([0.5, 0.0, 1.5], dtype=np.float32))
    
    def test_sparse_specific_operations(self):
        """Test sparse-specific operations."""
        v = SparseVector(indices=[0, 2, 4], values=[1.0, 3.0, 5.0], dimensionality=5)
        
        # Number of non-zero elements
        assert v.nnz == 3
        
        # Density
        assert v.density == 60.0  # 3/5 = 60%
    
    def test_sparse_distance_optimizations(self):
        """Test optimized sparse distance calculations."""
        # Create two sparse vectors with no overlap
        v1 = SparseVector(indices=[0, 2], values=[1.0, 3.0], dimensionality=5)
        v2 = SparseVector(indices=[1, 3], values=[2.0, 4.0], dimensionality=5)
        
        # Dot product should be 0 (no overlapping indices)
        assert v1.dot(v2) == 0.0
        
        # Create two sparse vectors with overlap
        v3 = SparseVector(indices=[0, 2], values=[1.0, 3.0], dimensionality=5)
        v4 = SparseVector(indices=[0, 3], values=[2.0, 4.0], dimensionality=5)
        
        # Dot product should be 2.0 (only index 0 overlaps: 1.0 * 2.0)
        assert v3.dot(v4) == 2.0
        
        # Test optimized distance calculations
        # Euclidean distance: sqrt((1-2)^2 + 3^2 + 4^2) = sqrt(1 + 9 + 16) = sqrt(26)
        assert v3.distance(v4, Distance.EUCLIDEAN) == approx(math.sqrt(26))
        
        # Manhattan distance: |1-2| + |3-0| + |0-4| = 1 + 3 + 4 = 8
        assert v3.distance(v4, Distance.MANHATTAN) == 8.0


class TestVectorIndex:
    """Tests for VectorIndex class."""

    def test_creation(self):
        """Test index creation."""
        # Create index with different types
        index_flat = VectorIndex(dimensionality=3, index_type=IndexType.FLAT)
        assert index_flat.dimensionality == 3
        assert index_flat.index_type == IndexType.FLAT
        
        index_hnsw = VectorIndex(dimensionality=3, index_type=IndexType.HNSW)
        assert index_hnsw.dimensionality == 3
        assert index_hnsw.index_type == IndexType.HNSW
    
    def test_add_and_get(self):
        """Test adding and retrieving vectors."""
        index = VectorIndex(dimensionality=3)
        
        # Add vectors
        v1 = DenseVector([1.0, 2.0, 3.0])
        v2 = DenseVector([4.0, 5.0, 6.0])
        
        index.add("key1", v1)
        index.add("key2", v2)
        
        # Verify index size
        assert len(index) == 2
        
        # Retrieve vectors
        retrieved_v1 = index.get("key1")
        retrieved_v2 = index.get("key2")
        
        assert retrieved_v1 == v1
        assert retrieved_v2 == v2
        
        # Check contains
        assert "key1" in index
        assert "key3" not in index
        
        # Check keys
        assert set(index.keys()) == {"key1", "key2"}
    
    def test_search(self):
        """Test similarity search."""
        index = VectorIndex(dimensionality=2)
        
        # Add vectors forming a grid
        for i in range(5):
            for j in range(5):
                key = f"vec_{i}_{j}"
                vec = DenseVector([float(i), float(j)])
                index.add(key, vec)
        
        # Search with Euclidean distance
        query = DenseVector([2.0, 2.0])
        results = index.search(query, k=5, metric=Distance.EUCLIDEAN)
        
        # The closest vectors should be:
        # vec_2_2 (distance 0)
        # vec_1_2, vec_2_1, vec_3_2, vec_2_3 (distance 1)
        assert len(results) == 5
        assert results[0][0] == "vec_2_2"
        assert results[0][1] == approx(0.0)
        
        for key, dist in results[1:]:
            # Check that all remaining vectors are distance 1 away
            assert dist == approx(1.0)
    
    def test_remove(self):
        """Test removing vectors."""
        index = VectorIndex(dimensionality=3)
        
        # Add vectors
        v1 = DenseVector([1.0, 2.0, 3.0])
        v2 = DenseVector([4.0, 5.0, 6.0])
        v3 = DenseVector([7.0, 8.0, 9.0])
        
        index.add("key1", v1)
        index.add("key2", v2)
        index.add("key3", v3)
        
        assert len(index) == 3
        
        # Remove a vector
        index.remove("key2")
        
        assert len(index) == 2
        assert "key2" not in index
        assert index.get("key2") is None
        
        # Search should not return the removed vector
        results = index.search(v2, k=3)
        assert len(results) == 2
        assert all(key != "key2" for key, _ in results)
    
    def test_different_metrics(self):
        """Test search with different distance metrics."""
        index = VectorIndex(dimensionality=2)
        
        # Add unit vectors in different directions
        index.add("right", DenseVector([1.0, 0.0]))
        index.add("up", DenseVector([0.0, 1.0]))
        index.add("left", DenseVector([-1.0, 0.0]))
        index.add("down", DenseVector([0.0, -1.0]))
        
        # Query with different metrics
        query = DenseVector([1.0, 0.0])  # Same as "right"
        
        # Euclidean distance
        euclidean_results = index.search(query, k=4, metric=Distance.EUCLIDEAN)
        assert euclidean_results[0][0] == "right"
        assert euclidean_results[0][1] == approx(0.0)
        assert euclidean_results[1][1] == approx(math.sqrt(2))  # Distance to up/down
        assert euclidean_results[3][0] == "left"
        assert euclidean_results[3][1] == approx(2.0)  # Distance to left
        
        # Cosine distance
        cosine_results = index.search(query, k=4, metric=Distance.COSINE)
        assert cosine_results[0][0] == "right"
        assert cosine_results[0][1] == approx(0.0)
        assert cosine_results[3][0] == "left"
        assert cosine_results[3][1] == approx(2.0)  # Cosine distance to opposite direction
        
        # Manhattan distance
        manhattan_results = index.search(query, k=4, metric=Distance.MANHATTAN)
        assert manhattan_results[0][0] == "right"
        assert manhattan_results[0][1] == approx(0.0)
        assert manhattan_results[1][1] == approx(2.0)  # Manhattan distance to up/down
        assert manhattan_results[3][0] == "left"
        assert manhattan_results[3][1] == approx(4.0)  # Manhattan distance to left


@pytest.mark.benchmark
class TestVectorPerformance:
    """Performance tests for vector operations."""

    def create_random_dense_vector(self, dims: int) -> DenseVector:
        """Create a random dense vector."""
        return DenseVector(np.random.randn(dims).astype(np.float32))
    
    def create_random_sparse_vector(
        self, 
        dims: int, 
        density: float = 0.1
    ) -> SparseVector:
        """Create a random sparse vector with given density."""
        # Decide which indices will be non-zero
        nnz = int(dims * density)
        indices = sorted(random.sample(range(dims), nnz))
        values = np.random.randn(nnz).astype(np.float32)
        return SparseVector(indices=indices, values=values, dimensionality=dims)
    
    def test_vector_creation_performance(self, benchmark):
        """Benchmark vector creation."""
        # Benchmark creating 1000 dense vectors
        dims = 100
        
        def create_vectors():
            return [self.create_random_dense_vector(dims) for _ in range(1000)]
        
        vectors = benchmark(create_vectors)
        assert len(vectors) == 1000
    
    def test_distance_calculation_performance(self, benchmark):
        """Benchmark distance calculations."""
        # Create vectors
        dims = 1000
        v1 = self.create_random_dense_vector(dims)
        v2 = self.create_random_dense_vector(dims)
        
        # Benchmark Euclidean distance
        def calc_distance():
            return v1.distance(v2, Distance.EUCLIDEAN)
        
        distance = benchmark(calc_distance)
        assert isinstance(distance, float)
    
    def test_sparse_vs_dense_performance(self, benchmark):
        """Compare sparse vs dense performance for sparse data."""
        # Create sparse data
        dims = 10000
        density = 0.01  # 1% non-zero
        
        # Create sparse vector
        sparse_vec1 = self.create_random_sparse_vector(dims, density)
        sparse_vec2 = self.create_random_sparse_vector(dims, density)
        
        # Equivalent dense vectors
        dense_vec1 = DenseVector(sparse_vec1.to_array())
        dense_vec2 = DenseVector(sparse_vec2.to_array())
        
        # Benchmark sparse dot product
        def sparse_dot():
            return sparse_vec1.dot(sparse_vec2)
        
        # Benchmark dense dot product
        def dense_dot():
            return dense_vec1.dot(dense_vec2)
        
        # Run benchmarks
        sparse_result = benchmark(sparse_dot)
        dense_result = benchmark(dense_dot)
        
        # Results should be approximately equal
        assert sparse_result == approx(dense_result)
    
    def test_index_search_performance(self, benchmark):
        """Benchmark vector index search performance."""
        # Create index with random vectors
        dims = 128
        num_vectors = 10000
        
        index = VectorIndex(dimensionality=dims, index_type=IndexType.HNSW)
        
        # Add vectors
        for i in range(num_vectors):
            key = f"vec_{i}"
            vec = self.create_random_dense_vector(dims)
            index.add(key, vec)
        
        # Create query vector
        query = self.create_random_dense_vector(dims)
        
        # Benchmark search
        def search():
            return index.search(query, k=10)
        
        results = benchmark(search)
        assert len(results) == 10