"""Analysis framework shared across implementations."""

from common.core.analysis.analyzer import (
    BaseAnalyzer,
    AnalysisResult,
    AnalysisParameters,
)

from common.core.analysis.time_series import (
    TimeSeriesGranularity,
    TimeSeriesData,
    TimeSeriesParameters,
    TimeSeriesAnalyzer,
)

from common.core.analysis.portfolio import (
    PortfolioAnalysisParameters,
    PortfolioBreakdown,
    PortfolioPerformance,
    PortfolioESGMetrics,
    PortfolioAnalysisResult,
    PortfolioAnalyzer,
)

from common.core.analysis.financial_projector import (
    ProjectionScenario,
    ProjectionParameters,
    CashFlow,
    Projection,
    ProjectionResult,
    FinancialProjector,
)

__all__ = [
    # Base analysis
    "BaseAnalyzer",
    "AnalysisResult",
    "AnalysisParameters",
    
    # Time series analysis
    "TimeSeriesGranularity",
    "TimeSeriesData",
    "TimeSeriesParameters",
    "TimeSeriesAnalyzer",
    
    # Portfolio analysis
    "PortfolioAnalysisParameters",
    "PortfolioBreakdown",
    "PortfolioPerformance",
    "PortfolioESGMetrics",
    "PortfolioAnalysisResult",
    "PortfolioAnalyzer",
    
    # Financial projections
    "ProjectionScenario",
    "ProjectionParameters",
    "CashFlow",
    "Projection",
    "ProjectionResult",
    "FinancialProjector",
]