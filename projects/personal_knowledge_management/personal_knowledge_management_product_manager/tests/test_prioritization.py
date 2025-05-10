"""
Tests for the prioritization module.

This module tests the feature prioritization functionality of the ProductInsight system.
"""

import os
from uuid import uuid4

import pytest

from product_insight.models import (
    Feature,
    PriorityScoreCard,
    StatusEnum,
)
from product_insight.prioritization import (
    FeaturePrioritizer,
    FeatureScorer,
    KanoCategory,
    PrioritizationCriteria,
    PrioritizationMethod,
    RiceScorer,
    ValueEffortScorer,
    WeightedScorer,
)
from product_insight.storage import FileStorage

from tests.fixtures.fixtures import (
    mock_data_generator,
    mock_features,
    populated_storage_dir,
    temp_dir,
)


class TestScoringModels:
    """Tests for the individual scoring models."""
    
    def test_rice_scorer(self):
        """Test the RICE scoring model."""
        # Create a scorer
        scorer = RiceScorer()
        
        # Calculate a RICE score
        score = scorer.calculate_rice_score(reach=100, impact=2, confidence=0.8, effort=4)
        
        # Check the result
        assert score == (100 * 2 * 0.8) / 4
        assert score == 40.0
        
        # Test with a feature
        feature = Feature(
            name="Test Feature",
            description="Test description",
            feedback_ids=[uuid4() for _ in range(5)],
            feedback_cluster_ids=[uuid4()],
            effort_estimate=3.0,
            value_estimate=8.0
        )
        
        # Score the feature
        score = scorer.score_feature(feature)
        
        # Check the result
        assert score > 0
    
    def test_value_effort_scorer(self):
        """Test the Value/Effort scoring model."""
        # Create a scorer
        scorer = ValueEffortScorer()
        
        # Calculate a Value/Effort score
        score = scorer.calculate_value_effort_score(value=8, effort=4)
        
        # Check the result
        assert score == 8 / 4
        assert score == 2.0
        
        # Test with a feature
        feature = Feature(
            name="Test Feature",
            description="Test description",
            effort_estimate=3.0,
            value_estimate=9.0
        )
        
        # Score the feature
        score = scorer.score_feature(feature)
        
        # Check the result
        assert score == 9.0 / 3.0
        assert score == 3.0
        
        # Test with default values
        feature = Feature(
            name="Default Feature",
            description="Test description"
        )
        
        score = scorer.score_feature(feature)
        assert score == 5.0 / 5.0  # Default values
        assert score == 1.0
    
    def test_kano_scorer(self):
        """Test the Kano scoring model."""
        # Create a scorer
        scorer = KanoScorer()
        
        # Calculate scores for different categories
        basic_score = scorer.category_to_score(KanoCategory.BASIC)
        performance_score = scorer.category_to_score(KanoCategory.PERFORMANCE)
        excitement_score = scorer.category_to_score(KanoCategory.EXCITEMENT)
        indifferent_score = scorer.category_to_score(KanoCategory.INDIFFERENT)
        reverse_score = scorer.category_to_score(KanoCategory.REVERSE)
        
        # Check the results
        assert basic_score > indifferent_score
        assert excitement_score > indifferent_score
        assert performance_score > indifferent_score
        assert indifferent_score > reverse_score
        
        # Test with a feature
        feature = Feature(
            name="Test Feature",
            description="Test description",
            kano_category="excitement"
        )
        
        # Score the feature
        score = scorer.score_feature(feature)
        
        # Check the result
        assert score == excitement_score
    
    def test_weighted_scorer(self):
        """Test the Weighted scoring model."""
        # Create a scorer
        scorer = WeightedScorer()
        
        # Create scores and weights
        scores = {
            "strategic": 8.0,
            "feedback": 7.0,
            "value": 9.0,
            "effort": 4.0
        }
        
        weights = {
            "strategic": 2.0,
            "feedback": 1.5,
            "value": 1.0,
            "effort": 0.5
        }
        
        # Calculate weighted score
        score = scorer.calculate_weighted_score(scores, weights)
        
        # Check the result
        weighted_sum = (8.0 * 2.0) + (7.0 * 1.5) + (9.0 * 1.0) + (4.0 * 0.5)
        total_weight = 2.0 + 1.5 + 1.0 + 0.5
        expected_score = weighted_sum / total_weight
        assert score == expected_score
        
        # Test with a feature
        feature = Feature(
            name="Test Feature",
            description="Test description",
            value_estimate=8.0,
            effort_estimate=3.0,
            objective_ids=[uuid4(), uuid4()],
            feedback_ids=[uuid4() for _ in range(5)]
        )
        
        criteria = PrioritizationCriteria(
            method=PrioritizationMethod.WEIGHTED,
            weight_strategic=2.0,
            weight_feedback=1.5,
            weight_value=1.0,
            weight_effort=0.5
        )
        
        # Score the feature
        score = scorer.score_feature(feature, criteria)
        
        # Check the result
        assert 0 <= score <= 10


class TestFeatureScorer:
    """Tests for the FeatureScorer class."""
    
    def test_score_feature_rice(self):
        """Test scoring a feature with the RICE method."""
        # Create a scorer
        scorer = FeatureScorer()
        
        # Create a feature
        feature = Feature(
            name="RICE Feature",
            description="Test description",
            feedback_ids=[uuid4() for _ in range(5)],
            feedback_cluster_ids=[uuid4()],
            effort_estimate=3.0,
            value_estimate=8.0
        )
        
        # Score with RICE method
        scorecard = scorer.score_feature(feature, PrioritizationMethod.RICE)
        
        # Check the result
        assert scorecard.feature_id == feature.id
        assert scorecard.rice_score is not None
        assert scorecard.total_score == scorecard.rice_score
        assert scorecard.value_effort_score is None
    
    def test_score_feature_value_effort(self):
        """Test scoring a feature with the Value/Effort method."""
        # Create a scorer
        scorer = FeatureScorer()
        
        # Create a feature
        feature = Feature(
            name="Value/Effort Feature",
            description="Test description",
            effort_estimate=3.0,
            value_estimate=9.0
        )
        
        # Score with Value/Effort method
        scorecard = scorer.score_feature(feature, PrioritizationMethod.VALUE_EFFORT)
        
        # Check the result
        assert scorecard.feature_id == feature.id
        assert scorecard.value_effort_score is not None
        assert scorecard.total_score == scorecard.value_effort_score
        assert scorecard.rice_score is None
    
    def test_score_feature_weighted(self):
        """Test scoring a feature with the Weighted method."""
        # Create a scorer
        scorer = FeatureScorer()
        
        # Create a feature
        feature = Feature(
            name="Weighted Feature",
            description="Test description",
            value_estimate=8.0,
            effort_estimate=3.0,
            objective_ids=[uuid4(), uuid4()],
            feedback_ids=[uuid4() for _ in range(5)]
        )
        
        criteria = PrioritizationCriteria(
            method=PrioritizationMethod.WEIGHTED,
            weight_strategic=2.0,
            weight_feedback=1.5,
            weight_value=1.0,
            weight_effort=0.5
        )
        
        # Score with Weighted method
        scorecard = scorer.score_feature(feature, PrioritizationMethod.WEIGHTED, criteria)
        
        # Check the result
        assert scorecard.feature_id == feature.id
        assert scorecard.total_score is not None
        assert scorecard.rice_score is not None
        assert scorecard.value_effort_score is not None
        assert scorecard.strategic_alignment_score is not None
        assert scorecard.customer_value_score is not None


class TestFeaturePrioritizer:
    """Tests for the FeaturePrioritizer class."""
    
    def test_add_and_get_feature(self, temp_dir):
        """Test adding and retrieving a feature."""
        # Create a prioritizer
        prioritizer = FeaturePrioritizer(storage_dir=temp_dir)
        
        # Create a feature
        feature = Feature(
            name="Test Feature",
            description="Test description",
            status=StatusEnum.PLANNED
        )
        
        # Add the feature
        added_feature = prioritizer.add_feature(feature)
        
        # Check the added feature
        assert added_feature.id == feature.id
        assert added_feature.name == "Test Feature"
        
        # Retrieve the feature
        retrieved_feature = prioritizer.get_feature(feature.id)
        
        # Check the retrieved feature
        assert retrieved_feature.id == feature.id
        assert retrieved_feature.name == "Test Feature"
        assert retrieved_feature.status == StatusEnum.PLANNED
    
    def test_prioritize_feature(self, temp_dir):
        """Test prioritizing a single feature."""
        # Create a prioritizer
        prioritizer = FeaturePrioritizer(storage_dir=temp_dir)
        
        # Create a feature
        feature = Feature(
            name="Priority Feature",
            description="Test description",
            value_estimate=8.0,
            effort_estimate=4.0,
            status=StatusEnum.PLANNED
        )
        
        # Add the feature
        added_feature = prioritizer.add_feature(feature)
        
        # Prioritize the feature
        prioritized_feature, scorecard = prioritizer.prioritize_feature(
            added_feature.id,
            PrioritizationMethod.VALUE_EFFORT
        )
        
        # Check the results
        assert prioritized_feature.id == feature.id
        assert prioritized_feature.priority_score is not None
        assert prioritized_feature.priority_method == PrioritizationMethod.VALUE_EFFORT.value
        assert scorecard.feature_id == feature.id
        assert scorecard.value_effort_score is not None
        assert scorecard.total_score == scorecard.value_effort_score
        
        # Check storage
        stored_feature = prioritizer.feature_storage.get(feature.id)
        assert stored_feature.priority_score == prioritized_feature.priority_score
        assert stored_feature.priority_method == prioritized_feature.priority_method
        
        stored_scorecard = prioritizer.get_scorecard(feature.id)
        assert stored_scorecard is not None
        assert stored_scorecard.value_effort_score == scorecard.value_effort_score
    
    def test_prioritize_features(self, temp_dir):
        """Test prioritizing multiple features."""
        # Create a prioritizer
        prioritizer = FeaturePrioritizer(storage_dir=temp_dir)
        
        # Create features
        features = [
            Feature(
                name="Feature 1",
                description="Description 1",
                value_estimate=9.0,
                effort_estimate=3.0,
                status=StatusEnum.PLANNED
            ),
            Feature(
                name="Feature 2",
                description="Description 2",
                value_estimate=7.0,
                effort_estimate=5.0,
                status=StatusEnum.PLANNED
            ),
            Feature(
                name="Feature 3",
                description="Description 3",
                value_estimate=8.0,
                effort_estimate=2.0,
                status=StatusEnum.PLANNED
            )
        ]
        
        # Add features
        added_features = [prioritizer.add_feature(feature) for feature in features]
        feature_ids = [feature.id for feature in added_features]
        
        # Create criteria
        criteria = PrioritizationCriteria(
            method=PrioritizationMethod.WEIGHTED,
            weight_value=2.0,
            weight_effort=1.0
        )
        
        # Prioritize features
        result = prioritizer.prioritize_features(
            feature_ids=feature_ids,
            method=PrioritizationMethod.WEIGHTED,
            criteria=criteria
        )
        
        # Check the results
        assert len(result.scored_features) == 3
        assert result.method == PrioritizationMethod.WEIGHTED
        assert result.criteria == criteria
        assert result.execution_time_ms > 0
        
        # Check that features are sorted by score (highest first)
        scores = [scorecard.total_score for _, scorecard in result.scored_features]
        assert scores == sorted(scores, reverse=True)
        
        # Check storage
        for feature_id in feature_ids:
            stored_feature = prioritizer.feature_storage.get(feature_id)
            assert stored_feature.priority_score is not None
            assert stored_feature.priority_method == PrioritizationMethod.WEIGHTED.value
            
            stored_scorecard = prioritizer.get_scorecard(feature_id)
            assert stored_scorecard is not None
    
    def test_get_top_features(self, temp_dir):
        """Test getting top prioritized features."""
        # Create a prioritizer
        prioritizer = FeaturePrioritizer(storage_dir=temp_dir)
        
        # Create features with various values and efforts
        features = [
            Feature(
                name="Feature 1",
                description="Description 1",
                value_estimate=9.0,
                effort_estimate=3.0,
                status=StatusEnum.PLANNED
            ),
            Feature(
                name="Feature 2",
                description="Description 2",
                value_estimate=7.0,
                effort_estimate=5.0,
                status=StatusEnum.PLANNED
            ),
            Feature(
                name="Feature 3",
                description="Description 3",
                value_estimate=8.0,
                effort_estimate=2.0,
                status=StatusEnum.PLANNED
            ),
            Feature(
                name="Feature 4",
                description="Description 4",
                value_estimate=5.0,
                effort_estimate=8.0,
                status=StatusEnum.PLANNED
            ),
            Feature(
                name="Feature 5",
                description="Description 5",
                value_estimate=6.0,
                effort_estimate=4.0,
                status=StatusEnum.PLANNED
            )
        ]
        
        # Add features
        added_features = [prioritizer.add_feature(feature) for feature in features]
        feature_ids = [feature.id for feature in added_features]
        
        # Prioritize features with Value/Effort method
        prioritizer.prioritize_features(
            feature_ids=feature_ids,
            method=PrioritizationMethod.VALUE_EFFORT
        )
        
        # Get top 3 features
        top_features = prioritizer.get_top_features(limit=3)
        
        # Check the results
        assert len(top_features) == 3
        
        # Check that they are sorted by score
        scores = [score for _, score in top_features]
        assert scores == sorted(scores, reverse=True)
        
        # Feature 3 should be the top feature (8/2 = 4)
        top_feature_name = top_features[0][0].name
        assert top_feature_name == "Feature 3"
    
    def test_compare_prioritization_methods(self, temp_dir):
        """Test comparing different prioritization methods."""
        # Create a prioritizer
        prioritizer = FeaturePrioritizer(storage_dir=temp_dir)
        
        # Create a feature with various characteristics
        feature = Feature(
            name="Comparison Feature",
            description="Description for comparison",
            value_estimate=8.0,
            effort_estimate=4.0,
            objective_ids=[uuid4(), uuid4()],
            feedback_ids=[uuid4() for _ in range(5)],
            kano_category="performance",
            status=StatusEnum.PLANNED
        )
        
        # Add feature
        added_feature = prioritizer.add_feature(feature)
        
        # Compare prioritization methods
        comparison = prioritizer.compare_prioritization_methods([added_feature.id])
        
        # Check the results
        assert len(comparison) == len(PrioritizationMethod)
        
        # Each method should have a score
        for method in PrioritizationMethod:
            assert method.value in comparison
            assert len(comparison[method.value]) == 1  # One feature
            
            # Get the score
            compared_feature, score = comparison[method.value][0]
            assert compared_feature.id == added_feature.id
            assert score >= 0