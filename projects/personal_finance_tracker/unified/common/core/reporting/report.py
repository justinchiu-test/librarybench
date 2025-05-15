"""Base reporting framework shared across implementations."""

from abc import ABC, abstractmethod
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ReportFormat(str, Enum):
    """Format options for reports."""
    
    SUMMARY = "summary"
    DETAILED = "detailed"
    CSV = "csv"
    JSON = "json"
    MARKDOWN = "markdown"


class ReportPeriod(str, Enum):
    """Time period options for reports."""
    
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class ReportParameters(BaseModel):
    """
    Parameters for report generation.
    
    Used to configure report options and settings.
    """
    
    period: ReportPeriod = ReportPeriod.MONTHLY
    start_date: Optional[Union[date, datetime]] = None
    end_date: Optional[Union[date, datetime]] = None
    format: ReportFormat = ReportFormat.DETAILED
    include_metadata: bool = False
    group_by: Optional[str] = None
    filters: Dict[str, Any] = Field(default_factory=dict)
    sort_by: Optional[str] = None
    sort_direction: str = "desc"
    limit: Optional[int] = None


class ReportSection(BaseModel):
    """
    Section of a report.
    
    Used to organize report data into logical sections.
    """
    
    title: str
    summary: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)
    charts: List[Dict[str, Any]] = Field(default_factory=list)
    subsections: List["ReportSection"] = Field(default_factory=list)
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class Report(BaseModel):
    """
    Report model for organizing and presenting analysis results.
    
    Used for generating structured reports from analysis data.
    """
    
    id: Union[str, UUID] = Field(default_factory=uuid4)
    title: str
    description: Optional[str] = None
    generated_at: datetime = Field(default_factory=datetime.now)
    period: ReportPeriod
    start_date: Optional[Union[date, datetime]] = None
    end_date: Optional[Union[date, datetime]] = None
    format: ReportFormat
    sections: List[ReportSection] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ReportGenerator(ABC):
    """
    Abstract base class for report generators.
    
    Defines the core interface for all report generators
    across different persona implementations.
    """
    
    @abstractmethod
    def generate(self, data: Any, parameters: ReportParameters) -> Report:
        """
        Generate a report from the provided data.
        
        Args:
            data: The data to include in the report
            parameters: Parameters to configure the report
            
        Returns:
            Generated report
        """
        pass
    
    def _format_currency(self, value: float) -> str:
        """
        Format a value as currency.
        
        Args:
            value: The value to format
            
        Returns:
            Formatted currency string
        """
        return f"${value:,.2f}"
    
    def _format_percentage(self, value: float) -> str:
        """
        Format a value as percentage.
        
        Args:
            value: The value to format
            
        Returns:
            Formatted percentage string
        """
        return f"{value * 100:.2f}%"
    
    def _format_date(self, value: Union[date, datetime]) -> str:
        """
        Format a date value.
        
        Args:
            value: The date to format
            
        Returns:
            Formatted date string
        """
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return value.strftime("%Y-%m-%d")
    
    def export_as_markdown(self, report: Report) -> str:
        """
        Export a report as markdown text.
        
        Args:
            report: The report to export
            
        Returns:
            Markdown text representation of the report
        """
        lines = []
        
        # Add title and description
        lines.append(f"# {report.title}")
        lines.append("")
        
        if report.description:
            lines.append(report.description)
            lines.append("")
        
        # Add period information
        period_str = f"Period: {report.period.value.capitalize()}"
        if report.start_date and report.end_date:
            period_str += f" ({self._format_date(report.start_date)} to {self._format_date(report.end_date)})"
        lines.append(period_str)
        lines.append(f"Generated: {self._format_date(report.generated_at)}")
        lines.append("")
        
        # Add sections
        for section in report.sections:
            self._append_section_markdown(lines, section, 2)
        
        # Add metadata if requested
        if report.metadata and report.format == ReportFormat.DETAILED:
            lines.append("## Metadata")
            lines.append("")
            for key, value in report.metadata.items():
                lines.append(f"- **{key}**: {value}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _append_section_markdown(self, lines: List[str], section: ReportSection, level: int) -> None:
        """
        Append a section to the markdown lines.
        
        Args:
            lines: The list of markdown lines
            section: The section to append
            level: The heading level
        """
        # Add section title
        heading = "#" * level
        lines.append(f"{heading} {section.title}")
        lines.append("")
        
        # Add section summary
        if section.summary:
            lines.append(section.summary)
            lines.append("")
        
        # Add section data as a table if available
        if section.data:
            # For simple key-value data
            if all(not isinstance(v, (dict, list)) for v in section.data.values()):
                lines.append("| Metric | Value |")
                lines.append("| ------ | ----- |")
                for key, value in section.data.items():
                    formatted_key = key.replace("_", " ").title()
                    formatted_value = value
                    
                    # Format value based on type
                    if isinstance(value, float):
                        if "percentage" in key.lower() or "rate" in key.lower():
                            formatted_value = self._format_percentage(value)
                        elif "amount" in key.lower() or "balance" in key.lower() or "value" in key.lower():
                            formatted_value = self._format_currency(value)
                    
                    lines.append(f"| {formatted_key} | {formatted_value} |")
                lines.append("")
        
        # Add charts if available (as descriptions)
        for chart in section.charts:
            chart_type = chart.get("type", "unknown")
            chart_title = chart.get("title", "Chart")
            lines.append(f"*{chart_title} ({chart_type} chart)*")
            lines.append("")
        
        # Add subsections recursively
        for subsection in section.subsections:
            self._append_section_markdown(lines, subsection, level + 1)
    
    def export_as_csv(self, report: Report) -> str:
        """
        Export a report as CSV text.
        
        Args:
            report: The report to export
            
        Returns:
            CSV text representation of the report
        """
        lines = []
        
        # Add header
        lines.append(f"# {report.title}")
        lines.append(f"# Period: {report.period.value.capitalize()}")
        if report.start_date and report.end_date:
            lines.append(f"# From: {self._format_date(report.start_date)} To: {self._format_date(report.end_date)}")
        lines.append(f"# Generated: {self._format_date(report.generated_at)}")
        lines.append("")
        
        # Add sections
        for section in report.sections:
            self._append_section_csv(lines, section)
        
        return "\n".join(lines)
    
    def _append_section_csv(self, lines: List[str], section: ReportSection) -> None:
        """
        Append a section to the CSV lines.
        
        Args:
            lines: The list of CSV lines
            section: The section to append
        """
        # Add section header
        lines.append(f"# {section.title}")
        
        # Add section data
        if section.data:
            # For simple key-value data
            if all(not isinstance(v, (dict, list)) for v in section.data.values()):
                lines.append("Metric,Value")
                for key, value in section.data.items():
                    formatted_key = key.replace("_", " ").title()
                    formatted_value = value
                    
                    # Format value based on type
                    if isinstance(value, float):
                        if "percentage" in key.lower() or "rate" in key.lower():
                            formatted_value = f"{value * 100:.2f}%"
                        elif "amount" in key.lower() or "balance" in key.lower() or "value" in key.lower():
                            formatted_value = f"{value:.2f}"
                    
                    # Escape commas and quotes in CSV
                    if isinstance(formatted_value, str) and ("," in formatted_value or '"' in formatted_value):
                        formatted_value = f'"{formatted_value.replace(\'"\', \'""\')}"'
                    
                    lines.append(f"{formatted_key},{formatted_value}")
        
        lines.append("")
        
        # Add subsections recursively
        for subsection in section.subsections:
            self._append_section_csv(lines, subsection)
    
    def export_as_json(self, report: Report) -> Dict[str, Any]:
        """
        Export a report as a JSON-serializable dictionary.
        
        Args:
            report: The report to export
            
        Returns:
            JSON-serializable dictionary representation of the report
        """
        # Convert to dictionary with datetime formatting
        report_dict = report.dict()
        
        # Format dates for JSON serialization
        if "generated_at" in report_dict:
            report_dict["generated_at"] = self._format_date(report.generated_at)
        
        if "start_date" in report_dict and report_dict["start_date"]:
            report_dict["start_date"] = self._format_date(report.start_date)
        
        if "end_date" in report_dict and report_dict["end_date"]:
            report_dict["end_date"] = self._format_date(report.end_date)
        
        return report_dict