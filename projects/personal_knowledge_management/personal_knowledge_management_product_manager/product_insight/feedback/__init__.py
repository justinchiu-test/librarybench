"""
Feedback management module for ProductInsight.

This module provides functionality for managing customer feedback,
including importing, processing, clustering, and analyzing feedback.
"""

from product_insight.feedback.analyzer import (
    FeedbackAnalyzer,
    FeatureExtraction,
    SentimentResult,
)
from product_insight.feedback.clustering import (
    ClusteringParams,
    ClusteringResult,
    FeedbackClusterer,
)
from product_insight.feedback.manager import FeedbackManager, FeedbackStats

__all__ = [
    "FeedbackAnalyzer",
    "SentimentResult",
    "FeatureExtraction",
    "FeedbackClusterer",
    "ClusteringParams",
    "ClusteringResult",
    "FeedbackManager",
    "FeedbackStats",
]