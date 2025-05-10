"""
Performance benchmark tests for the ProductInsight system.

This module tests the performance of various components of the ProductInsight system
to ensure they meet the specified performance requirements.
"""

import time
from datetime import datetime

import pytest

from product_insight.discovery import SearchEngine, SearchQuery
from product_insight.feedback import ClusteringParams, FeedbackManager
from product_insight.models import FeedbackItem, Feature, SourceEnum
from product_insight.prioritization import (
    FeaturePrioritizer,
    PrioritizationMethod,
)

from tests.fixtures.fixtures import (
    mock_data_generator,
    populated_storage_dir,
    temp_dir,
)


class TestPerformanceBenchmarks:
    """Performance benchmark tests."""
    
    def test_feedback_clustering_performance(self, temp_dir):
        """Test feedback clustering performance with 1000+ items."""
        # Create a feedback manager
        manager = FeedbackManager(storage_dir=temp_dir)
        
        # Create mock data generator
        generator = mock_data_generator
        
        # Generate 1000+ feedback items
        num_items = 1000
        feedback_items = generator.generate_feedback_items(num_items)
        
        # Add all feedback items (without processing to speed up the test)
        added_items = manager.batch_add_feedback(feedback_items, process=False)
        
        # Process feedback items (which is normally done during add)
        for item in added_items:
            item.processed = True
            manager.feedback_storage.save(item)
        
        # Measure clustering time
        start_time = time.time()
        
        # Set clustering parameters
        params = ClusteringParams(
            min_cluster_size=5,
            min_similarity=0.3
        )
        
        # Cluster feedback
        result = manager.cluster_feedback(params=params, recalculate=True)
        
        # Calculate elapsed time
        elapsed_seconds = time.time() - start_time
        
        # Check performance (should be under 3 seconds as per requirements)
        assert elapsed_seconds < 3.0, f"Clustering {num_items} items took {elapsed_seconds:.2f} seconds (should be < 3.0)"
        
        # Check result
        assert result.num_clusters > 0
        assert result.execution_time_ms > 0
        assert len(result.clusters) == result.num_clusters
    
    def test_feature_prioritization_performance(self, temp_dir):
        """Test feature prioritization performance with 200+ features."""
        # Create a feature prioritizer
        prioritizer = FeaturePrioritizer(storage_dir=temp_dir)
        
        # Create mock data generator
        generator = mock_data_generator
        
        # Generate 200+ features
        num_features = 200
        features = generator.generate_features(num_features)
        
        # Add all features
        added_features = [prioritizer.add_feature(feature) for feature in features]
        feature_ids = [feature.id for feature in added_features]
        
        # Measure prioritization time
        start_time = time.time()
        
        # Prioritize features
        result = prioritizer.prioritize_features(
            feature_ids=feature_ids,
            method=PrioritizationMethod.WEIGHTED
        )
        
        # Calculate elapsed time
        elapsed_seconds = time.time() - start_time
        
        # Check performance (should be under 1 second as per requirements)
        assert elapsed_seconds < 1.0, f"Prioritizing {num_features} features took {elapsed_seconds:.2f} seconds (should be < 1.0)"
        
        # Check result
        assert len(result.scored_features) == num_features
        assert result.execution_time_ms > 0
    
    def test_search_performance(self, populated_storage_dir):
        """Test search performance across knowledge domains."""
        # Create a search engine
        engine = SearchEngine(storage_dir=populated_storage_dir)
        
        # Build the search index (this may take time but is typically done once at startup)
        print("Building search index...")
        engine.build_index()
        
        # Create a complex search query that spans multiple domains
        query = SearchQuery(
            query="feature",
            include_feedback=True,
            include_features=True,
            include_objectives=True,
            include_decisions=True,
            include_competitors=True,
            include_stakeholders=True,
            limit=50
        )
        
        # Measure search time
        start_time = time.time()
        
        # Perform search
        results = engine.search(query)
        
        # Calculate elapsed time
        elapsed_seconds = time.time() - start_time
        
        # Check performance (should be under 1 second as per requirements)
        assert elapsed_seconds < 1.0, f"Search across all domains took {elapsed_seconds:.2f} seconds (should be < 1.0)"
        
        # Check result timing agrees with elapsed time (within reasonable margin)
        timing_diff = abs((results.execution_time_ms / 1000) - elapsed_seconds)
        assert timing_diff < 0.1, f"Timing mismatch: {results.execution_time_ms}ms vs {elapsed_seconds*1000}ms"


@pytest.mark.skip(reason="Large scale test - run manually")
class TestLargeScalePerformance:
    """Large scale performance tests (skipped by default)."""
    
    def test_large_scale_feedback_clustering(self, temp_dir):
        """Test feedback clustering with a very large dataset (2000+ items)."""
        # Create a feedback manager
        manager = FeedbackManager(storage_dir=temp_dir)
        
        # Create mock data generator
        generator = mock_data_generator
        
        # Generate 2000+ feedback items (as specified in benchmark requirements)
        num_items = 2000
        print(f"Generating {num_items} feedback items...")
        feedback_items = generator.generate_feedback_items(num_items)
        
        # Add all feedback items (without processing to speed up the test)
        print("Adding feedback items...")
        added_items = manager.batch_add_feedback(feedback_items, process=False)
        
        # Process feedback items (which is normally done during add)
        print("Marking as processed...")
        for item in added_items:
            item.processed = True
            manager.feedback_storage.save(item)
        
        # Measure clustering time
        print("Clustering feedback...")
        start_time = time.time()
        
        # Set clustering parameters
        params = ClusteringParams(
            min_cluster_size=5,
            min_similarity=0.3
        )
        
        # Cluster feedback
        result = manager.cluster_feedback(params=params, recalculate=True)
        
        # Calculate elapsed time
        elapsed_seconds = time.time() - start_time
        
        # Check performance (should be under 5 seconds as per requirements)
        print(f"Clustering time: {elapsed_seconds:.2f} seconds")
        assert elapsed_seconds < 5.0, f"Clustering {num_items} items took {elapsed_seconds:.2f} seconds (should be < 5.0)"
        
        # Print results
        print(f"Created {result.num_clusters} clusters")
        print(f"Avg cluster size: {result.avg_cluster_size:.2f}")
        print(f"Unclustered items: {len(result.unclustered_items)}")
    
    def test_large_scale_feature_prioritization(self, temp_dir):
        """Test feature prioritization with a very large dataset (500+ features)."""
        # Create a feature prioritizer
        prioritizer = FeaturePrioritizer(storage_dir=temp_dir)
        
        # Create mock data generator
        generator = mock_data_generator
        
        # Generate 500+ features (as specified in benchmark requirements)
        num_features = 500
        print(f"Generating {num_features} features...")
        features = generator.generate_features(num_features)
        
        # Add all features
        print("Adding features...")
        added_features = [prioritizer.add_feature(feature) for feature in features]
        feature_ids = [feature.id for feature in added_features]
        
        # Measure prioritization time
        print("Prioritizing features...")
        start_time = time.time()
        
        # Prioritize features
        result = prioritizer.prioritize_features(
            feature_ids=feature_ids,
            method=PrioritizationMethod.WEIGHTED
        )
        
        # Calculate elapsed time
        elapsed_seconds = time.time() - start_time
        
        # Check performance (should be under 2 seconds as per requirements)
        print(f"Prioritization time: {elapsed_seconds:.2f} seconds")
        assert elapsed_seconds < 2.0, f"Prioritizing {num_features} features took {elapsed_seconds:.2f} seconds (should be < 2.0)"
        
        # Print top features
        top_features = prioritizer.get_top_features(limit=5)
        print("Top 5 features:")
        for feature, score in top_features:
            print(f"- {feature.name}: {score:.2f}")