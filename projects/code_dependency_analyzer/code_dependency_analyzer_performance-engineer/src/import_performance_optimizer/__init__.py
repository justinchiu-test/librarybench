"""Import Performance Optimizer

A performance-focused dependency analysis tool for optimizing application
startup time and memory footprint by analyzing import chains.
"""

from .profiler import ImportProfiler
from .memory_analyzer import MemoryAnalyzer
from .lazy_loading import LazyLoadingDetector
from .circular_imports import CircularImportAnalyzer
from .dynamic_optimizer import DynamicImportOptimizer
from .models import (
    ImportMetrics,
    MemoryFootprint,
    LazyLoadingOpportunity,
    CircularImportInfo,
    DynamicImportSuggestion,
)

__version__ = "0.1.0"

__all__ = [
    "ImportProfiler",
    "MemoryAnalyzer",
    "LazyLoadingDetector",
    "CircularImportAnalyzer",
    "DynamicImportOptimizer",
    "ImportMetrics",
    "MemoryFootprint",
    "LazyLoadingOpportunity",
    "CircularImportInfo",
    "DynamicImportSuggestion",
]