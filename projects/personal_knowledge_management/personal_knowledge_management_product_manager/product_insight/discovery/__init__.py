"""
Knowledge discovery module for ProductInsight.

This module provides functionality for discovering insights and searching
across knowledge domains.
"""

from product_insight.discovery.insights import (
    Insight,
    InsightEngine,
    InsightGroup,
    TrendData,
)
from product_insight.discovery.search import SearchEngine, SearchIndex
from product_insight.discovery.visualization import (
    ConnectionGraph,
    DiscoveryVisualizer,
    InsightVisualization,
    TrendVisualization,
)
from product_insight.models import SearchQuery

__all__ = [
    "Insight",
    "InsightEngine",
    "InsightGroup",
    "TrendData",
    "SearchEngine",
    "SearchIndex",
    "SearchQuery",
    "DiscoveryVisualizer",
    "InsightVisualization",
    "TrendVisualization",
    "ConnectionGraph",
]