"""
Unit tests for the versioning system.
"""

import time
from typing import Dict, List, Optional, Set, Tuple

import numpy as np
import pytest
from pytest import approx

from feature_store.vectors.dense import DenseVector
from feature_store.versioning.lineage import (
    DependencyType, LineageNode, LineageTracker
)
from feature_store.versioning.timeline import (
    Timeline, VersionInfo, VersionType
)
from feature_store.versioning.version_store import (
    FeatureGroup, VersionStore
)


class TestTimeline:
    """Tests for the Timeline class."""

    def test_add_version(self):
        """Test adding versions to a timeline."""
        timeline = Timeline()
        vector1 = DenseVector([1.0, 2.0, 3.0])
        vector2 = DenseVector([4.0, 5.0, 6.0])
        
        # Add version with timestamp
        timestamp1 = 1000.0
        version_id1 = timeline.add_version(vector1, timestamp=timestamp1)
        assert version_id1 == str(timestamp1)
        
        # Add version with tag
        tag = "v1"
        version_id2 = timeline.add_version(vector2, tag=tag)
        assert version_id2 == tag
        
        # Verify size
        assert len(timeline) == 2
        
        # Verify contents
        version1 = timeline.get_version(version_id1)
        assert version1 is not None
        assert version1.version_id == version_id1
        assert version1.version_type == VersionType.TIMESTAMP
        assert version1.timestamp == timestamp1
        assert version1.vector == vector1
        
        version2 = timeline.get_version(version_id2)
        assert version2 is not None
        assert version2.version_id == version_id2
        assert version2.version_type == VersionType.TAG
        assert version2.vector == vector2
    
    def test_timeline_tagging(self):
        """Test adding tags to versions."""
        timeline = Timeline()
        vector = DenseVector([1.0, 2.0, 3.0])
        
        # Add version
        timestamp = 1000.0
        version_id = timeline.add_version(vector, timestamp=timestamp)
        
        # Add tag
        tag = "production"
        assert timeline.add_tag(version_id, tag)
        
        # Verify tag
        version_by_tag = timeline.get_version(tag)
        assert version_by_tag is not None
        assert version_by_tag.version_id == version_id
        
        # Try to add duplicate tag
        with pytest.raises(ValueError):
            timeline.add_version(vector, tag=tag)
        
        # Remove tag
        assert timeline.remove_tag(tag)
        assert timeline.get_version(tag) is None
        
        # Try to remove non-existent tag
        assert not timeline.remove_tag("non-existent")
    
    def test_version_retrieval(self):
        """Test retrieving versions from a timeline."""
        timeline = Timeline()
        
        # Add multiple versions at different times
        timestamps = [1000.0, 2000.0, 3000.0, 4000.0]
        vectors = [
            DenseVector([1.0, 2.0, 3.0]),
            DenseVector([2.0, 3.0, 4.0]),
            DenseVector([3.0, 4.0, 5.0]),
            DenseVector([4.0, 5.0, 6.0])
        ]
        
        for i, (timestamp, vector) in enumerate(zip(timestamps, vectors)):
            timeline.add_version(vector, timestamp=timestamp)
        
        # Get latest version
        latest = timeline.get_latest_version()
        assert latest is not None
        assert latest.timestamp == timestamps[-1]
        assert latest.vector == vectors[-1]
        
        # Get version at specific time
        # At exact time
        version_at_2000 = timeline.get_version_at_time(2000.0)
        assert version_at_2000 is not None
        assert version_at_2000.timestamp == 2000.0
        assert version_at_2000.vector == vectors[1]
        
        # Between versions (should get the latest version before the time)
        version_at_2500 = timeline.get_version_at_time(2500.0)
        assert version_at_2500 is not None
        assert version_at_2500.timestamp == 2000.0
        assert version_at_2500.vector == vectors[1]
        
        # Before first version
        version_at_500 = timeline.get_version_at_time(500.0)
        assert version_at_500 is None
        
        # After last version
        version_at_5000 = timeline.get_version_at_time(5000.0)
        assert version_at_5000 is not None
        assert version_at_5000.timestamp == 4000.0
        assert version_at_5000.vector == vectors[3]
        
        # Get versions in range
        versions_2000_to_3000 = timeline.get_versions_in_range(2000.0, 3000.0)
        assert len(versions_2000_to_3000) == 2
        assert versions_2000_to_3000[0].timestamp == 2000.0
        assert versions_2000_to_3000[1].timestamp == 3000.0
    
    def test_version_metadata(self):
        """Test adding and retrieving version metadata."""
        timeline = Timeline()
        vector = DenseVector([1.0, 2.0, 3.0])
        
        # Add version with metadata
        metadata = {"source": "test", "quality": "high"}
        version_id = timeline.add_version(vector, metadata=metadata)
        
        # Verify metadata
        version = timeline.get_version(version_id)
        assert version is not None
        assert version.metadata == metadata


class TestLineageTracker:
    """Tests for the LineageTracker class."""

    def test_feature_registration(self):
        """Test registering features."""
        tracker = LineageTracker()
        
        # Register features
        tracker.register_feature("feature1", {"type": "embedding"})
        tracker.register_feature("feature2", {"type": "scalar"})
        
        # Verify registration
        assert "feature1" in tracker.nodes
        assert "feature2" in tracker.nodes
        assert tracker.nodes["feature1"].metadata["type"] == "embedding"
        assert tracker.nodes["feature2"].metadata["type"] == "scalar"
        
        # Try to register duplicate
        with pytest.raises(ValueError):
            tracker.register_feature("feature1")
        
        # Get all features
        features = tracker.get_all_features()
        assert set(features) == {"feature1", "feature2"}
    
    def test_dependency_tracking(self):
        """Test adding and tracking dependencies."""
        tracker = LineageTracker()
        
        # Register features
        tracker.register_feature("raw_data")
        tracker.register_feature("processed_data")
        tracker.register_feature("model_input")
        tracker.register_feature("model_output")
        
        # Add dependencies
        tracker.add_dependency(
            "processed_data", "raw_data", DependencyType.DERIVED_FROM,
            {"transformation": "normalization"}
        )
        tracker.add_dependency(
            "model_input", "processed_data", DependencyType.DERIVED_FROM,
            {"transformation": "feature_extraction"}
        )
        tracker.add_dependency(
            "model_output", "model_input", DependencyType.COMPUTED_WITH,
            {"model": "neural_network"}
        )
        
        # Verify dependencies
        # Direct dependencies
        deps = tracker.get_feature_dependencies("processed_data")
        assert len(deps) == 1
        assert deps[0].source == "processed_data"
        assert deps[0].target == "raw_data"
        assert deps[0].type == DependencyType.DERIVED_FROM
        assert deps[0].metadata["transformation"] == "normalization"
        
        # Dependents
        deps = tracker.get_feature_dependents("processed_data")
        assert len(deps) == 1
        assert deps[0].source == "model_input"
        assert deps[0].target == "processed_data"
        
        # Get specific dependency
        dep = tracker.get_dependency("model_output", "model_input")
        assert dep is not None
        assert dep.type == DependencyType.COMPUTED_WITH
        assert dep.metadata["model"] == "neural_network"
        
        # Try to get non-existent dependency
        assert tracker.get_dependency("raw_data", "model_output") is None
        
        # Remove dependency
        assert tracker.remove_dependency("model_output", "model_input")
        assert tracker.get_dependency("model_output", "model_input") is None
        
        # Try to remove non-existent dependency
        assert not tracker.remove_dependency("raw_data", "model_output")
    
    def test_lineage_and_impact(self):
        """Test lineage and impact analysis."""
        tracker = LineageTracker()
        
        # Create a simple pipeline:
        # raw_data -> cleaned_data -> normalized_data -> feature_vector -> model_input -> model_output
        features = [
            "raw_data",
            "cleaned_data",
            "normalized_data",
            "feature_vector",
            "model_input",
            "model_output"
        ]
        
        for feature in features:
            tracker.register_feature(feature)
        
        # Add dependencies
        for i in range(1, len(features)):
            tracker.add_dependency(
                features[i], features[i-1], DependencyType.DERIVED_FROM,
                {"step": f"step_{i}"}
            )
        
        # Get lineage for model_output (should be the entire pipeline)
        lineage = tracker.get_lineage("model_output")
        
        # Verify lineage structure
        assert set(lineage.keys()) == set(features)
        assert lineage["model_output"] == {"model_input"}
        assert lineage["model_input"] == {"feature_vector"}
        assert lineage["feature_vector"] == {"normalized_data"}
        assert lineage["normalized_data"] == {"cleaned_data"}
        assert lineage["cleaned_data"] == {"raw_data"}
        assert lineage["raw_data"] == set()
        
        # Get lineage with depth limit
        limited_lineage = tracker.get_lineage("model_output", max_depth=2)
        assert set(limited_lineage.keys()) == {"model_output", "model_input", "feature_vector"}
        
        # Get impact for raw_data (should be the entire pipeline)
        impact = tracker.get_impact("raw_data")
        
        # Verify impact structure
        assert set(impact.keys()) == set(features)
        assert impact["raw_data"] == {"cleaned_data"}
        assert impact["cleaned_data"] == {"normalized_data"}
        assert impact["normalized_data"] == {"feature_vector"}
        assert impact["feature_vector"] == {"model_input"}
        assert impact["model_input"] == {"model_output"}
        assert impact["model_output"] == set()
        
        # Get impact with depth limit
        limited_impact = tracker.get_impact("raw_data", max_depth=2)
        assert set(limited_impact.keys()) == {"raw_data", "cleaned_data", "normalized_data"}
    
    def test_metadata_management(self):
        """Test feature metadata management."""
        tracker = LineageTracker()
        
        # Register feature with metadata
        initial_metadata = {"type": "embedding", "dimensions": "128"}
        tracker.register_feature("feature", initial_metadata)
        
        # Get metadata
        metadata = tracker.get_feature_metadata("feature")
        assert metadata == initial_metadata
        
        # Update metadata
        tracker.update_feature_metadata("feature", {"source": "user_profile", "dimensions": "256"})
        
        # Verify updated metadata
        updated_metadata = tracker.get_feature_metadata("feature")
        assert updated_metadata["type"] == "embedding"
        assert updated_metadata["dimensions"] == "256"  # Updated
        assert updated_metadata["source"] == "user_profile"  # Added


class TestVersionStore:
    """Tests for the VersionStore class."""

    def test_add_and_get_feature(self):
        """Test adding and retrieving features."""
        store = VersionStore()
        
        # Add feature
        vector = DenseVector([1.0, 2.0, 3.0])
        version_id = store.add_feature("feature1", vector, group="group1")
        
        # Get feature
        retrieved = store.get_feature("feature1")
        assert retrieved is not None
        assert retrieved == vector
        
        # Get feature with version
        retrieved = store.get_feature("feature1", version_id)
        assert retrieved is not None
        assert retrieved == vector
        
        # Get feature with timestamp
        timestamp = float(version_id)
        retrieved = store.get_feature("feature1", timestamp)
        assert retrieved is not None
        assert retrieved == vector
        
        # Add another version
        vector2 = DenseVector([4.0, 5.0, 6.0])
        version_id2 = store.add_feature("feature1", vector2, tag="v2")
        
        # Get with tag
        retrieved = store.get_feature("feature1", "v2")
        assert retrieved is not None
        assert retrieved == vector2
        
        # Get latest (should be second version)
        retrieved = store.get_feature("feature1")
        assert retrieved is not None
        assert retrieved == vector2
    
    def test_feature_groups(self):
        """Test feature groups."""
        store = VersionStore()
        
        # Create groups
        store.create_group("group1", "First group", {"purpose": "testing"})
        store.create_group("group2", "Second group")
        
        # Add features to groups
        vector1 = DenseVector([1.0, 2.0, 3.0])
        vector2 = DenseVector([4.0, 5.0, 6.0])
        
        store.add_feature("feature1", vector1, group="group1")
        store.add_feature("feature2", vector2, group="group2")
        
        # Get features in group
        group1_features = store.get_features_in_group("group1")
        assert "feature1" in group1_features
        
        group2_features = store.get_features_in_group("group2")
        assert "feature2" in group2_features
        
        # Get group for feature
        group = store.get_feature_group("feature1")
        assert group is not None
        assert group.name == "group1"
        assert group.description == "First group"
        assert group.metadata["purpose"] == "testing"
        
        # Move feature to different group
        store.add_feature_to_group("feature1", "group2")
        
        # Verify new group
        new_group = store.get_feature_group("feature1")
        assert new_group is not None
        assert new_group.name == "group2"
        
        # Verify feature is removed from old group
        group1_features = store.get_features_in_group("group1")
        assert "feature1" not in group1_features
    
    def test_version_history(self):
        """Test retrieving version history."""
        store = VersionStore()
        
        # Add feature with multiple versions
        feature_key = "feature"
        vectors = [
            DenseVector([i * 1.0, i * 2.0, i * 3.0])
            for i in range(1, 5)
        ]
        
        timestamps = [1000.0, 2000.0, 3000.0, 4000.0]
        
        for i, (vector, timestamp) in enumerate(zip(vectors, timestamps)):
            store.add_feature(
                feature_key, 
                vector, 
                tag=f"v{i+1}",
                timestamp=timestamp
            )
        
        # Get version history
        history = store.get_version_history(feature_key)
        assert len(history) == 4
        
        # Verify history is sorted by timestamp
        for i, (version_id, timestamp) in enumerate(history):
            assert timestamp == timestamps[i]
        
        # Get history in time range
        history = store.get_version_history(feature_key, 2000.0, 3000.0)
        assert len(history) == 2
        assert history[0][1] == 2000.0
        assert history[1][1] == 3000.0
    
    def test_metadata_and_tagging(self):
        """Test metadata and version tagging."""
        store = VersionStore()
        
        # Add feature with metadata
        vector = DenseVector([1.0, 2.0, 3.0])
        metadata = {"source": "test", "quality": "high"}
        version_id = store.add_feature("feature", vector, metadata=metadata)
        
        # Get metadata
        retrieved_metadata = store.get_version_metadata("feature", version_id)
        assert retrieved_metadata == metadata
        
        # Add tag to version
        assert store.add_tag("feature", version_id, "production")
        
        # Get feature by tag
        retrieved = store.get_feature("feature", "production")
        assert retrieved is not None
        assert retrieved == vector
    
    def test_dependencies(self):
        """Test feature dependencies."""
        store = VersionStore()
        
        # Add features
        store.add_feature("raw", DenseVector([1.0, 2.0, 3.0]))
        store.add_feature("processed", DenseVector([2.0, 3.0, 4.0]))
        
        # Add dependency
        store.add_dependency(
            "processed", "raw", "derived_from",
            {"transformation": "normalization"}
        )
        
        # Get dependencies
        deps = store.get_feature_dependencies("processed")
        assert len(deps) == 1
        assert deps[0]["source"] == "processed"
        assert deps[0]["target"] == "raw"
        assert deps[0]["type"] == "derived_from"
        assert deps[0]["transformation"] == "normalization"
        
        # Get lineage
        lineage = store.get_feature_lineage("processed")
        assert set(lineage.keys()) == {"processed", "raw"}
        assert lineage["processed"] == ["raw"]
        assert lineage["raw"] == []