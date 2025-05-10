"""
Stakeholder management module for ProductInsight.

This module provides functionality for managing stakeholders, their perspectives,
and relationships.
"""

from product_insight.stakeholders.manager import (
    StakeholderAlignment,
    StakeholderGroup,
    StakeholderManager,
    StakeholderNetwork,
    StakeholderQuery,
)
from product_insight.stakeholders.visualization import (
    StakeholderHeatmap,
    StakeholderHeatmapItem,
    StakeholderMatrix,
    StakeholderMatrixItem,
    StakeholderVisualizer,
)

__all__ = [
    "StakeholderManager",
    "StakeholderQuery",
    "StakeholderGroup",
    "StakeholderAlignment",
    "StakeholderNetwork",
    "StakeholderVisualizer",
    "StakeholderMatrix",
    "StakeholderMatrixItem",
    "StakeholderHeatmap",
    "StakeholderHeatmapItem",
]