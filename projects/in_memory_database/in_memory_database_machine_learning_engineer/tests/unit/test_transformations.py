"""
Unit tests for transformation operations.
"""

import time
from typing import List, Optional

import numpy as np
import pytest
from pytest import approx

from feature_store.transformations.base import Transformation
from feature_store.transformations.encoding import LabelEncoder, OneHotEncoder
from feature_store.transformations.pipeline import TransformationPipeline
from feature_store.transformations.scaling import MinMaxScaler, StandardScaler
from feature_store.vectors.dense import DenseVector
from feature_store.vectors.sparse import SparseVector


class TestStandardScaler:
    """Tests for StandardScaler transformation."""

    def test_fit_transform(self):
        """Test fitting and transforming with StandardScaler."""
        # Create sample data
        vectors = [
            DenseVector([0.0, 0.0, 0.0]),
            DenseVector([1.0, 2.0, 3.0]),
            DenseVector([4.0, 5.0, 6.0]),
            DenseVector([7.0, 8.0, 9.0])
        ]
        
        # Calculate expected mean and std
        data = np.vstack([v.to_array() for v in vectors])
        expected_mean = np.mean(data, axis=0)
        expected_std = np.std(data, axis=0, ddof=1)
        
        # Fit scaler
        scaler = StandardScaler(name="standard_scaler")
        scaler.fit(vectors)
        
        # Verify fitted parameters
        assert scaler.is_fitted
        assert np.allclose(scaler.mean_, expected_mean)
        assert np.allclose(scaler.scale_, expected_std)
        
        # Transform a vector
        vector = DenseVector([3.0, 4.0, 5.0])
        transformed = scaler.transform(vector)
        
        # Calculate expected transformed values
        expected = (np.array([3.0, 4.0, 5.0]) - expected_mean) / expected_std
        expected_vector = DenseVector(expected)
        
        # Verify transformation
        assert isinstance(transformed, DenseVector)
        assert transformed == expected_vector
        
        # Inverse transform
        inverse = scaler.inverse_transform(transformed)
        
        # Verify inverse transformation
        assert isinstance(inverse, DenseVector)
        assert np.allclose(inverse.to_array(), vector.to_array())
    
    def test_transform_many(self):
        """Test transforming multiple vectors at once."""
        # Create sample data
        vectors = [
            DenseVector([0.0, 0.0, 0.0]),
            DenseVector([1.0, 2.0, 3.0]),
            DenseVector([4.0, 5.0, 6.0]),
            DenseVector([7.0, 8.0, 9.0])
        ]
        
        # Fit scaler
        scaler = StandardScaler(name="standard_scaler")
        scaler.fit(vectors)
        
        # Transform all vectors
        transformed = scaler.transform_many(vectors)
        
        # Verify results
        assert len(transformed) == len(vectors)
        
        # Calculate expected transformed values
        data = np.vstack([v.to_array() for v in vectors])
        expected_transformed = (data - scaler.mean_) / scaler.scale_
        
        # Verify each vector
        for i, trans_vec in enumerate(transformed):
            assert isinstance(trans_vec, DenseVector)
            assert np.allclose(trans_vec.to_array(), expected_transformed[i])
    
    def test_with_sparse_vectors(self):
        """Test with sparse vectors."""
        # Create sample data (mix of dense and sparse)
        dense_vectors = [
            DenseVector([0.0, 0.0, 0.0]),
            DenseVector([3.0, 0.0, 6.0]),
            DenseVector([0.0, 5.0, 0.0])
        ]
        
        sparse_vectors = [
            SparseVector(
                indices=np.array([0, 2], dtype=np.int32), 
                values=np.array([3.0, 6.0], dtype=np.float32), 
                dimensionality=3
            ),
            SparseVector(
                indices=np.array([1], dtype=np.int32), 
                values=np.array([5.0], dtype=np.float32), 
                dimensionality=3
            )
        ]
        
        # Fit on dense vectors
        scaler = StandardScaler(name="standard_scaler")
        scaler.fit(dense_vectors)
        
        # Transform sparse vector
        transformed = scaler.transform(sparse_vectors[0])
        
        # Should return sparse vector
        assert isinstance(transformed, SparseVector)
        
        # Calculate expected transformed values manually
        sparse_array = sparse_vectors[0].to_array()
        expected = (sparse_array - scaler.mean_) / scaler.scale_
        
        assert np.allclose(transformed.to_array(), expected)


class TestMinMaxScaler:
    """Tests for MinMaxScaler transformation."""

    def test_fit_transform(self):
        """Test fitting and transforming with MinMaxScaler."""
        # Create sample data
        vectors = [
            DenseVector([0.0, 0.0, 0.0]),
            DenseVector([1.0, 2.0, 3.0]),
            DenseVector([4.0, 5.0, 6.0]),
            DenseVector([7.0, 8.0, 9.0])
        ]
        
        # Calculate expected min and max
        data = np.vstack([v.to_array() for v in vectors])
        expected_min = np.min(data, axis=0)
        expected_max = np.max(data, axis=0)
        
        # Fit scaler
        scaler = MinMaxScaler(name="minmax_scaler", feature_range=(0, 1))
        scaler.fit(vectors)
        
        # Verify fitted parameters
        assert scaler.is_fitted
        assert np.allclose(scaler.min_, expected_min)
        assert np.allclose(scaler.max_, expected_max)
        
        # Transform a vector
        vector = DenseVector([3.0, 4.0, 5.0])
        transformed = scaler.transform(vector)
        
        # Calculate expected transformed values
        data_range = expected_max - expected_min
        expected = (np.array([3.0, 4.0, 5.0]) - expected_min) / data_range
        expected_vector = DenseVector(expected)
        
        # Verify transformation
        assert isinstance(transformed, DenseVector)
        assert np.allclose(transformed.to_array(), expected_vector.to_array())
        
        # Test with different feature range
        scaler = MinMaxScaler(name="minmax_scaler", feature_range=(-1, 1))
        scaler.fit(vectors)
        
        transformed = scaler.transform(vector)
        
        # Calculate expected values for feature range (-1, 1)
        data_range = expected_max - expected_min
        expected = 2 * (np.array([3.0, 4.0, 5.0]) - expected_min) / data_range - 1
        expected_vector = DenseVector(expected)
        
        assert np.allclose(transformed.to_array(), expected_vector.to_array())
    
    def test_inverse_transform(self):
        """Test inverse transformation."""
        # Create sample data
        vectors = [
            DenseVector([1.0, 2.0, 3.0]),
            DenseVector([4.0, 5.0, 6.0]),
            DenseVector([7.0, 8.0, 9.0])
        ]
        
        # Fit scaler
        scaler = MinMaxScaler(name="minmax_scaler", feature_range=(0, 1))
        scaler.fit(vectors)
        
        # Transform vector
        vector = DenseVector([3.0, 4.0, 5.0])
        transformed = scaler.transform(vector)
        
        # Inverse transform
        inverse = scaler.inverse_transform(transformed)
        
        # Verify inverse transformation
        assert isinstance(inverse, DenseVector)
        assert np.allclose(inverse.to_array(), vector.to_array())


class TestOneHotEncoder:
    """Tests for OneHotEncoder transformation."""

    def test_fit_transform(self):
        """Test fitting and transforming with OneHotEncoder."""
        # Create sample data (integer categories)
        vectors = [
            DenseVector([0, 1, 2]),  # First feature: category 0, second: category 1, etc.
            DenseVector([1, 0, 1]),
            DenseVector([2, 2, 0])
        ]
        
        # Fit encoder
        encoder = OneHotEncoder(name="onehot_encoder", sparse=True)
        encoder.fit(vectors)
        
        # Verify fitted parameters
        assert encoder.is_fitted
        assert encoder.n_features_ == 3
        
        # Each feature has 3 categories (0, 1, 2)
        assert encoder.categories_ == [[0, 1, 2], [0, 1, 2], [0, 1, 2]]
        
        # Verify feature indices (0-2 for first feature, 3-5 for second, 6-8 for third)
        assert np.array_equal(encoder.feature_indices_, np.array([0, 3, 6, 9]))
        
        # Transform a vector
        vector = DenseVector([1, 0, 2])
        transformed = encoder.transform(vector)
        
        # Should be a sparse vector since sparse=True
        assert isinstance(transformed, SparseVector)
        
        # Expected indices: second category of first feature (1),
        # first category of second feature (3),
        # third category of third feature (8)
        expected_indices = np.array([1, 3, 8], dtype=np.int32)
        expected_values = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        
        assert np.array_equal(transformed.indices, expected_indices)
        assert np.array_equal(transformed.values, expected_values)
        
        # Expected one-hot encoding:
        # First feature: [0, 1, 0] (category 1)
        # Second feature: [1, 0, 0] (category 0)
        # Third feature: [0, 0, 1] (category 2)
        # Total: [0, 1, 0, 1, 0, 0, 0, 0, 1]
        expected_array = np.zeros(9, dtype=np.float32)
        expected_array[np.array([1, 3, 8])] = 1.0
        
        assert np.array_equal(transformed.to_array(), expected_array)
    
    def test_dense_output(self):
        """Test with dense output."""
        # Create sample data
        vectors = [
            DenseVector([0, 1]),
            DenseVector([1, 0])
        ]
        
        # Fit encoder with dense output
        encoder = OneHotEncoder(name="onehot_encoder", sparse=False)
        encoder.fit(vectors)
        
        # Transform
        vector = DenseVector([0, 0])
        transformed = encoder.transform(vector)
        
        # Should be a dense vector
        assert isinstance(transformed, DenseVector)
        
        # Expected encoding:
        # First feature: [1, 0] (category 0)
        # Second feature: [1, 0] (category 0)
        # Total: [1, 0, 1, 0]
        expected = np.array([1, 0, 1, 0], dtype=np.float32)
        
        assert np.array_equal(transformed.to_array(), expected)
    
    def test_inverse_transform(self):
        """Test inverse transformation."""
        # Create sample data
        vectors = [
            DenseVector([0, 1]),
            DenseVector([1, 0])
        ]
        
        # Fit encoder
        encoder = OneHotEncoder(name="onehot_encoder", sparse=True)
        encoder.fit(vectors)
        
        # Transform vector
        vector = DenseVector([0, 0])
        transformed = encoder.transform(vector)
        
        # Inverse transform
        inverse = encoder.inverse_transform(transformed)
        
        # Verify inverse transformation
        assert isinstance(inverse, DenseVector)
        assert np.array_equal(inverse.to_array(), vector.to_array())


class TestTransformationPipeline:
    """Tests for TransformationPipeline."""

    def test_pipeline_creation(self):
        """Test creating a transformation pipeline."""
        # Create transformations
        scaler = StandardScaler(name="standard_scaler")
        encoder = OneHotEncoder(name="onehot_encoder", sparse=False)
        
        # Create pipeline
        pipeline = TransformationPipeline(
            name="pipeline",
            steps=[scaler, encoder]
        )
        
        # Verify pipeline
        assert len(pipeline.steps) == 2
        assert pipeline.steps[0] == scaler
        assert pipeline.steps[1] == encoder
        assert not pipeline.is_fitted
    
    def test_fit_transform(self):
        """Test fitting and transforming with a pipeline."""
        # Create sample data
        vectors = [
            DenseVector([0.0, 0.0]),
            DenseVector([3.0, 4.0]),
            DenseVector([6.0, 8.0])
        ]
        
        # Create transformations
        scaler = StandardScaler(name="standard_scaler")
        encoder = MinMaxScaler(name="minmax_scaler")
        
        # Create pipeline
        pipeline = TransformationPipeline(
            name="pipeline",
            steps=[scaler, encoder]
        )
        
        # Fit pipeline
        pipeline.fit(vectors)
        
        # Verify all steps are fitted
        assert pipeline.is_fitted
        assert scaler.is_fitted
        assert encoder.is_fitted
        
        # Transform a vector
        vector = DenseVector([3.0, 4.0])
        transformed = pipeline.transform(vector)
        
        # Verify transformation (should be equivalent to applying each step in sequence)
        expected = scaler.transform(vector)
        expected = encoder.transform(expected)
        
        assert isinstance(transformed, DenseVector)
        assert np.allclose(transformed.to_array(), expected.to_array())
        
        # Inverse transform
        inverse = pipeline.inverse_transform(transformed)
        
        # Verify inverse transformation
        assert isinstance(inverse, DenseVector)
        assert np.allclose(inverse.to_array(), vector.to_array())
    
    def test_state_serialization(self):
        """Test state serialization and deserialization."""
        # Create sample data
        vectors = [
            DenseVector([0.0, 0.0]),
            DenseVector([3.0, 4.0]),
            DenseVector([6.0, 8.0])
        ]
        
        # Create and fit transformations
        scaler = StandardScaler(name="standard_scaler")
        scaler.fit(vectors)
        
        # Get state dict
        state = scaler.get_state_dict()
        
        # Verify state contains expected keys
        assert "name" in state
        assert "version" in state
        assert "is_fitted" in state
        assert "mean_" in state
        assert "scale_" in state
        
        # Verify values
        assert state["name"] == "standard_scaler"
        assert state["is_fitted"] is True
        
        # Create a new scaler and set state
        new_scaler = StandardScaler(name="temp")
        new_scaler.set_state_dict(state)
        
        # Verify restored state
        assert new_scaler.name == "standard_scaler"
        assert new_scaler.is_fitted is True
        assert np.allclose(new_scaler.mean_, scaler.mean_)
        assert np.allclose(new_scaler.scale_, scaler.scale_)
        
        # Transform a vector with both scalers and verify results match
        vector = DenseVector([3.0, 4.0])
        result1 = scaler.transform(vector)
        result2 = new_scaler.transform(vector)
        
        assert np.allclose(result1.to_array(), result2.to_array())
    
    def test_pipeline_caching(self):
        """Test pipeline caching functionality."""
        # Create sample data
        vectors = [
            DenseVector([0.0, 0.0]),
            DenseVector([3.0, 4.0]),
            DenseVector([6.0, 8.0])
        ]
        
        # Create transformations
        scaler = StandardScaler(name="standard_scaler")
        normalizer = MinMaxScaler(name="minmax_scaler")
        
        # Create pipeline with caching enabled
        pipeline = TransformationPipeline(
            name="pipeline",
            steps=[scaler, normalizer],
            cache_enabled=True
        )
        
        # Fit pipeline
        pipeline.fit(vectors)
        
        # Transform a vector
        vector = DenseVector([3.0, 4.0])
        
        # First transformation should populate the cache
        result1 = pipeline.transform(vector)
        
        # Create a new copy of the vector with the same values
        same_vector = DenseVector([3.0, 4.0])
        
        # Second transformation should use the cache
        result2 = pipeline.transform(same_vector)
        
        # Results should be the same
        assert np.allclose(result1.to_array(), result2.to_array())
        
        # Disable cache
        pipeline.disable_cache()
        
        # Verify cache is empty
        assert not pipeline._cache
        
        # Enable cache again
        pipeline.enable_cache()
        
        # Transform again to populate cache
        result3 = pipeline.transform(vector)
        
        # Verify results are still correct
        assert np.allclose(result1.to_array(), result3.to_array())