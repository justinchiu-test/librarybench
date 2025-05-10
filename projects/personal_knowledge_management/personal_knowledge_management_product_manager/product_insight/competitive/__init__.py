"""
Competitive analysis module for ProductInsight.

This module provides functionality for analyzing competitor products and
market positioning.
"""

from product_insight.competitive.analysis import (
    CompetitiveAnalyzer,
    CompetitorFeatureMatrix,
    MarketSegmentDistribution,
    PricingComparison,
)
from product_insight.competitive.visualization import CompetitiveVisualizer

__all__ = [
    "CompetitiveAnalyzer",
    "CompetitorFeatureMatrix",
    "MarketSegmentDistribution",
    "PricingComparison",
    "CompetitiveVisualizer",
]