"""Reporting functionality for file system analysis.

This module provides reporting capabilities for generating and exporting
analysis results in various formats.
"""

import os
import json
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple

from pydantic import BaseModel, Field

from .base import ReportGenerator
from ..utils.types import ScanResult, ScanSummary, FileCategory, ComplianceCategory
from ..utils.crypto import CryptoProvider, sign_data, verify_signed_data


logger = logging.getLogger(__name__)


class ReportMetadata(BaseModel):
    """Metadata for a report."""
    
    report_id: str
    report_name: str
    generated_at: datetime
    generator_info: Dict[str, Any] = Field(default_factory=dict)
    additional_info: Dict[str, Any] = Field(default_factory=dict)
    signature_info: Optional[Dict[str, Any]] = None


class Report(BaseModel):
    """Base class for reports."""
    
    metadata: ReportMetadata
    summary: Dict[str, Any]
    findings: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    
    def sign(self, crypto_provider: CryptoProvider):
        """
        Sign the report to ensure integrity.
        
        Args:
            crypto_provider: Provider for cryptographic operations
        """
        # Create a copy of the report data without the signature
        report_data = self.dict(exclude={"metadata": {"signature_info"}})
        
        # Sign the report data
        signature_info = sign_data(report_data, crypto_provider)
        
        # Update the metadata with signature info
        self.metadata.signature_info = signature_info
    
    def verify(self, crypto_provider: CryptoProvider) -> bool:
        """
        Verify the report signature.
        
        Args:
            crypto_provider: Provider for cryptographic operations
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not self.metadata.signature_info:
            return False
        
        # Create a copy of the report data without the signature
        report_data = self.dict(exclude={"metadata": {"signature_info"}})
        
        # Verify the signature
        return verify_signed_data(
            data=report_data,
            signature_info=self.metadata.signature_info,
            crypto_provider=crypto_provider
        )
    
    def to_json(self, indent: int = 2) -> str:
        """
        Convert report to JSON string.
        
        Args:
            indent: Indentation level for JSON formatting
            
        Returns:
            JSON representation of report
        """
        return json.dumps(self.dict(), indent=indent, default=str)
    
    def save(
        self, 
        file_path: Union[str, Path],
        verify: bool = True,
        crypto_provider: Optional[CryptoProvider] = None
    ) -> str:
        """
        Save report to a file.
        
        Args:
            file_path: Path to save to
            verify: Whether to verify signature before saving
            crypto_provider: Provider for cryptographic operations
            
        Returns:
            Path to saved file
        """
        # Verify signature if requested
        if verify and crypto_provider and self.metadata.signature_info:
            if not self.verify(crypto_provider):
                raise ValueError("Report signature verification failed")
        
        # Save to file
        with open(file_path, 'w') as f:
            f.write(self.to_json())
        
        return str(file_path)


class GenericReportGenerator(ReportGenerator):
    """Generic report generator implementation."""
    
    def __init__(
        self,
        report_name: str = "File Analysis Report",
        crypto_provider: Optional[CryptoProvider] = None
    ):
        """
        Initialize report generator.
        
        Args:
            report_name: Name for generated reports
            crypto_provider: Provider for cryptographic operations
        """
        self.report_name = report_name
        self.crypto_provider = crypto_provider or CryptoProvider.generate()
    
    def generate_report(
        self, 
        scan_results: List[ScanResult],
        scan_summary: Optional[ScanSummary] = None
    ) -> Report:
        """
        Generate a report from scan results.
        
        Args:
            scan_results: List of scan results to include in the report
            scan_summary: Optional summary of scan results
            
        Returns:
            Generated report
        """
        # Create a unique report ID
        import uuid
        report_id = str(uuid.uuid4())
        
        # Create metadata
        metadata = ReportMetadata(
            report_id=report_id,
            report_name=self.report_name,
            generated_at=datetime.now(),
            generator_info={
                "generator": self.__class__.__name__,
                "result_count": len(scan_results),
            }
        )
        
        # Create summary data
        if scan_summary:
            summary = scan_summary.dict()
        else:
            # Compute basic summary if not provided
            start_time = min(r.scan_time for r in scan_results) if scan_results else datetime.now()
            end_time = max(r.scan_time for r in scan_results) if scan_results else datetime.now()
            duration = sum(r.scan_duration for r in scan_results)
            
            files_with_matches = sum(1 for r in scan_results if len(r.matches) > 0)
            total_matches = sum(len(r.matches) for r in scan_results)
            files_with_errors = sum(1 for r in scan_results if r.error is not None)
            
            summary = {
                "start_time": start_time,
                "end_time": end_time,
                "duration": duration,
                "total_files": len(scan_results),
                "files_with_matches": files_with_matches,
                "total_matches": total_matches,
                "files_with_errors": files_with_errors
            }
        
        # Create findings from scan results
        findings = []
        for result in scan_results:
            if result.matches:
                for match in result.matches:
                    finding = {
                        "file_path": result.file_metadata.file_path,
                        "file_size": result.file_metadata.file_size,
                        "file_type": result.file_metadata.file_type,
                        "pattern_name": match.pattern_name,
                        "pattern_description": match.pattern_description,
                        "matched_content": match.matched_content,
                        "category": match.category,
                        "sensitivity": match.sensitivity
                    }
                    
                    if match.line_number is not None:
                        finding["line_number"] = match.line_number
                    
                    if match.context:
                        finding["context"] = match.context
                        
                    findings.append(finding)
        
        # Create the report
        report = Report(
            metadata=metadata,
            summary=summary,
            findings=findings
        )
        
        # Sign the report if crypto provider is available
        if self.crypto_provider:
            report.sign(self.crypto_provider)
        
        return report
    
    def export_report(
        self, 
        report: Report, 
        output_path: Union[str, Path],
        format: str = "json"
    ) -> str:
        """
        Export a report to a file.
        
        Args:
            report: Report to export
            output_path: Path to export to
            format: Export format ("json", "csv", or "html")
            
        Returns:
            Path to exported report
        """
        path = Path(output_path)
        
        # Create parent directory if it doesn't exist
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        
        if format.lower() == "json":
            # Save as JSON
            report.save(path, crypto_provider=self.crypto_provider)
            
        elif format.lower() == "csv":
            # Save as CSV
            with open(path, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow([
                    "File Path", "File Type", "Pattern Name", "Category", 
                    "Sensitivity", "Matched Content", "Line Number"
                ])
                
                # Write findings
                for finding in report.findings:
                    writer.writerow([
                        finding.get("file_path", ""),
                        finding.get("file_type", ""),
                        finding.get("pattern_name", ""),
                        finding.get("category", ""),
                        finding.get("sensitivity", ""),
                        finding.get("matched_content", ""),
                        finding.get("line_number", "")
                    ])
                    
        elif format.lower() == "html":
            # Save as HTML
            with open(path, 'w') as f:
                f.write(f"<!DOCTYPE html>\n<html>\n<head>\n")
                f.write(f"<title>{report.metadata.report_name}</title>\n")
                f.write("<style>\n")
                f.write("body { font-family: Arial, sans-serif; margin: 20px; }\n")
                f.write("table { border-collapse: collapse; width: 100%; }\n")
                f.write("th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }\n")
                f.write("th { background-color: #f2f2f2; }\n")
                f.write("tr:hover { background-color: #f5f5f5; }\n")
                f.write(".high { background-color: #ffcccc; }\n")
                f.write(".medium { background-color: #fff2cc; }\n")
                f.write(".low { background-color: #e6f2ff; }\n")
                f.write("</style>\n")
                f.write("</head>\n<body>\n")
                
                # Report header
                f.write(f"<h1>{report.metadata.report_name}</h1>\n")
                f.write(f"<p>Generated at: {report.metadata.generated_at}</p>\n")
                
                # Summary section
                f.write("<h2>Summary</h2>\n")
                f.write("<table>\n")
                f.write("<tr><th>Metric</th><th>Value</th></tr>\n")
                for key, value in report.summary.items():
                    f.write(f"<tr><td>{key}</td><td>{value}</td></tr>\n")
                f.write("</table>\n")
                
                # Findings section
                f.write("<h2>Findings</h2>\n")
                if report.findings:
                    f.write("<table>\n")
                    f.write("<tr><th>File Path</th><th>Pattern</th><th>Category</th>")
                    f.write("<th>Sensitivity</th><th>Content</th><th>Line Number</th></tr>\n")
                    
                    for finding in report.findings:
                        sensitivity = finding.get("sensitivity", "").lower()
                        f.write(f"<tr class='{sensitivity}'>")
                        f.write(f"<td>{finding.get('file_path', '')}</td>")
                        f.write(f"<td>{finding.get('pattern_name', '')}</td>")
                        f.write(f"<td>{finding.get('category', '')}</td>")
                        f.write(f"<td>{finding.get('sensitivity', '')}</td>")
                        f.write(f"<td>{finding.get('matched_content', '')}</td>")
                        f.write(f"<td>{finding.get('line_number', '')}</td>")
                        f.write("</tr>\n")
                    
                    f.write("</table>\n")
                else:
                    f.write("<p>No findings to report.</p>\n")
                
                f.write("</body>\n</html>")
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
        return str(path)