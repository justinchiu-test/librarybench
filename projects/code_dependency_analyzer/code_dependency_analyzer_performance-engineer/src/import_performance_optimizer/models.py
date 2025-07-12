"""Data models for Import Performance Optimizer."""

from typing import List, Dict, Optional, Set, Any
from datetime import timedelta
from pydantic import BaseModel, Field


class ImportMetrics(BaseModel):
    """Metrics for a single import."""

    module_name: str
    import_time: timedelta
    cumulative_time: timedelta
    parent_module: Optional[str] = None
    children: List[str] = Field(default_factory=list)
    is_bottleneck: bool = False
    import_depth: int = 0


class MemoryFootprint(BaseModel):
    """Memory footprint information for a module."""

    module_name: str
    direct_memory: int  # bytes
    cumulative_memory: int  # bytes including all dependencies
    memory_by_child: Dict[str, int] = Field(default_factory=dict)
    percentage_of_total: float = 0.0


class LazyLoadingOpportunity(BaseModel):
    """Information about a potential lazy loading optimization."""

    module_name: str
    import_location: str
    first_usage_location: Optional[str] = None
    time_to_first_use: Optional[timedelta] = None
    estimated_time_savings: timedelta
    confidence_score: float = Field(ge=0.0, le=1.0)
    transformation_suggestion: str = ""


class CircularImportInfo(BaseModel):
    """Information about a circular import."""

    modules_involved: List[str]
    performance_impact: timedelta
    memory_overhead: int  # bytes
    import_chain: List[str]
    severity: str = Field(pattern="^(low|medium|high|critical)$")


class DynamicImportSuggestion(BaseModel):
    """Suggestion for converting to dynamic import."""

    module_name: str
    current_import_statement: str
    suggested_import_statement: str
    usage_patterns: List[str]
    estimated_time_improvement: timedelta
    estimated_memory_savings: int  # bytes
    code_examples: List[str] = Field(default_factory=list)


class ImportAnalysisReport(BaseModel):
    """Complete analysis report."""

    total_import_time: timedelta
    total_memory_footprint: int  # bytes
    bottleneck_modules: List[ImportMetrics]
    lazy_loading_opportunities: List[LazyLoadingOpportunity]
    circular_imports: List[CircularImportInfo]
    dynamic_import_suggestions: List[DynamicImportSuggestion]
    optimization_summary: Dict[str, Any] = Field(default_factory=dict)