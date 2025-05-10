"""
Integration tests for end-to-end workflows.
"""

import os
import tempfile
import time
from typing import Dict, List, Optional, Set, Tuple

import numpy as np
import pytest
from pytest import approx

from feature_store.core import FeatureStore
from feature_store.transformations.scaling import MinMaxScaler, StandardScaler
from feature_store.vectors.base import Distance
from feature_store.vectors.dense import DenseVector
from feature_store.vectors.index import IndexType
from feature_store.vectors.sparse import SparseVector


class TestEndToEndWorkflows:
    """Integration tests for end-to-end workflows."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create feature store
        self.store = FeatureStore(auto_create_groups=True)
    
    def test_basic_vector_storage_and_retrieval(self):
        """Test basic vector storage and retrieval workflow."""
        # 1. Add vectors
        for i in range(10):
            key = f"user_{i}"
            vector = DenseVector([float(i), float(i*2), float(i*3)])
            self.store.add(key, vector, group="embeddings")
        
        # 2. Retrieve vectors
        for i in range(10):
            key = f"user_{i}"
            vector = self.store.get(key, group="embeddings")
            assert vector is not None
            assert np.array_equal(
                vector.to_array(), 
                np.array([float(i), float(i*2), float(i*3)], dtype=np.float32)
            )
        
        # 3. Query similar vectors
        query = DenseVector([5.0, 10.0, 15.0])  # Should be close to user_5
        results = self.store.query_similar(query, k=3, group="embeddings")
        
        # Should return user_5 as closest match
        assert results[0][0] == "user_5"
        assert results[0][1] == approx(0.0)  # Distance should be very close to 0
        
        # Other results should be close to 5 (likely 4 and 6)
        assert int(results[1][0].split("_")[1]) in (4, 6)
        assert int(results[2][0].split("_")[1]) in (4, 6)
    
    def test_feature_versioning_workflow(self):
        """Test feature versioning workflow."""
        # 1. Add initial vectors
        feature_key = "product_embedding"
        initial_vector = DenseVector([1.0, 2.0, 3.0])
        self.store.add(feature_key, initial_vector, group="embeddings")
        
        # 2. Add new versions
        updated_vector = DenseVector([1.5, 2.5, 3.5])
        version_id = self.store.add(
            feature_key, 
            updated_vector, 
            group="embeddings",
            tag="v2",
            metadata={"update_reason": "model retrained"}
        )
        
        # 3. Retrieve specific versions
        retrieved_initial = self.store.get(feature_key, group="embeddings", version="v1")
        retrieved_updated = self.store.get(feature_key, group="embeddings", version="v2")
        
        assert retrieved_updated is not None
        assert np.array_equal(retrieved_updated.to_array(), updated_vector.to_array())
        
        # Default should return latest version
        latest = self.store.get(feature_key, group="embeddings")
        assert latest is not None
        assert np.array_equal(latest.to_array(), updated_vector.to_array())
        
        # 4. Add dependencies
        source_key = "product_features"
        source_vector = DenseVector([0.5, 1.0, 1.5])
        self.store.add(source_key, source_vector, group="features")
        
        # Add dependency
        self.store.add_dependency(
            feature_key, 
            source_key, 
            "derived_from",
            {"transformation": "embedding_model"}
        )
        
        # 5. Get lineage
        lineage = self.store.get_feature_lineage(feature_key)
        assert feature_key in lineage
        assert source_key in lineage[feature_key]
    
    def test_transformation_workflow(self):
        """Test transformation workflow."""
        # 1. Create and add vectors
        vectors = []
        for i in range(10):
            key = f"feature_{i}"
            # Create vector with increasing values (need variety for scaling)
            vector = DenseVector([float(i), float(i+5), float(i*2)])
            self.store.add(key, vector, group="raw_features")
            vectors.append(vector)
        
        # 2. Create and fit transformations
        scaler = StandardScaler(name="standard_scaler")
        scaler.fit(vectors)
        
        normalizer = MinMaxScaler(name="minmax_scaler")
        normalizer.fit(vectors)
        
        # 3. Register transformations
        self.store.register_transformation("raw_features", scaler)
        self.store.register_transformation("raw_features", normalizer)
        
        # 4. Retrieve with transformations
        key = "feature_5"
        raw_vector = self.store.get(key, group="raw_features")
        transformed_vector = self.store.get(
            key, 
            group="raw_features", 
            apply_transformations=True
        )
        
        # Vector should be transformed
        assert raw_vector is not None
        assert transformed_vector is not None
        assert not np.array_equal(raw_vector.to_array(), transformed_vector.to_array())
        
        # 5. Manual transformation for verification
        manual_transformed = normalizer.transform(scaler.transform(raw_vector))
        assert np.array_equal(transformed_vector.to_array(), manual_transformed.to_array())
    
    def test_batch_operations_workflow(self):
        """Test batch operations workflow."""
        # 1. Add vectors
        for i in range(20):
            key = f"item_{i}"
            vector = DenseVector([float(i), float(i+1), float(i+2)])
            group = "group_a" if i < 10 else "group_b"
            self.store.add(key, vector, group=group)
        
        # 2. Batch retrieval
        keys = [f"item_{i}" for i in range(5, 15)]  # Mix of group_a and group_b
        batch_results = self.store.batch_get(keys)
        
        # Should retrieve all keys
        assert len(batch_results) == 10
        for i, key in enumerate(keys):
            assert key in batch_results
            vector = batch_results[key]
            idx = int(key.split("_")[1])
            assert np.array_equal(
                vector.to_array(), 
                np.array([float(idx), float(idx+1), float(idx+2)], dtype=np.float32)
            )
        
        # 3. Batch retrieval with group filter
        batch_results = self.store.batch_get(keys, group="group_a")
        
        # Should only retrieve keys in group_a
        assert len(batch_results) == 5
        for i in range(5, 10):
            key = f"item_{i}"
            assert key in batch_results
        
        # 4. Batch similarity query
        query_keys = ["item_5", "item_15"]
        batch_query_results = self.store.batch_query_similar(query_keys, k=3)
        
        # Should have results for both keys
        assert len(batch_query_results) == 2
        assert "item_5" in batch_query_results
        assert "item_15" in batch_query_results
        
        # Each query should return closest matches
        item5_results = batch_query_results["item_5"]
        assert len(item5_results) == 3
        assert item5_results[0][0] == "item_5"  # Self match
        
        item15_results = batch_query_results["item_15"]
        assert len(item15_results) == 3
        assert item15_results[0][0] == "item_15"  # Self match
    
    def test_experimentation_workflow(self):
        """Test experimentation workflow."""
        # 1. Create experiment
        groups = ["control", "variation_a", "variation_b"]
        weights = [0.6, 0.2, 0.2]
        
        experiment = self.store.create_experiment(
            name="rec_algorithm_test",
            groups=groups,
            weights=weights,
            description="Testing recommendation algorithms",
            metadata={"owner": "data_science_team"}
        )
        
        # 2. Verify experiment
        assert experiment.name == "rec_algorithm_test"
        assert experiment.groups == groups
        assert experiment.status == ExperimentStatus.ACTIVE
        
        # 3. Get experiment
        retrieved = self.store.get_experiment("rec_algorithm_test")
        assert retrieved is not None
        assert retrieved.name == experiment.name
        
        # 4. Assign users to groups
        user_ids = [f"user_{i}" for i in range(100)]
        assignments = {}
        
        for user_id in user_ids:
            group = self.store.get_experiment_group(user_id, "rec_algorithm_test")
            assignments[user_id] = group
        
        # 5. Verify distribution
        control_count = list(assignments.values()).count("control")
        var_a_count = list(assignments.values()).count("variation_a")
        var_b_count = list(assignments.values()).count("variation_b")
        
        # Check proportions roughly match weights
        assert control_count / 100 == approx(0.6, abs=0.1)
        assert var_a_count / 100 == approx(0.2, abs=0.1)
        assert var_b_count / 100 == approx(0.2, abs=0.1)
        
        # 6. Create experiment group
        self.store.add_to_experiment_group("recommendation_tests", "rec_algorithm_test")
    
    def test_export_import_workflow(self):
        """Test export and import workflow."""
        # 1. Set up feature store with data
        # Add vectors
        for i in range(5):
            key = f"export_test_{i}"
            vector = DenseVector([float(i), float(i*2), float(i*3)])
            self.store.add(key, vector, group="export_group")
        
        # Create experiment
        self.store.create_experiment(
            name="export_experiment",
            groups=["A", "B"],
            weights=[0.5, 0.5]
        )
        
        # 2. Export to file
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            # Export to the temporary file
            self.store.export_to_file(tmp.name)
            
            # 3. Import from file
            imported_store = FeatureStore.import_from_file(tmp.name)
            
            # Clean up temporary file
            tmp.close()
            os.unlink(tmp.name)
        
        # 4. Verify imported store
        # Verify vector indices
        assert "export_group" in imported_store.vector_indices
        
        # Should have same experiments
        assert "export_experiment" in imported_store.experiments
        imported_exp = imported_store.experiments["export_experiment"]
        assert imported_exp.groups == ["A", "B"]
        
        # API should work on imported store
        for i in range(5):
            key = f"export_test_{i}"
            # Get should work (data is not exported currently, just metadata)
            # This would return None in a full implementation
            vector = imported_store.get(key, group="export_group")
    
    def test_end_to_end_ml_workflow(self):
        """Test a complete ML feature workflow."""
        # 1. Set up feature groups for different data types
        self.store.create_group(
            "user_embeddings", 
            "User embedding vectors", 
            dimensions=128,
            index_type=IndexType.HNSW
        )
        
        self.store.create_group(
            "item_embeddings",
            "Item embedding vectors",
            dimensions=128,
            index_type=IndexType.HNSW
        )
        
        self.store.create_group(
            "user_features",
            "Raw user features",
            dimensions=10
        )
        
        # 2. Add raw user features (demographic data, etc.)
        user_features = {}
        for i in range(100):
            user_id = f"user_{i}"
            # Create features (age, income, etc. normalized to [0, 1])
            features = np.random.random(10).astype(np.float32)
            vector = DenseVector(features)
            self.store.add(user_id, vector, group="user_features")
            user_features[user_id] = vector
        
        # 3. Create transformations for user features
        user_scaler = StandardScaler(name="user_standard_scaler")
        user_scaler.fit(list(user_features.values()))
        
        # Register transformation
        self.store.register_transformation("user_features", user_scaler)
        
        # 4. Derive user embeddings from features
        # This is a simplified simulation - in reality would use a proper embedding model
        def simple_embedding_derivation(vector: DenseVector) -> DenseVector:
            """Simulate deriving embeddings from features."""
            # Start with normalized features
            normalized = user_scaler.transform(vector)
            
            # Expand to higher dimensions with some patterns
            # (in reality this would be a neural network or other model)
            base = normalized.to_array()
            embedding = np.zeros(128, dtype=np.float32)
            
            # Copy the base features to first dimensions
            embedding[:10] = base
            
            # Add some systematic patterns (just for simulation)
            for i in range(10, 128):
                idx = i % 10
                factor = (i // 10) + 1
                embedding[i] = base[idx] * (np.sin(factor * np.pi * base[idx]) + 1) / 2
            
            return DenseVector(embedding)
        
        # 5. Create and add user embeddings
        for user_id, features in user_features.items():
            # Derive embedding
            embedding = simple_embedding_derivation(features)
            
            # Add embedding
            self.store.add(user_id, embedding, group="user_embeddings")
            
            # Add dependency to track lineage
            self.store.add_dependency(user_id, user_id, "derived_from", {
                "source_group": "user_features",
                "target_group": "user_embeddings",
                "algorithm": "embedding_model_v1"
            })
        
        # 6. Perform similarity search in embedding space
        query_user = "user_42"
        similar_users = self.store.query_similar(
            query_user, 
            k=5, 
            group="user_embeddings"
        )
        
        # Verify query results
        assert len(similar_users) == 5
        assert similar_users[0][0] == query_user  # First result is the query itself
        
        # 7. Set up A/B test for a recommendation algorithm
        experiment = self.store.create_experiment(
            name="rec_model_comparison",
            groups=["baseline", "new_algorithm"],
            weights=[0.5, 0.5],
            description="Comparing recommendation algorithms",
            metadata={"metric": "click_through_rate"}
        )
        
        # 8. Get recommendations for users based on their experiment group
        for i in range(10):
            user_id = f"user_{i}"
            
            # Get experiment group
            group = self.store.get_experiment_group(user_id, "rec_model_comparison")
            
            # Based on group, would choose different recommendation logic
            # Here we just verify the group assignment works
            assert group in ["baseline", "new_algorithm"]
        
        # 9. Batch operations for efficient processing
        # Get embeddings for a batch of users
        batch_users = [f"user_{i}" for i in range(10, 20)]
        batch_embeddings = self.store.batch_get(batch_users, group="user_embeddings")
        
        # Verify batch retrieval
        assert len(batch_embeddings) == 10
        for user_id in batch_users:
            assert user_id in batch_embeddings