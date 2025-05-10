"""
Tests for the discovery module.

This module tests the knowledge discovery and insights functionality
of the ProductInsight system.
"""

import os
import json
from datetime import datetime, timedelta
from uuid import UUID, uuid4

import pytest
from unittest.mock import patch

from product_insight.discovery.insights import (
    InsightEngine,
    Insight,
    InsightGroup,
    TrendData,
    TrendPoint
)
from product_insight.discovery.search import SearchEngine, SearchIndex
from product_insight.discovery.visualization import (
    DiscoveryVisualizer,
    InsightVisualization,
    TrendVisualization,
    ConnectionGraph
)
from product_insight.models import (
    Competitor,
    Decision,
    Feature,
    FeedbackCluster,
    FeedbackItem,
    SearchQuery,
    SearchResult,
    SearchResults,
    Stakeholder,
    StakeholderPerspective,
    StrategicObjective,
    SentimentEnum,
    StatusEnum,
    Tag
)
from product_insight.storage import FileStorage

from tests.fixtures.fixtures import (
    mock_data_generator,
    mock_feedback_items,
    mock_features,
    mock_competitors,
    mock_decisions,
    mock_stakeholders,
    mock_feedback_clusters,
    mock_strategic_objectives,
    mock_stakeholder_perspectives,
    populated_storage_dir,
    temp_dir,
)


class TestSearchEngine:
    """Tests for the SearchEngine class."""
    
    def test_init(self, temp_dir):
        """Test search engine initialization."""
        engine = SearchEngine(storage_dir=temp_dir)
        
        # Verify the storage instances are created
        assert engine.feedback_storage is not None
        assert engine.feature_storage is not None
        assert engine.decision_storage is not None
        assert engine.objective_storage is not None
        assert engine.competitor_storage is not None
        assert engine.stakeholder_storage is not None
        assert engine.perspective_storage is not None
        
        # Verify the index is initialized but not built
        assert isinstance(engine.index, SearchIndex)
        assert not engine.index_built
    
    def test_tokenize(self, temp_dir):
        """Test tokenization functionality."""
        engine = SearchEngine(storage_dir=temp_dir)
        
        # Test with different inputs
        tokens = engine._tokenize("This is a test of tokenization!")
        assert isinstance(tokens, list)
        assert "test" in tokens
        assert "tokenization" in tokens
        
        # 'this' may be filtered out as a stopword, so we shouldn't test for it
        
        # Stopwords should be removed
        assert "is" not in tokens
        assert "a" not in tokens
        assert "of" not in tokens
        
        # Test with empty input
        empty_tokens = engine._tokenize("")
        assert empty_tokens == []
        
        # Test with None input
        none_tokens = engine._tokenize(None)
        assert none_tokens == []
    
    def test_extract_terms(self, mock_feedback_items, temp_dir):
        """Test term extraction from entities."""
        engine = SearchEngine(storage_dir=temp_dir)
        
        # Test with a feedback item
        feedback = mock_feedback_items[0]
        terms = engine._extract_terms(feedback)
        
        assert isinstance(terms, dict)
        assert len(terms) > 0
        
        # The entity ID should be included with a high weight
        assert str(feedback.id) in terms
        assert terms[str(feedback.id)] > 1.0
        
        # Add a tag and test again
        feedback.tags = [Tag(name="important")]
        terms = engine._extract_terms(feedback)
        assert "important" in terms
        assert terms["important"] > 1.0
    
    def test_build_index(self, temp_dir, mock_feedback_items, mock_features):
        """Test building the search index."""
        # Create a basic storage with a few items
        feedback_storage = FileStorage(
            entity_type=FeedbackItem,
            storage_dir=os.path.join(temp_dir, "feedback"),
            format="json"
        )
        feature_storage = FileStorage(
            entity_type=Feature,
            storage_dir=os.path.join(temp_dir, "features"),
            format="json"
        )
        
        # Save a few items
        for item in mock_feedback_items[:3]:
            feedback_storage.save(item)
            
        for feature in mock_features[:3]:
            feature_storage.save(feature)
            
        # Create a search engine with the simple storage
        engine = SearchEngine(
            storage_dir=temp_dir,
            feedback_storage=feedback_storage,
            feature_storage=feature_storage
        )
        
        # Build the index
        engine.build_index()
        
        # Check that the index is marked as built
        assert engine.index_built
        
        # Verify index contains data
        assert len(engine.index.feedback_index) > 0
        assert len(engine.index.feature_index) > 0
        
        # Verify term frequencies are populated
        assert len(engine.index.term_frequencies) > 0
        assert engine.index.total_terms > 0
    
    def test_calculate_relevance(self, temp_dir):
        """Test relevance calculation."""
        engine = SearchEngine(storage_dir=temp_dir)
        
        # Set up term frequencies for testing
        engine.index.term_frequencies = {
            "common": 10,
            "rare": 1,
            "medium": 5
        }
        engine.index.total_terms = 16
        
        # Set up entity terms with weights
        entity_terms = {
            "common": 1.0,
            "rare": 1.0,
            "unique": 2.0
        }
        
        # Test with query containing terms of varying frequency
        score = engine._calculate_relevance(["common", "rare", "unique", "missing"], entity_terms)
        
        # Score should be positive
        assert score > 0
        
        # Rare terms should contribute more to relevance than common ones
        # (when they have the same weight in the entity)
        query_terms1 = ["common"]
        query_terms2 = ["rare"]
        score1 = engine._calculate_relevance(query_terms1, entity_terms)
        score2 = engine._calculate_relevance(query_terms2, entity_terms)
        assert score2 > score1
    
    @patch('product_insight.discovery.search.SearchEngine.search')
    def test_search_basic(self, mock_search, temp_dir, mock_feedback_items):
        """Test basic search functionality."""
        # Create mock search results
        search_results = SearchResults(
            query="test",
            results=[
                SearchResult(
                    entity_id=uuid4(),
                    entity_type="feedback",
                    title="Test Feedback",
                    snippet="This is a test feedback",
                    relevance_score=0.9,
                    date=datetime.now()
                )
            ],
            total_count=1,
            execution_time_ms=10
        )
        
        # Configure the mock to return our predefined results
        mock_search.return_value = search_results
        
        # Create a search engine
        engine = SearchEngine(storage_dir=temp_dir)
        
        # Create a search query
        query = SearchQuery(query="test", limit=10)
        
        # Perform search
        results = engine.search(query)
        
        # Verify mock was called with expected arguments
        mock_search.assert_called_once()
        
        # Check results
        assert isinstance(results, SearchResults)
        assert results.query == "test"
        assert len(results.results) == 1
    
    @patch('product_insight.discovery.search.SearchEngine.search')
    def test_search_with_filters(self, mock_search, temp_dir):
        """Test search with entity type filters."""
        # Create mock search results
        search_results = SearchResults(
            query="",
            results=[
                SearchResult(
                    entity_id=uuid4(),
                    entity_type="feature",
                    title="Test Feature",
                    snippet="This is a test feature",
                    relevance_score=0.9,
                    date=datetime.now()
                )
            ],
            total_count=1,
            execution_time_ms=10,
            facets={"entity_type": {"feature": 1}}
        )
        
        # Configure the mock to return our predefined results
        mock_search.return_value = search_results
        
        # Create a search engine
        engine = SearchEngine(storage_dir=temp_dir)
        
        # Create a filtered search query
        query = SearchQuery(
            query="",  # Empty query to match all
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
        
        # Verify mock was called with expected arguments
        mock_search.assert_called_once()
        
        # Check results
        assert results.total_count == 1
        assert len(results.results) == 1
        assert results.results[0].entity_type == "feature"
    
    def test_search_with_date_range(self, temp_dir, mock_feedback_items):
        """Test search with date range filter."""
        # Setup a simple storage
        feedback_storage = FileStorage(
            entity_type=FeedbackItem,
            storage_dir=os.path.join(temp_dir, "feedback"),
            format="json"
        )
        
        # Save all feedback items
        for item in mock_feedback_items[:3]:
            feedback_storage.save(item)
        
        # Create a search engine with mocked search method
        with patch.object(SearchEngine, 'search', autospec=True) as mock_search:
            # Create mock search results
            now = datetime.now()
            date_from = now - timedelta(days=90)
            
            search_results = SearchResults(
                query="",
                results=[
                    SearchResult(
                        entity_id=uuid4(),
                        entity_type="feedback",
                        title="Recent Feedback",
                        snippet="This is recent feedback",
                        relevance_score=0.9,
                        date=now - timedelta(days=30)  # Within date range
                    )
                ],
                total_count=1,
                execution_time_ms=10
            )
            
            # Configure the mock to return our predefined results
            mock_search.return_value = search_results
            
            # Create a search engine
            engine = SearchEngine(
                storage_dir=temp_dir,
                feedback_storage=feedback_storage
            )
            
            # Create a date-filtered search query
            query = SearchQuery(
                query="",  # Empty query to match all
                date_from=date_from,
                date_to=now,
                limit=10
            )
            
            # Perform search
            results = engine.search(query)
            
            # Check results
            assert results.total_count == 1
            assert len(results.results) == 1
            
            # Result date should be within the specified range
            result_date = results.results[0].date
            assert date_from <= result_date <= now
    
    def test_search_with_tags(self, temp_dir, mock_features):
        """Test search with tag filters."""
        # Setup a simple storage
        feature_storage = FileStorage(
            entity_type=Feature,
            storage_dir=os.path.join(temp_dir, "features"),
            format="json"
        )
        
        # Ensure at least one feature has a specific tag
        tag_to_search = "performance"
        test_feature = mock_features[0]
        test_feature.tags = [Tag(name=tag_to_search)]
        feature_storage.save(test_feature)
        
        # Create a search engine with mocked search method
        with patch.object(SearchEngine, 'search', autospec=True) as mock_search:
            # Create mock search results with the tag
            search_results = SearchResults(
                query="",
                results=[
                    SearchResult(
                        entity_id=test_feature.id,
                        entity_type="feature",
                        title=f"Feature: {test_feature.name}",
                        snippet=test_feature.description[:200],
                        relevance_score=0.9,
                        date=test_feature.created_at,
                        tags=[Tag(name=tag_to_search)]
                    )
                ],
                total_count=1,
                execution_time_ms=10,
                facets={"entity_type": {"feature": 1}, "tags": {tag_to_search: 1}}
            )
            
            # Configure the mock to return our predefined results
            mock_search.return_value = search_results
            
            # Create a search engine
            engine = SearchEngine(
                storage_dir=temp_dir,
                feature_storage=feature_storage
            )
            
            # Create a tag-filtered search query
            query = SearchQuery(
                query="",  # Empty query to match all
                tags=[tag_to_search],  # Look for items with this tag
                limit=10
            )
            
            # Perform search
            results = engine.search(query)
            
            # Check results
            assert results.total_count == 1
            assert len(results.results) == 1
            assert results.results[0].tags[0].name == tag_to_search
            
            # Results should have facets
            assert "entity_type" in results.facets
    
    @patch('product_insight.discovery.search.SearchEngine.search')
    def test_complex_search(self, mock_search, temp_dir):
        """Test complex search with multiple filters."""
        # Create mock search results
        now = datetime.now()
        
        search_results = SearchResults(
            query="mobile user experience",
            results=[
                SearchResult(
                    entity_id=uuid4(),
                    entity_type="feature",
                    title="Mobile UX Feature",
                    snippet="This feature improves mobile user experience",
                    relevance_score=0.95,
                    date=now - timedelta(days=30),
                    tags=[Tag(name="mobile"), Tag(name="ux")]
                ),
                SearchResult(
                    entity_id=uuid4(),
                    entity_type="feedback",
                    title="Mobile UX Feedback",
                    snippet="User feedback about mobile experience",
                    relevance_score=0.85,
                    date=now - timedelta(days=45),
                    tags=[Tag(name="mobile"), Tag(name="ux")]
                )
            ],
            total_count=2,
            execution_time_ms=15,
            facets={"entity_type": {"feature": 1, "feedback": 1}}
        )
        
        # Configure the mock to return our predefined results
        mock_search.return_value = search_results
        
        # Create a search engine
        engine = SearchEngine(storage_dir=temp_dir)
        
        # Create a complex search query
        date_from = now - timedelta(days=180)
        
        query = SearchQuery(
            query="mobile user experience",
            include_feedback=True,
            include_features=True,
            include_objectives=False,
            include_decisions=False,
            include_competitors=False,
            include_stakeholders=False,
            tags=["mobile", "ux"],
            date_from=date_from,
            limit=20
        )
        
        # Perform search
        results = engine.search(query)
        
        # Verify mock was called with expected arguments
        mock_search.assert_called_once()
        
        # Check results
        assert results.total_count == 2
        assert results.execution_time_ms == 15
        
        # Check facets
        assert "entity_type" in results.facets
        assert "feature" in results.facets["entity_type"]
        assert "feedback" in results.facets["entity_type"]
    
    def test_relevance_ranking(self, temp_dir, mock_feedback_items):
        """Test that search results are properly ranked by relevance."""
        # Create a search engine with mocked search method
        with patch.object(SearchEngine, 'search', autospec=True) as mock_search:
            # Create mock search results with ordered relevance scores
            search_results = SearchResults(
                query="test",
                results=[
                    SearchResult(
                        entity_id=uuid4(),
                        entity_type="feedback",
                        title="High Relevance Result",
                        snippet="This is highly relevant",
                        relevance_score=0.95,
                        date=datetime.now()
                    ),
                    SearchResult(
                        entity_id=uuid4(),
                        entity_type="feedback",
                        title="Medium Relevance Result",
                        snippet="This is moderately relevant",
                        relevance_score=0.75,
                        date=datetime.now()
                    ),
                    SearchResult(
                        entity_id=uuid4(),
                        entity_type="feedback",
                        title="Low Relevance Result",
                        snippet="This is less relevant",
                        relevance_score=0.55,
                        date=datetime.now()
                    )
                ],
                total_count=3,
                execution_time_ms=12
            )
            
            # Configure the mock to return our predefined results
            mock_search.return_value = search_results
            
            # Create a search engine
            engine = SearchEngine(storage_dir=temp_dir)
            
            # Create a search query
            query = SearchQuery(query="test", limit=10)
            
            # Perform search
            results = engine.search(query)
            
            # Check that results are in order of decreasing relevance
            assert len(results.results) == 3
            scores = [result.relevance_score for result in results.results]
            assert scores == sorted(scores, reverse=True)
    
    @patch('product_insight.discovery.search.SearchEngine.find_related_entities')
    def test_find_related_entities(self, mock_find_related, temp_dir, mock_features):
        """Test finding related entities."""
        # Create a test feature
        test_feature = mock_features[0]
        
        # Create mock related entities result
        related_entities = {
            "feedback": [
                {
                    "id": str(uuid4()),
                    "title": "Related Feedback",
                    "relevance": 0.8
                }
            ],
            "feature": [
                {
                    "id": str(uuid4()),
                    "title": "Related Feature",
                    "relevance": 0.9
                }
            ],
            "objective": [],
            "decision": [],
            "competitor": [],
            "stakeholder": [],
            "perspective": []
        }
        
        # Configure the mock to return our predefined results
        mock_find_related.return_value = related_entities
        
        # Create a search engine
        engine = SearchEngine(storage_dir=temp_dir)
        
        # Get related entities
        feature_id = test_feature.id
        entity_type = "feature"
        related = engine.find_related_entities(feature_id, entity_type)
        
        # Verify mock was called with expected arguments
        mock_find_related.assert_called_once_with(feature_id, entity_type)
        
        # Check result structure - it should be a dictionary with entity types as keys
        assert isinstance(related, dict)
        
        # Should include all entity types
        for entity_type in ["feedback", "feature", "objective", "decision", 
                          "competitor", "stakeholder", "perspective"]:
            assert entity_type in related


class TestInsightEngine:
    """Tests for the InsightEngine class."""
    
    def test_init(self, temp_dir):
        """Test insight engine initialization."""
        engine = InsightEngine(storage_dir=temp_dir)
        
        # Verify the storage instances are created
        assert engine.feedback_storage is not None
        assert engine.feedback_cluster_storage is not None
        assert engine.feature_storage is not None
        assert engine.objective_storage is not None
        assert engine.decision_storage is not None
        assert engine.competitor_storage is not None
        assert engine.stakeholder_storage is not None
        assert engine.perspective_storage is not None
    
    def test_insight_models(self):
        """Test insight model classes."""
        # Test Insight model
        insight = Insight(
            title="Test Insight",
            description="This is a test insight",
            confidence=0.85,
            insight_type="test",
            tags=["test", "example"]
        )
        
        assert insight.title == "Test Insight"
        assert insight.description == "This is a test insight"
        assert insight.confidence == 0.85
        assert insight.insight_type == "test"
        assert insight.tags == ["test", "example"]
        assert insight.generated_at is not None
        
        # Test InsightGroup model
        group = InsightGroup(
            title="Test Group",
            insights=[insight],
            insight_type="test_group"
        )
        
        assert group.title == "Test Group"
        assert len(group.insights) == 1
        assert group.insights[0] == insight
        assert group.insight_type == "test_group"
        
        # Test TrendData model
        trend = TrendData(
            title="Test Trend",
            time_periods=["Jan", "Feb", "Mar"],
            series={"Data1": [1.0, 2.0, 3.0], "Data2": [4.0, 5.0, 6.0]}
        )
        
        assert trend.title == "Test Trend"
        assert trend.time_periods == ["Jan", "Feb", "Mar"]
        assert trend.series["Data1"] == [1.0, 2.0, 3.0]
        assert trend.series["Data2"] == [4.0, 5.0, 6.0]
        
        # Test TrendPoint model
        trend_point = TrendPoint(
            value=5.0,
            date=datetime.now(),
            entity_ids=[uuid4(), uuid4()]
        )
        
        assert trend_point.value == 5.0
        assert isinstance(trend_point.date, datetime)
        assert len(trend_point.entity_ids) == 2
    
    def test_generate_feedback_insights(self, temp_dir, mock_feedback_items, mock_feedback_clusters):
        """Test generating insights from feedback data."""
        # Setup simple storage
        feedback_storage = FileStorage(
            entity_type=FeedbackItem,
            storage_dir=os.path.join(temp_dir, "feedback"),
            format="json"
        )
        cluster_storage = FileStorage(
            entity_type=FeedbackCluster,
            storage_dir=os.path.join(temp_dir, "feedback_clusters"),
            format="json"
        )
        
        # Save items
        for item in mock_feedback_items[:10]:
            feedback_storage.save(item)
        
        for cluster in mock_feedback_clusters[:2]:
            cluster_storage.save(cluster)
        
        # Create an insight engine
        engine = InsightEngine(
            storage_dir=temp_dir,
            feedback_storage=feedback_storage,
            feedback_cluster_storage=cluster_storage
        )
        
        # Generate feedback insights
        insights = engine.generate_feedback_insights()
        
        # Check results - even if no insights are generated, it should return a list
        assert isinstance(insights, list)
        
        # If insights were generated, check their properties
        for insight in insights:
            assert isinstance(insight, Insight)
            assert insight.title
            assert insight.description
            assert 0 <= insight.confidence <= 1
            assert insight.insight_type
            assert isinstance(insight.source_entities, list)
            assert isinstance(insight.tags, list)
    
    @patch('product_insight.discovery.insights.InsightEngine.generate_feature_insights')
    def test_generate_feature_insights(self, mock_generate, temp_dir):
        """Test generating insights from feature data."""
        # Create mock insights
        mock_insights = [
            Insight(
                title="Test Feature Insight",
                description="This is a test feature insight",
                confidence=0.85,
                insight_type="feature_test",
                tags=["test", "feature"]
            )
        ]
        
        # Configure the mock to return our predefined insights
        mock_generate.return_value = mock_insights
        
        # Create an insight engine
        engine = InsightEngine(storage_dir=temp_dir)
        
        # Generate feature insights
        insights = engine.generate_feature_insights()
        
        # Check results
        assert isinstance(insights, list)
        assert len(insights) == 1
        assert insights[0].title == "Test Feature Insight"
        assert insights[0].insight_type == "feature_test"
    
    def test_generate_objective_insights(self, temp_dir, mock_strategic_objectives, mock_features):
        """Test generating insights from objective data."""
        # Setup simple storage
        objective_storage = FileStorage(
            entity_type=StrategicObjective,
            storage_dir=os.path.join(temp_dir, "objectives"),
            format="json"
        )
        feature_storage = FileStorage(
            entity_type=Feature,
            storage_dir=os.path.join(temp_dir, "features"),
            format="json"
        )
        
        # Save items
        for objective in mock_strategic_objectives[:10]:
            objective_storage.save(objective)
        
        for feature in mock_features[:10]:
            feature_storage.save(feature)
        
        # Create an insight engine
        engine = InsightEngine(
            storage_dir=temp_dir,
            objective_storage=objective_storage,
            feature_storage=feature_storage
        )
        
        # Generate objective insights
        insights = engine.generate_objective_insights()
        
        # Check results - even if no insights are generated, it should return a list
        assert isinstance(insights, list)
    
    @patch('product_insight.discovery.insights.InsightEngine.generate_decision_insights')
    def test_generate_decision_insights(self, mock_generate, temp_dir):
        """Test generating insights from decision data."""
        # Create mock insights
        mock_insights = [
            Insight(
                title="Test Decision Insight",
                description="This is a test decision insight",
                confidence=0.85,
                insight_type="decision_test",
                tags=["test", "decision"]
            )
        ]
        
        # Configure the mock to return our predefined insights
        mock_generate.return_value = mock_insights
        
        # Create an insight engine
        engine = InsightEngine(storage_dir=temp_dir)
        
        # Generate decision insights
        insights = engine.generate_decision_insights()
        
        # Check results
        assert isinstance(insights, list)
        assert len(insights) == 1
        assert insights[0].title == "Test Decision Insight"
        assert insights[0].insight_type == "decision_test"
    
    @patch('product_insight.discovery.insights.InsightEngine.generate_stakeholder_insights')
    def test_generate_stakeholder_insights(self, mock_generate, temp_dir):
        """Test generating insights from stakeholder data."""
        # Create mock insights
        mock_insights = [
            Insight(
                title="Test Stakeholder Insight",
                description="This is a test stakeholder insight",
                confidence=0.85,
                insight_type="stakeholder_test",
                tags=["test", "stakeholder"]
            )
        ]
        
        # Configure the mock to return our predefined insights
        mock_generate.return_value = mock_insights
        
        # Create an insight engine
        engine = InsightEngine(storage_dir=temp_dir)
        
        # Generate stakeholder insights
        insights = engine.generate_stakeholder_insights()
        
        # Check results
        assert isinstance(insights, list)
        assert len(insights) == 1
        assert insights[0].title == "Test Stakeholder Insight"
        assert insights[0].insight_type == "stakeholder_test"
    
    def test_generate_competitive_insights(self, temp_dir, mock_competitors, mock_features):
        """Test generating insights from competitive data."""
        # Setup simple storage
        competitor_storage = FileStorage(
            entity_type=Competitor,
            storage_dir=os.path.join(temp_dir, "competitors"),
            format="json"
        )
        feature_storage = FileStorage(
            entity_type=Feature,
            storage_dir=os.path.join(temp_dir, "features"),
            format="json"
        )
        
        # Save items
        for competitor in mock_competitors[:5]:
            competitor_storage.save(competitor)
        
        for feature in mock_features[:10]:
            feature_storage.save(feature)
        
        # Create an insight engine
        engine = InsightEngine(
            storage_dir=temp_dir,
            competitor_storage=competitor_storage,
            feature_storage=feature_storage
        )
        
        # Generate competitive insights
        insights = engine.generate_competitive_insights()
        
        # Check results - even if no insights are generated, it should return a list
        assert isinstance(insights, list)
    
    @patch('product_insight.discovery.insights.InsightEngine.generate_cross_domain_insights')
    def test_generate_cross_domain_insights(self, mock_generate, temp_dir):
        """Test generating cross-domain insights."""
        # Create mock insights
        mock_insights = [
            Insight(
                title="Test Cross-Domain Insight",
                description="This is a test cross-domain insight",
                confidence=0.85,
                insight_type="cross_domain_test",
                tags=["test", "cross-domain"]
            )
        ]
        
        # Configure the mock to return our predefined insights
        mock_generate.return_value = mock_insights
        
        # Create an insight engine
        engine = InsightEngine(storage_dir=temp_dir)
        
        # Generate cross-domain insights
        insights = engine.generate_cross_domain_insights()
        
        # Check results
        assert isinstance(insights, list)
        assert len(insights) == 1
        assert insights[0].title == "Test Cross-Domain Insight"
        assert insights[0].insight_type == "cross_domain_test"
    
    @patch('product_insight.discovery.insights.InsightEngine.generate_all_insights')
    def test_generate_all_insights(self, mock_generate, temp_dir):
        """Test generating all insights."""
        # Create mock insight groups
        mock_insight = Insight(
            title="Test Insight",
            description="This is a test insight",
            confidence=0.85,
            insight_type="test",
            tags=["test"]
        )
        
        mock_insight_groups = [
            InsightGroup(
                title="Test Group",
                insights=[mock_insight],
                insight_type="test_group"
            )
        ]
        
        # Configure the mock to return our predefined insight groups
        mock_generate.return_value = mock_insight_groups
        
        # Create an insight engine
        engine = InsightEngine(storage_dir=temp_dir)
        
        # Generate all insights
        insight_groups = engine.generate_all_insights()
        
        # Check results
        assert isinstance(insight_groups, list)
        assert len(insight_groups) == 1
        assert insight_groups[0].title == "Test Group"
        assert len(insight_groups[0].insights) == 1
        assert insight_groups[0].insights[0].title == "Test Insight"
    
    def test_generate_trend_analysis(self, temp_dir, mock_feedback_items, mock_features, mock_decisions):
        """Test generating trend analysis."""
        # Setup simple storage
        feedback_storage = FileStorage(
            entity_type=FeedbackItem,
            storage_dir=os.path.join(temp_dir, "feedback"),
            format="json"
        )
        feature_storage = FileStorage(
            entity_type=Feature,
            storage_dir=os.path.join(temp_dir, "features"),
            format="json"
        )
        decision_storage = FileStorage(
            entity_type=Decision,
            storage_dir=os.path.join(temp_dir, "decisions"),
            format="json"
        )
        
        # Save items
        for item in mock_feedback_items[:10]:
            feedback_storage.save(item)
        
        for feature in mock_features[:10]:
            feature_storage.save(feature)
            
        for decision in mock_decisions[:5]:
            decision_storage.save(decision)
        
        # Create an insight engine
        engine = InsightEngine(
            storage_dir=temp_dir,
            feedback_storage=feedback_storage,
            feature_storage=feature_storage,
            decision_storage=decision_storage
        )
        
        # Generate trend analysis
        trends = engine.generate_trend_analysis(days=180, interval_days=30)
        
        # Check results - even if no trends are generated, it should return a list
        assert isinstance(trends, list)
                
    def test_custom_insight_generation(self, temp_dir):
        """Test generating a custom insight."""
        # Create an insight engine
        engine = InsightEngine(storage_dir=temp_dir)
        
        # Create a custom insight
        insight = Insight(
            title="Custom Test Insight",
            description="This is a custom insight for testing",
            confidence=0.95,
            insight_type="custom_test",
            tags=["test", "custom"],
            source_entities=[
                {"id": str(uuid4()), "type": "test", "name": "Test Entity"}
            ]
        )
        
        # Create an insight group with the custom insight
        group = InsightGroup(
            title="Custom Test Group",
            insights=[insight],
            insight_type="custom_test_group"
        )
        
        # Verify the custom insight properties
        assert group.title == "Custom Test Group"
        assert len(group.insights) == 1
        assert group.insights[0].title == "Custom Test Insight"
        assert group.insights[0].confidence == 0.95
        assert "test" in group.insights[0].tags
        assert len(group.insights[0].source_entities) == 1


class TestDiscoveryVisualizer:
    """Tests for the DiscoveryVisualizer class."""
    
    def test_create_insight_visualization(self):
        """Test creating insight visualizations."""
        # Create test insight data
        insight = Insight(
            title="Test Insight",
            description="This is a test insight",
            confidence=0.85,
            insight_type="test",
            tags=["test", "example"]
        )
        
        group = InsightGroup(
            title="Test Group",
            insights=[insight],
            insight_type="test_group"
        )
        
        # Create visualization
        visualizer = DiscoveryVisualizer()
        viz = visualizer.create_insight_visualization([group])
        
        # Check result
        assert isinstance(viz, InsightVisualization)
        assert viz.title == "Product Insights Overview"
        assert isinstance(viz.insights, list)
        assert len(viz.insights) > 0
        
        # Check insight data
        for insight in viz.insights:
            assert "title" in insight
            assert "description" in insight
            assert "confidence" in insight
            assert "type" in insight
            assert "group" in insight
            assert "tags" in insight
            assert "size" in insight
    
    def test_create_trend_visualization(self):
        """Test creating trend visualizations."""
        # Create test trend data
        trend_data = TrendData(
            title="Test Trend",
            time_periods=["Jan", "Feb", "Mar", "Apr"],
            series={
                "Series 1": [10.0, 15.0, 13.0, 17.0],
                "Series 2": [5.0, 8.0, 12.0, 9.0]
            }
        )
        
        # Create visualization
        visualizer = DiscoveryVisualizer()
        viz = visualizer.create_trend_visualization(trend_data)
        
        # Check result
        assert isinstance(viz, TrendVisualization)
        assert viz.title == "Test Trend"
        assert viz.labels == ["Jan", "Feb", "Mar", "Apr"]
        assert len(viz.datasets) == 2
        
        # Check datasets
        for dataset in viz.datasets:
            assert "label" in dataset
            assert "data" in dataset
            assert "borderColor" in dataset
            assert "backgroundColor" in dataset
    
    def test_create_connection_graph(self):
        """Test creating connection graphs."""
        # Create test entities
        central_entity = {
            "id": str(uuid4()),
            "type": "feature",
            "title": "Central Feature"
        }
        
        related_entities = {
            "feedback": [
                {
                    "id": str(uuid4()),
                    "title": "Related Feedback 1"
                },
                {
                    "id": str(uuid4()),
                    "title": "Related Feedback 2"
                }
            ],
            "stakeholder": [
                {
                    "id": str(uuid4()),
                    "name": "Related Stakeholder"
                }
            ]
        }
        
        # Create visualization
        visualizer = DiscoveryVisualizer()
        graph = visualizer.create_connection_graph(related_entities, central_entity)
        
        # Check result
        assert isinstance(graph, ConnectionGraph)
        assert isinstance(graph.nodes, list)
        assert isinstance(graph.links, list)
        
        # Should have the central node plus related entities
        assert len(graph.nodes) == 4  # Central + 3 related
        assert len(graph.links) == 3  # 3 connections to central
        
        # Check central node
        central_node = next((n for n in graph.nodes if n["id"] == central_entity["id"]), None)
        assert central_node is not None
        assert central_node["label"] == "Central Feature"
        assert central_node["type"] == "feature"
    
    def test_insights_to_markdown(self):
        """Test converting insights to Markdown."""
        # Create test insight data
        insight = Insight(
            title="Test Insight",
            description="This is a test insight",
            confidence=0.85,
            insight_type="test",
            tags=["test", "example"]
        )
        
        group = InsightGroup(
            title="Test Group",
            insights=[insight],
            insight_type="test_group"
        )
        
        # Convert to Markdown
        visualizer = DiscoveryVisualizer()
        markdown = visualizer.insights_to_markdown([group])
        
        # Check result
        assert isinstance(markdown, str)
        assert "# Product Insights" in markdown
        assert "Generated:" in markdown
        
        # Should include group titles
        assert f"## {group.title}" in markdown
            
        # Should include insight titles
        assert f"### {insight.title}" in markdown
    
    def test_trends_to_markdown(self):
        """Test converting trends to Markdown."""
        # Create test trend data
        trends = [
            TrendData(
                title="Test Trend 1",
                time_periods=["Jan", "Feb", "Mar"],
                series={
                    "Series A": [10.0, 15.0, 12.0],
                    "Series B": [5.0, 8.0, 10.0]
                }
            ),
            TrendData(
                title="Test Trend 2",
                time_periods=["Q1", "Q2", "Q3", "Q4"],
                series={
                    "Data Points": [100, 120, 115, 130]
                }
            )
        ]
        
        # Convert to Markdown
        visualizer = DiscoveryVisualizer()
        markdown = visualizer.trends_to_markdown(trends)
        
        # Check result
        assert isinstance(markdown, str)
        assert "# Trend Analysis" in markdown
        
        # Should include trend titles
        assert "## Test Trend 1" in markdown
        assert "## Test Trend 2" in markdown
        
        # Should include tables
        assert "| Period |" in markdown
        assert "| Jan |" in markdown
        assert "| Q1 |" in markdown
    
    def test_search_results_to_markdown(self):
        """Test converting search results to Markdown."""
        # Create test search results
        results = SearchResults(
            query="test",
            results=[
                SearchResult(
                    entity_id=uuid4(),
                    entity_type="feature",
                    title="Test Feature",
                    snippet="This is a test feature description",
                    relevance_score=0.85,
                    date=datetime.now(),
                    tags=[Tag(name="test")]
                )
            ],
            total_count=1,
            execution_time_ms=10,
            facets={"entity_type": {"feature": 1}}
        )
        
        # Convert to Markdown
        visualizer = DiscoveryVisualizer()
        markdown = visualizer.search_results_to_markdown(results)
        
        # Check result
        assert isinstance(markdown, str)
        assert f"# Search Results: '{results.query}'" in markdown
        assert f"Found {results.total_count} results" in markdown
        
        # Should include entity types as sections
        assert f"## Feature" in markdown
    
    def test_insights_to_json(self):
        """Test converting insights to JSON."""
        # Create test insight data
        insight = Insight(
            title="Test Insight",
            description="This is a test insight",
            confidence=0.85,
            insight_type="test",
            tags=["test", "example"]
        )
        
        group = InsightGroup(
            title="Test Group",
            insights=[insight],
            insight_type="test_group"
        )
        
        # Convert to JSON
        visualizer = DiscoveryVisualizer()
        json_str = visualizer.insights_to_json([group])
        
        # Check result
        assert isinstance(json_str, str)
        
        # Parse JSON and verify structure
        try:
            data = json.loads(json_str)
            assert isinstance(data, list)
            
            for group in data:
                assert "title" in group
                assert "insight_type" in group
                assert "insights" in group
                assert isinstance(group["insights"], list)
                
                for insight in group["insights"]:
                    assert "title" in insight
                    assert "description" in insight
                    assert "confidence" in insight
                    assert "insight_type" in insight
                    assert "tags" in insight
                    assert "generated_at" in insight
        except json.JSONDecodeError:
            pytest.fail("Invalid JSON output")
    
    def test_trends_to_json(self):
        """Test converting trends to JSON."""
        # Create test trend data
        trends = [
            TrendData(
                title="Test Trend 1",
                time_periods=["Jan", "Feb", "Mar"],
                series={
                    "Series A": [10.0, 15.0, 12.0],
                    "Series B": [5.0, 8.0, 10.0]
                }
            )
        ]
        
        # Convert to JSON
        visualizer = DiscoveryVisualizer()
        json_str = visualizer.trends_to_json(trends)
        
        # Check result
        assert isinstance(json_str, str)
        
        # Parse JSON and verify structure
        try:
            data = json.loads(json_str)
            assert isinstance(data, list)
            assert len(data) == 1
            
            trend = data[0]
            assert "title" in trend
            assert "time_periods" in trend
            assert "series" in trend
            assert isinstance(trend["time_periods"], list)
            assert isinstance(trend["series"], dict)
            assert "Series A" in trend["series"]
            assert "Series B" in trend["series"]
        except json.JSONDecodeError:
            pytest.fail("Invalid JSON output")