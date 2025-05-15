"""Reporting framework shared across implementations."""

from common.core.reporting.report import (
    ReportFormat,
    ReportPeriod,
    ReportParameters,
    ReportSection,
    Report,
    ReportGenerator,
)

from common.core.reporting.financial_reports import (
    TransactionSummaryGenerator,
    PortfolioReportGenerator,
    ProjectionReportGenerator,
)

__all__ = [
    # Base reporting
    "ReportFormat",
    "ReportPeriod", 
    "ReportParameters",
    "ReportSection",
    "Report",
    "ReportGenerator",
    
    # Financial reports
    "TransactionSummaryGenerator",
    "PortfolioReportGenerator",
    "ProjectionReportGenerator",
]