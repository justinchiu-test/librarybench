"""
Prioritization models for ProductInsight.

This module provides models and algorithms for feature prioritization,
including various frameworks like RICE, Value/Effort, and Kano.
"""

from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel

from product_insight.models import Feature, PriorityScoreCard


class KanoCategory(str, Enum):
    """Categories for the Kano model."""
    
    BASIC = "basic"
    PERFORMANCE = "performance"
    EXCITEMENT = "excitement"
    INDIFFERENT = "indifferent"
    REVERSE = "reverse"


class PrioritizationMethod(str, Enum):
    """Available prioritization methods."""
    
    RICE = "rice"
    VALUE_EFFORT = "value_effort"
    KANO = "kano"
    WEIGHTED = "weighted"
    STRATEGIC = "strategic"
    CUSTOM = "custom"


class PrioritizationCriteria(BaseModel):
    """Criteria for feature prioritization."""
    
    method: PrioritizationMethod
    weight_strategic: float = 1.0
    weight_feedback: float = 1.0
    weight_effort: float = 1.0
    weight_value: float = 1.0
    weight_risk: float = 1.0
    weight_time_sensitivity: float = 1.0
    weight_innovation: float = 1.0
    custom_weights: Dict[str, float] = {}


class RiceScorer:
    """Scorer for RICE (Reach, Impact, Confidence, Effort) prioritization model."""
    
    @staticmethod
    def calculate_rice_score(
        reach: float,
        impact: float,
        confidence: float,
        effort: float
    ) -> float:
        """Calculate RICE score.
        
        RICE = (Reach * Impact * Confidence) / Effort
        
        Args:
            reach: Number of people affected (typically customers per time period)
            impact: Impact per person (typically on a scale of 0.25, 0.5, 1, 2, 3)
            confidence: Confidence percentage (typically 50%, 80%, 100%)
            effort: Estimated effort (typically person-weeks)
            
        Returns:
            RICE score
        """
        if effort <= 0:
            return 0.0
        
        # Convert confidence to percentage if it's given as a whole number
        if confidence > 1:
            confidence = confidence / 100.0
        
        return (reach * impact * confidence) / effort
    
    @staticmethod
    def score_feature(feature: Feature) -> float:
        """Calculate RICE score for a feature.
        
        This method uses feature attributes and metadata to compute the RICE score.
        
        Args:
            feature: Feature to score
            
        Returns:
            RICE score
        """
        # Extract values from the feature, with reasonable defaults
        # In a real implementation, these would come from feature attributes or be calculated
        reach = len(feature.feedback_ids) + len(feature.feedback_cluster_ids) * 5
        
        # Impact based on value estimate
        impact = 1.0
        if feature.value_estimate is not None:
            if feature.value_estimate >= 9:
                impact = 3.0
            elif feature.value_estimate >= 7:
                impact = 2.0
            elif feature.value_estimate >= 5:
                impact = 1.0
            elif feature.value_estimate >= 3:
                impact = 0.5
            else:
                impact = 0.25
        
        # Confidence based on research and validation
        confidence = 0.8  # Default to 80% confidence
        
        # Effort from feature estimate, default to 1 if not provided
        effort = max(1.0, feature.effort_estimate or 1.0)
        
        return RiceScorer.calculate_rice_score(reach, impact, confidence, effort)


class ValueEffortScorer:
    """Scorer for Value/Effort prioritization model."""
    
    @staticmethod
    def calculate_value_effort_score(value: float, effort: float) -> float:
        """Calculate Value/Effort score.
        
        Value/Effort = Value / Effort
        
        Args:
            value: Estimated value (typically on a scale of 1-10)
            effort: Estimated effort (typically on a scale of 1-10)
            
        Returns:
            Value/Effort score
        """
        if effort <= 0:
            return 0.0
        
        return value / effort
    
    @staticmethod
    def score_feature(feature: Feature) -> float:
        """Calculate Value/Effort score for a feature.
        
        This method uses feature attributes to compute the Value/Effort score.
        
        Args:
            feature: Feature to score
            
        Returns:
            Value/Effort score
        """
        # Extract values from the feature, with reasonable defaults
        value = feature.value_estimate or 5.0
        effort = max(1.0, feature.effort_estimate or 5.0)
        
        return ValueEffortScorer.calculate_value_effort_score(value, effort)


class KanoScorer:
    """Scorer for Kano prioritization model."""
    
    @staticmethod
    def category_to_score(category: KanoCategory) -> float:
        """Convert Kano category to a numerical score.
        
        Args:
            category: Kano category
            
        Returns:
            Numerical score
        """
        # Convert Kano categories to scores for prioritization
        scores = {
            KanoCategory.BASIC: 8.0,       # Must be implemented
            KanoCategory.PERFORMANCE: 6.0,  # More is better
            KanoCategory.EXCITEMENT: 7.0,   # Delighters, unexpected
            KanoCategory.INDIFFERENT: 2.0,  # Users don't care
            KanoCategory.REVERSE: 0.0,      # Users dislike
        }
        
        return scores.get(category, 4.0)
    
    @staticmethod
    def score_feature(feature: Feature) -> float:
        """Calculate Kano score for a feature.
        
        This method uses feature attributes to determine the Kano score.
        
        Args:
            feature: Feature to score
            
        Returns:
            Kano score
        """
        # Extract Kano category from the feature, default to INDIFFERENT
        category_str = feature.kano_category or "indifferent"
        
        try:
            category = KanoCategory(category_str.lower())
        except ValueError:
            category = KanoCategory.INDIFFERENT
        
        return KanoScorer.category_to_score(category)


class WeightedScorer:
    """Scorer for weighted prioritization model."""
    
    @staticmethod
    def calculate_weighted_score(
        scores: Dict[str, float],
        weights: Dict[str, float]
    ) -> float:
        """Calculate weighted score.
        
        Args:
            scores: Dictionary of scores by criteria
            weights: Dictionary of weights by criteria
            
        Returns:
            Weighted score
        """
        # If there are no scores or weights, return zero
        if not scores or not weights:
            return 0.0
        
        # Calculate weighted sum
        weighted_sum = sum(
            score * weights.get(criteria, 1.0)
            for criteria, score in scores.items()
            if criteria in weights
        )
        
        # Calculate total weight for normalization
        total_weight = sum(
            weights.get(criteria, 1.0)
            for criteria in scores.keys()
            if criteria in weights
        )
        
        if total_weight <= 0:
            return 0.0
        
        return weighted_sum / total_weight
    
    @staticmethod
    def score_feature(
        feature: Feature, 
        criteria: PrioritizationCriteria
    ) -> float:
        """Calculate weighted score for a feature.
        
        This method uses feature attributes and criteria to compute a weighted score.
        
        Args:
            feature: Feature to score
            criteria: Prioritization criteria with weights
            
        Returns:
            Weighted score
        """
        # Calculate individual scores
        scores = {}
        
        # Strategic alignment
        strategic_score = 0.0
        if feature.objective_ids:
            # More objectives = higher score (could be more sophisticated)
            strategic_score = min(10.0, len(feature.objective_ids) * 2.0)
        scores["strategic"] = strategic_score
        
        # Feedback-based score
        feedback_score = 0.0
        if feature.feedback_ids or feature.feedback_cluster_ids:
            feedback_count = len(feature.feedback_ids) + len(feature.feedback_cluster_ids) * 5
            feedback_score = min(10.0, feedback_count / 5.0)
        scores["feedback"] = feedback_score
        
        # Value and effort scores
        scores["value"] = feature.value_estimate or 5.0
        scores["effort"] = 10.0 - min(10.0, feature.effort_estimate or 5.0)  # Invert effort
        
        # Risk score (lower risk = higher score)
        risk_score = 10.0 - min(10.0, feature.risk_level or 5.0)  # Invert risk
        scores["risk"] = risk_score
        
        # Time sensitivity (default to medium)
        scores["time_sensitivity"] = 5.0
        
        # Innovation score (default to medium)
        scores["innovation"] = 5.0
        
        # Extract weights from criteria
        weights = {
            "strategic": criteria.weight_strategic,
            "feedback": criteria.weight_feedback,
            "value": criteria.weight_value,
            "effort": criteria.weight_effort,
            "risk": criteria.weight_risk,
            "time_sensitivity": criteria.weight_time_sensitivity,
            "innovation": criteria.weight_innovation,
        }
        
        # Add custom weights
        if criteria.custom_weights:
            weights.update(criteria.custom_weights)
        
        return WeightedScorer.calculate_weighted_score(scores, weights)


class FeatureScorer:
    """Orchestrates various scoring methods for features."""
    
    def __init__(self):
        """Initialize the feature scorer."""
        self.rice_scorer = RiceScorer()
        self.value_effort_scorer = ValueEffortScorer()
        self.kano_scorer = KanoScorer()
        self.weighted_scorer = WeightedScorer()
    
    def score_feature(
        self, 
        feature: Feature, 
        method: PrioritizationMethod,
        criteria: Optional[PrioritizationCriteria] = None
    ) -> PriorityScoreCard:
        """Score a feature using the specified method.
        
        Args:
            feature: Feature to score
            method: Prioritization method to use
            criteria: Optional prioritization criteria
            
        Returns:
            PriorityScoreCard with scores
        """
        if criteria is None:
            criteria = PrioritizationCriteria(method=method)
        
        # Create a scorecard for the feature
        scorecard = PriorityScoreCard(feature_id=feature.id)
        
        # Calculate scores based on the method
        if method == PrioritizationMethod.RICE:
            scorecard.rice_score = self.rice_scorer.score_feature(feature)
            scorecard.total_score = scorecard.rice_score
        
        elif method == PrioritizationMethod.VALUE_EFFORT:
            scorecard.value_effort_score = self.value_effort_scorer.score_feature(feature)
            scorecard.total_score = scorecard.value_effort_score
        
        elif method == PrioritizationMethod.KANO:
            kano_score = self.kano_scorer.score_feature(feature)
            scorecard.custom_scores["kano"] = kano_score
            scorecard.total_score = kano_score
        
        elif method == PrioritizationMethod.WEIGHTED:
            weighted_score = self.weighted_scorer.score_feature(feature, criteria)
            scorecard.total_score = weighted_score
            
            # Also calculate component scores for reference
            scorecard.rice_score = self.rice_scorer.score_feature(feature)
            scorecard.value_effort_score = self.value_effort_scorer.score_feature(feature)
            
            # Strategic alignment
            if feature.objective_ids:
                strategic_score = min(10.0, len(feature.objective_ids) * 2.0) / 10.0
                scorecard.strategic_alignment_score = strategic_score
            
            # Customer value
            if feature.feedback_ids or feature.feedback_cluster_ids:
                feedback_count = len(feature.feedback_ids) + len(feature.feedback_cluster_ids) * 5
                customer_value = min(10.0, feedback_count / 5.0) / 10.0
                scorecard.customer_value_score = customer_value
        
        else:  # Default or custom
            # Calculate all scores for custom prioritization
            scorecard.rice_score = self.rice_scorer.score_feature(feature)
            scorecard.value_effort_score = self.value_effort_scorer.score_feature(feature)
            kano_score = self.kano_scorer.score_feature(feature)
            scorecard.custom_scores["kano"] = kano_score
            
            # Strategic alignment
            if feature.objective_ids:
                strategic_score = min(10.0, len(feature.objective_ids) * 2.0) / 10.0
                scorecard.strategic_alignment_score = strategic_score
            
            # Customer value
            if feature.feedback_ids or feature.feedback_cluster_ids:
                feedback_count = len(feature.feedback_ids) + len(feature.feedback_cluster_ids) * 5
                customer_value = min(10.0, feedback_count / 5.0) / 10.0
                scorecard.customer_value_score = customer_value
            
            # Use weighted score as the default total
            scorecard.total_score = self.weighted_scorer.score_feature(feature, criteria)
        
        return scorecard