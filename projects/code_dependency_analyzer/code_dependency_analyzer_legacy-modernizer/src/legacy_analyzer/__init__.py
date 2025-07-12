"""Legacy System Modernization Analyzer.

A specialized dependency analysis tool for consultants modernizing legacy codebases.
"""

from .analyzer import LegacyAnalyzer
from .models import (
    AnalysisResult,
    LegacyPattern,
    ModernizationRoadmap,
    StranglerFigBoundary,
    ExtractionFeasibility,
    DatabaseCoupling,
)

__version__ = "0.1.0"
__all__ = [
    "LegacyAnalyzer",
    "AnalysisResult",
    "LegacyPattern",
    "ModernizationRoadmap",
    "StranglerFigBoundary",
    "ExtractionFeasibility",
    "DatabaseCoupling",
]
