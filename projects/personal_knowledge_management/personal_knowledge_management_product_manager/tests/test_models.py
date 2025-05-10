"""
Tests for the data models.

This module tests the Pydantic data models used in the ProductInsight system.
"""

import json
from datetime import datetime, timedelta
from uuid import UUID, uuid4

import pytest

from product_insight.models import (
    Competitor,
    Decision,
    Feature,
    FeedbackCluster,
    FeedbackItem,
    InfluenceEnum,
    MetricTypeEnum,
    PriorityEnum,
    PriorityScoreCard,
    SearchQuery,
    SearchResult,
    SearchResults,
    SentimentEnum,
    SourceEnum,
    Stakeholder,
    StakeholderPerspective,
    StakeholderRoleEnum,
    StatusEnum,
    StrategicObjective,
    Tag,
)


class TestBaseModels:
    """Tests for base model functionality."""
    
    def test_tag_model(self):
        """Test the Tag model."""
        # Create a tag
        tag = Tag(name="test", color="#FF0000")
        
        # Check properties
        assert tag.name == "test"
        assert tag.color == "#FF0000"
        
        # Test serialization
        tag_dict = tag.model_dump()
        assert tag_dict["name"] == "test"
        assert tag_dict["color"] == "#FF0000"
        
        # Test JSON serialization
        tag_json = tag.model_dump_json()
        tag_data = json.loads(tag_json)
        assert tag_data["name"] == "test"
        assert tag_data["color"] == "#FF0000"


class TestFeedbackModels:
    """Tests for feedback-related models."""
    
    def test_feedback_item_model(self):
        """Test the FeedbackItem model."""
        # Create a feedback item
        feedback = FeedbackItem(
            content="This is test feedback",
            source=SourceEnum.CUSTOMER_INTERVIEW,
            sentiment=SentimentEnum.POSITIVE,
            tags=[Tag(name="test", color="#FF0000")],
            source_id="SRC-1234",
            customer_id="CUST-5678",
            customer_segment="Enterprise",
            processed=True,
            extracted_features=["feature1", "feature2"],
            impact_score=0.75
        )
        
        # Check properties
        assert feedback.content == "This is test feedback"
        assert feedback.source == SourceEnum.CUSTOMER_INTERVIEW
        assert feedback.sentiment == SentimentEnum.POSITIVE
        assert len(feedback.tags) == 1
        assert feedback.tags[0].name == "test"
        assert feedback.source_id == "SRC-1234"
        assert feedback.customer_id == "CUST-5678"
        assert feedback.customer_segment == "Enterprise"
        assert feedback.processed is True
        assert feedback.extracted_features == ["feature1", "feature2"]
        assert feedback.impact_score == 0.75
        
        # Check UUID and timestamps
        assert isinstance(feedback.id, UUID)
        assert isinstance(feedback.created_at, datetime)
        assert isinstance(feedback.updated_at, datetime)
    
    def test_feedback_cluster_model(self):
        """Test the FeedbackCluster model."""
        # Create feedback IDs
        feedback_ids = [uuid4() for _ in range(3)]
        
        # Create a feedback cluster
        cluster = FeedbackCluster(
            name="Test Cluster",
            description="This is a test cluster",
            feedback_ids=feedback_ids,
            tags=[Tag(name="test", color="#FF0000")],
            central_theme="Central Theme",
            sentiment_summary=SentimentEnum.POSITIVE,
            impact_score=0.8,
            feature_requests=[uuid4(), uuid4()]
        )
        
        # Check properties
        assert cluster.name == "Test Cluster"
        assert cluster.description == "This is a test cluster"
        assert len(cluster.feedback_ids) == 3
        assert len(cluster.tags) == 1
        assert cluster.central_theme == "Central Theme"
        assert cluster.sentiment_summary == SentimentEnum.POSITIVE
        assert cluster.volume == 3  # Automatically set based on feedback_ids
        assert cluster.impact_score == 0.8
        assert len(cluster.feature_requests) == 2


class TestObjectiveModels:
    """Tests for objective-related models."""
    
    def test_strategic_objective_model(self):
        """Test the StrategicObjective model."""
        # Create a strategic objective
        objective = StrategicObjective(
            name="Test Objective",
            description="This is a test objective",
            metric_type=MetricTypeEnum.ADOPTION,
            metric_target=100.0,
            metric_current=50.0,
            timeframe_start=datetime.now(),
            timeframe_end=datetime.now() + timedelta(days=90),
            status=StatusEnum.IN_PROGRESS,
            priority=PriorityEnum.HIGH,
            tags=[Tag(name="test", color="#FF0000")]
        )
        
        # Check properties
        assert objective.name == "Test Objective"
        assert objective.description == "This is a test objective"
        assert objective.metric_type == MetricTypeEnum.ADOPTION
        assert objective.metric_target == 100.0
        assert objective.metric_current == 50.0
        assert isinstance(objective.timeframe_start, datetime)
        assert isinstance(objective.timeframe_end, datetime)
        assert objective.status == StatusEnum.IN_PROGRESS
        assert objective.priority == PriorityEnum.HIGH
        assert len(objective.tags) == 1
        
        # Check relationships
        assert objective.parent_id is None
        assert len(objective.child_ids) == 0
        assert len(objective.stakeholder_ids) == 0
        assert len(objective.feature_ids) == 0


class TestFeatureModels:
    """Tests for feature-related models."""
    
    def test_feature_model(self):
        """Test the Feature model."""
        # Create a feature
        feature = Feature(
            name="Test Feature",
            description="This is a test feature",
            status=StatusEnum.PLANNED,
            effort_estimate=5.0,
            value_estimate=8.0,
            priority_score=0.7,
            priority_method="weighted",
            tags=[Tag(name="test", color="#FF0000")]
        )
        
        # Check properties
        assert feature.name == "Test Feature"
        assert feature.description == "This is a test feature"
        assert feature.status == StatusEnum.PLANNED
        assert feature.effort_estimate == 5.0
        assert feature.value_estimate == 8.0
        assert feature.priority_score == 0.7
        assert feature.priority_method == "weighted"
        assert len(feature.tags) == 1
        
        # Check relationships
        assert len(feature.objective_ids) == 0
        assert len(feature.feedback_ids) == 0
        assert len(feature.feedback_cluster_ids) == 0
        assert len(feature.stakeholder_ids) == 0
        assert len(feature.dependencies) == 0
    
    def test_priority_scorecard_model(self):
        """Test the PriorityScoreCard model."""
        feature_id = uuid4()
        
        # Create a priority scorecard
        scorecard = PriorityScoreCard(
            feature_id=feature_id,
            rice_score=5.2,
            value_effort_score=1.6,
            strategic_alignment_score=0.8,
            customer_value_score=0.7,
            innovation_score=0.5,
            risk_score=0.3,
            total_score=0.75,
            custom_scores={"kano": 0.6}
        )
        
        # Check properties
        assert scorecard.feature_id == feature_id
        assert scorecard.rice_score == 5.2
        assert scorecard.value_effort_score == 1.6
        assert scorecard.strategic_alignment_score == 0.8
        assert scorecard.customer_value_score == 0.7
        assert scorecard.innovation_score == 0.5
        assert scorecard.risk_score == 0.3
        assert scorecard.total_score == 0.75
        assert scorecard.custom_scores["kano"] == 0.6


class TestDecisionModels:
    """Tests for decision-related models."""
    
    def test_decision_model(self):
        """Test the Decision model."""
        decision_date = datetime.now() - timedelta(days=30)
        stakeholder_ids = [uuid4(), uuid4()]
        
        # Create a decision
        decision = Decision(
            title="Test Decision",
            description="This is a test decision",
            context="Context for the decision",
            rationale="Rationale for the decision",
            alternatives=["Alternative 1", "Alternative 2"],
            decision_date=decision_date,
            decided_by=stakeholder_ids,
            tags=[Tag(name="test", color="#FF0000")]
        )
        
        # Check properties
        assert decision.title == "Test Decision"
        assert decision.description == "This is a test decision"
        assert decision.context == "Context for the decision"
        assert decision.rationale == "Rationale for the decision"
        assert decision.alternatives == ["Alternative 1", "Alternative 2"]
        assert decision.decision_date == decision_date
        assert decision.decided_by == stakeholder_ids
        assert len(decision.tags) == 1
        
        # Check relationships and optional fields
        assert len(decision.stakeholder_input) == 0
        assert len(decision.feature_ids) == 0
        assert len(decision.objective_ids) == 0
        assert len(decision.supporting_data) == 0
        assert decision.outcome_notes is None
        assert decision.outcome_date is None
        assert decision.retrospective is None


class TestStakeholderModels:
    """Tests for stakeholder-related models."""
    
    def test_stakeholder_model(self):
        """Test the Stakeholder model."""
        # Create a stakeholder
        stakeholder = Stakeholder(
            name="Test Stakeholder",
            role=StakeholderRoleEnum.PRODUCT,
            organization="Test Org",
            email="test@example.com",
            influence=InfluenceEnum.HIGH,
            key_concerns=["Concern 1", "Concern 2"],
            engagement_history=["[2023-01-01 10:00] Meeting: Discussed features"]
        )
        
        # Check properties
        assert stakeholder.name == "Test Stakeholder"
        assert stakeholder.role == StakeholderRoleEnum.PRODUCT
        assert stakeholder.organization == "Test Org"
        assert stakeholder.email == "test@example.com"
        assert stakeholder.influence == InfluenceEnum.HIGH
        assert stakeholder.key_concerns == ["Concern 1", "Concern 2"]
        assert stakeholder.engagement_history == ["[2023-01-01 10:00] Meeting: Discussed features"]
        
        # Check relationships and optional fields
        assert len(stakeholder.feature_preferences) == 0
        assert len(stakeholder.objective_alignment) == 0
        assert stakeholder.communication_preferences is None
        assert stakeholder.notes is None
    
    def test_stakeholder_perspective_model(self):
        """Test the StakeholderPerspective model."""
        stakeholder_id = uuid4()
        recorded_date = datetime.now() - timedelta(days=5)
        
        # Create a stakeholder perspective
        perspective = StakeholderPerspective(
            stakeholder_id=stakeholder_id,
            topic="Test Topic",
            perspective="This is a test perspective",
            sentiment=SentimentEnum.POSITIVE,
            date_recorded=recorded_date,
            context="Meeting context"
        )
        
        # Check properties
        assert perspective.stakeholder_id == stakeholder_id
        assert perspective.topic == "Test Topic"
        assert perspective.perspective == "This is a test perspective"
        assert perspective.sentiment == SentimentEnum.POSITIVE
        assert perspective.date_recorded == recorded_date
        assert perspective.context == "Meeting context"
        
        # Check relationships
        assert len(perspective.related_feature_ids) == 0
        assert len(perspective.related_objective_ids) == 0


class TestCompetitorModels:
    """Tests for competitor-related models."""
    
    def test_competitor_model(self):
        """Test the Competitor model."""
        # Create a competitor
        competitor = Competitor(
            name="Test Competitor",
            description="This is a test competitor",
            website="https://example.com",
            market_share=15.0,
            pricing_model="Subscription",
            pricing_details="Basic: $10/mo; Pro: $20/mo",
            target_segments=["Enterprise", "SMB"],
            strengths=["Strength 1", "Strength 2"],
            weaknesses=["Weakness 1", "Weakness 2"],
            feature_comparison={"Feature A": True, "Feature B": False},
            detailed_comparisons={"Feature A": "Their implementation is better"},
            threat_level=0.7,
            tags=[Tag(name="test", color="#FF0000")]
        )
        
        # Check properties
        assert competitor.name == "Test Competitor"
        assert competitor.description == "This is a test competitor"
        assert competitor.website == "https://example.com"
        assert competitor.market_share == 15.0
        assert competitor.pricing_model == "Subscription"
        assert competitor.pricing_details == "Basic: $10/mo; Pro: $20/mo"
        assert competitor.target_segments == ["Enterprise", "SMB"]
        assert competitor.strengths == ["Strength 1", "Strength 2"]
        assert competitor.weaknesses == ["Weakness 1", "Weakness 2"]
        assert competitor.feature_comparison == {"Feature A": True, "Feature B": False}
        assert competitor.detailed_comparisons == {"Feature A": "Their implementation is better"}
        assert competitor.threat_level == 0.7
        assert len(competitor.tags) == 1


class TestSearchModels:
    """Tests for search-related models."""
    
    def test_search_query_model(self):
        """Test the SearchQuery model."""
        # Create a search query
        query = SearchQuery(
            query="test query",
            include_feedback=True,
            include_features=True,
            include_objectives=False,
            include_decisions=False,
            include_competitors=False,
            include_stakeholders=False,
            tags=["tag1", "tag2"],
            limit=10
        )
        
        # Check properties
        assert query.query == "test query"
        assert query.include_feedback is True
        assert query.include_features is True
        assert query.include_objectives is False
        assert query.include_decisions is False
        assert query.include_competitors is False
        assert query.include_stakeholders is False
        assert query.tags == ["tag1", "tag2"]
        assert query.limit == 10
    
    def test_search_result_model(self):
        """Test the SearchResult model."""
        entity_id = uuid4()
        result_date = datetime.now() - timedelta(days=5)
        
        # Create a search result
        result = SearchResult(
            entity_id=entity_id,
            entity_type="feature",
            title="Test Result",
            snippet="This is a search result snippet",
            relevance_score=0.85,
            date=result_date,
            tags=[Tag(name="test", color="#FF0000")]
        )
        
        # Check properties
        assert result.entity_id == entity_id
        assert result.entity_type == "feature"
        assert result.title == "Test Result"
        assert result.snippet == "This is a search result snippet"
        assert result.relevance_score == 0.85
        assert result.date == result_date
        assert len(result.tags) == 1
    
    def test_search_results_model(self):
        """Test the SearchResults model."""
        entity_id = uuid4()
        result_date = datetime.now() - timedelta(days=5)
        
        # Create a search result
        result = SearchResult(
            entity_id=entity_id,
            entity_type="feature",
            title="Test Result",
            snippet="This is a search result snippet",
            relevance_score=0.85,
            date=result_date,
            tags=[Tag(name="test", color="#FF0000")]
        )
        
        # Create search results
        results = SearchResults(
            query="test query",
            results=[result],
            total_count=1,
            execution_time_ms=150,
            facets={"entity_type": {"feature": 1}}
        )
        
        # Check properties
        assert results.query == "test query"
        assert len(results.results) == 1
        assert results.results[0].entity_id == entity_id
        assert results.total_count == 1
        assert results.execution_time_ms == 150
        assert results.facets["entity_type"]["feature"] == 1