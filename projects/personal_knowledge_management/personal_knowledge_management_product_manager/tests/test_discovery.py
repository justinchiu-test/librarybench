"""
Tests for the discovery module.

This module tests the knowledge discovery and insights functionality
of the ProductInsight system.
"""

import os
from datetime import datetime, timedelta
from uuid import UUID, uuid4

import pytest

from product_insight.discovery.insights import (
    InsightEngine,
    Insight,
    InsightGroup,
    TrendData
)
from product_insight.discovery.search import SearchEngine
from product_insight.models import (
    Competitor,
    Decision,
    Feature,
    FeedbackCluster,
    FeedbackItem,
    SearchQuery,
    SearchResults,
    Stakeholder,
    StakeholderPerspective,
    StrategicObjective,
    SentimentEnum,
    StatusEnum
)
from product_insight.storage import FileStorage

from tests.fixtures.fixtures import (
    mock_data_generator,
    mock_feedback_items,
    mock_features,
    mock_competitors,
    mock_decisions,
    mock_stakeholders,
    populated_storage_dir,
    temp_dir,
)


class TestSearchEngine:
    """Tests for the SearchEngine class."""
    
    def test_build_index(self, populated_storage_dir):
        """Test building the search index."""
        # Create a search engine with the populated storage
        engine = SearchEngine(storage_dir=populated_storage_dir)
        
        # Build the index
        index_info = engine.build_index()
        
        # Check results
        assert index_info.total_documents > 0
        assert index_info.execution_time_ms > 0
        assert index_info.index_size_bytes > 0
    
    def test_search_basic(self, populated_storage_dir):
        """Test basic search functionality."""
        # Create a search engine with the populated storage
        engine = SearchEngine(storage_dir=populated_storage_dir)
        
        # Build the index
        engine.build_index()
        
        # Create a simple search query
        query = SearchQuery(
            query="performance",
            limit=10
        )
        
        # Perform search
        results = engine.search(query)
        
        # Check results
        assert isinstance(results, SearchResults)
        assert results.query == "performance"
        assert results.execution_time_ms > 0
        assert len(results.results) <= 10  # Should not exceed limit
    
    def test_search_with_filters(self, populated_storage_dir):
        """Test search with entity type filters."""
        # Create a search engine with the populated storage
        engine = SearchEngine(storage_dir=populated_storage_dir)
        
        # Build the index
        engine.build_index()
        
        # Create a filtered search query
        query = SearchQuery(
            query="feature",
            include_feedback=False,
            include_features=True,
            include_objectives=False,
            include_decisions=False,
            include_competitors=False,
            include_stakeholders=False,
            limit=10
        )
        
        # Perform search
        results = engine.search(query)
        
        # Check results
        assert results.total_count >= 0
        
        # All results should be features
        for result in results.results:
            assert result.entity_type == "feature"
    
    def test_search_with_date_range(self, populated_storage_dir):
        """Test search with date range filter."""
        # Create a search engine with the populated storage
        engine = SearchEngine(storage_dir=populated_storage_dir)
        
        # Build the index
        engine.build_index()
        
        # Create a date-filtered search query
        now = datetime.now()
        date_from = now - timedelta(days=90)
        
        query = SearchQuery(
            query="important",
            date_from=date_from,
            date_to=now,
            limit=10
        )
        
        # Perform search
        results = engine.search(query)
        
        # Check results
        assert results.total_count >= 0
        
        # All results should be within the date range
        for result in results.results:
            assert date_from <= result.date <= now
    
    def test_search_with_tags(self, populated_storage_dir):
        """Test search with tag filters."""
        # Create a search engine with the populated storage
        engine = SearchEngine(storage_dir=populated_storage_dir)
        
        # Build the index
        engine.build_index()
        
        # Create a tag-filtered search query
        query = SearchQuery(
            query="feature",
            tags=["performance", "mobile"],  # Look for items with these tags
            limit=10
        )
        
        # Perform search
        results = engine.search(query)
        
        # Check results
        assert results.total_count >= 0
        
        # Results should have facets
        if results.facets and "tags" in results.facets:
            # The tags facet should show counts of matching tags
            assert len(results.facets["tags"]) > 0
    
    def test_complex_search(self, populated_storage_dir):
        """Test complex search with multiple filters."""
        # Create a search engine with the populated storage
        engine = SearchEngine(storage_dir=populated_storage_dir)
        
        # Build the index
        engine.build_index()
        
        # Create a complex search query
        now = datetime.now()
        date_from = now - timedelta(days=180)
        
        query = SearchQuery(
            query="user experience mobile",
            include_feedback=True,
            include_features=True,
            include_objectives=True,
            include_decisions=False,
            include_competitors=False,
            include_stakeholders=False,
            tags=["mobile", "ux"],
            date_from=date_from,
            limit=20
        )
        
        # Perform search
        results = engine.search(query)
        
        # Check results
        assert results.total_count >= 0
        assert results.execution_time_ms > 0
        
        # Should have facets for entity_type
        if results.facets and "entity_type" in results.facets:
            # The entity_type facet should only include the requested types
            entity_types = results.facets["entity_type"].keys()
            for entity_type in entity_types:
                assert entity_type in ["feedback", "feature", "objective"]
    
    def test_relevance_ranking(self, populated_storage_dir):
        """Test that search results are properly ranked by relevance."""
        # Create a search engine with the populated storage
        engine = SearchEngine(storage_dir=populated_storage_dir)
        
        # Build the index
        engine.build_index()
        
        # Create a search query
        query = SearchQuery(
            query="performance optimization",
            limit=10
        )
        
        # Perform search
        results = engine.search(query)
        
        # Check that results are ordered by relevance score (highest first)
        if len(results.results) > 1:
            scores = [result.relevance_score for result in results.results]
            assert scores == sorted(scores, reverse=True)
    
    def test_find_connections(self, populated_storage_dir):
        """Test finding connections between entities."""
        # Create a search engine with the populated storage
        engine = SearchEngine(storage_dir=populated_storage_dir)
        
        # Build the index
        engine.build_index()
        
        # Create some entity IDs for testing (using UUIDs that may not exist)
        feature_id = uuid4()
        stakeholder_id = uuid4()
        
        # Find connections
        connections = engine.find_connections(feature_id, stakeholder_id)
        
        # Check result structure
        assert "primary_entity" in connections
        assert "secondary_entity" in connections
        assert "connection_type" in connections
        assert "connection_strength" in connections
        assert "path" in connections
    
    def test_get_related_entities(self, populated_storage_dir):
        """Test getting related entities."""
        # Create a search engine with the populated storage
        engine = SearchEngine(storage_dir=populated_storage_dir)
        
        # Build the index
        engine.build_index()
        
        # Create a feature ID for testing (using a UUID that may not exist)
        entity_id = uuid4()
        entity_type = "feature"
        
        # Get related entities
        related = engine.get_related_entities(entity_id, entity_type)
        
        # Check result structure
        assert "source_entity" in related
        assert "related_entities" in related
        
        # Related entities should be grouped by type
        if related["related_entities"]:
            for entity_type, entities in related["related_entities"].items():
                assert isinstance(entities, list)


class TestInsightEngine:
    """Tests for the InsightEngine class."""
    
    def test_generate_feedback_insights(self, populated_storage_dir):
        """Test generating insights from feedback data."""
        # Create an insight engine with the populated storage
        engine = InsightEngine(storage_dir=populated_storage_dir)
        
        # Generate feedback insights
        insights = engine.generate_feedback_insights()
        
        # Check results
        assert isinstance(insights, list)
        for insight in insights:
            assert isinstance(insight, Insight)
            assert insight.title
            assert insight.description
            assert 0 <= insight.confidence <= 1
            assert insight.insight_type
    
    def test_generate_feature_insights(self, populated_storage_dir):
        """Test generating insights from feature data."""
        # Create an insight engine with the populated storage
        engine = InsightEngine(storage_dir=populated_storage_dir)
        
        # Generate feature insights
        insights = engine.generate_feature_insights()
        
        # Check results
        assert isinstance(insights, list)
        for insight in insights:
            assert isinstance(insight, Insight)
            assert insight.title
            assert insight.description
            assert 0 <= insight.confidence <= 1
            assert insight.insight_type
    
    def test_generate_objective_insights(self, populated_storage_dir):
        """Test generating insights from objective data."""
        # Create an insight engine with the populated storage
        engine = InsightEngine(storage_dir=populated_storage_dir)
        
        # Generate objective insights
        insights = engine.generate_objective_insights()
        
        # Check results
        assert isinstance(insights, list)
        for insight in insights:
            assert isinstance(insight, Insight)
            assert insight.title
            assert insight.description
            assert 0 <= insight.confidence <= 1
            assert insight.insight_type
    
    def test_generate_decision_insights(self, populated_storage_dir):
        """Test generating insights from decision data."""
        # Create an insight engine with the populated storage
        engine = InsightEngine(storage_dir=populated_storage_dir)
        
        # Generate decision insights
        insights = engine.generate_decision_insights()
        
        # Check results
        assert isinstance(insights, list)
        for insight in insights:
            assert isinstance(insight, Insight)
            assert insight.title
            assert insight.description
            assert 0 <= insight.confidence <= 1
            assert insight.insight_type
    
    def test_generate_stakeholder_insights(self, populated_storage_dir):
        """Test generating insights from stakeholder data."""
        # Create an insight engine with the populated storage
        engine = InsightEngine(storage_dir=populated_storage_dir)
        
        # Generate stakeholder insights
        insights = engine.generate_stakeholder_insights()
        
        # Check results
        assert isinstance(insights, list)
        for insight in insights:
            assert isinstance(insight, Insight)
            assert insight.title
            assert insight.description
            assert 0 <= insight.confidence <= 1
            assert insight.insight_type
    
    def test_generate_competitive_insights(self, populated_storage_dir):
        """Test generating insights from competitive data."""
        # Create an insight engine with the populated storage
        engine = InsightEngine(storage_dir=populated_storage_dir)
        
        # Generate competitive insights
        insights = engine.generate_competitive_insights()
        
        # Check results
        assert isinstance(insights, list)
        for insight in insights:
            assert isinstance(insight, Insight)
            assert insight.title
            assert insight.description
            assert 0 <= insight.confidence <= 1
            assert insight.insight_type
    
    def test_generate_cross_domain_insights(self, populated_storage_dir):
        """Test generating cross-domain insights."""
        # Create an insight engine with the populated storage
        engine = InsightEngine(storage_dir=populated_storage_dir)
        
        # Generate cross-domain insights
        insights = engine.generate_cross_domain_insights()
        
        # Check results
        assert isinstance(insights, list)
        for insight in insights:
            assert isinstance(insight, Insight)
            assert insight.title
            assert insight.description
            assert 0 <= insight.confidence <= 1
            assert insight.insight_type == "cross-domain"
    
    def test_generate_all_insights(self, populated_storage_dir):
        """Test generating all insights."""
        # Create an insight engine with the populated storage
        engine = InsightEngine(storage_dir=populated_storage_dir)
        
        # Generate all insights
        insight_groups = engine.generate_all_insights()
        
        # Check results
        assert isinstance(insight_groups, list)
        for group in insight_groups:
            assert isinstance(group, InsightGroup)
            assert group.title
            assert group.insight_type
            assert isinstance(group.insights, list)
            
            # Check individual insights in each group
            for insight in group.insights:
                assert isinstance(insight, Insight)
                assert insight.title
                assert insight.description
                assert 0 <= insight.confidence <= 1
    
    def test_generate_trend_analysis(self, populated_storage_dir):
        """Test generating trend analysis."""
        # Create an insight engine with the populated storage
        engine = InsightEngine(storage_dir=populated_storage_dir)
        
        # Generate trend analysis
        trends = engine.generate_trend_analysis(days=180, interval_days=30)
        
        # Check results
        assert isinstance(trends, list)
        for trend in trends:
            assert isinstance(trend, TrendData)
            assert trend.title
            assert isinstance(trend.time_periods, list)
            assert isinstance(trend.series, dict)

            # Check series data
            for series_name, values in trend.series.items():
                assert isinstance(series_name, str)
                assert isinstance(values, list)
                assert len(values) == len(trend.time_periods)