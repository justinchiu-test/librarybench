"""Report generation functionality."""

import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from .models import ScanResult, ComplianceReport, Vulnerability, SeverityLevel


class ReportGenerator:
    """Generates reports in various formats."""
    
    def export(self, scan_result: ScanResult, output_path: str, format: str = "json") -> None:
        """Export scan results to file."""
        output = Path(output_path)
        
        if format == "json":
            self._export_json(scan_result, output)
        elif format == "xml":
            self._export_xml(scan_result, output)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_json(self, scan_result: ScanResult, output_path: Path) -> None:
        """Export results as JSON."""
        data = scan_result.model_dump()
        
        # Convert Path objects to strings
        data = self._convert_paths_to_strings(data)
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _export_xml(self, scan_result: ScanResult, output_path: Path) -> None:
        """Export results as XML."""
        root = ET.Element("SecurityScanResult")
        
        # Add metadata
        metadata = ET.SubElement(root, "Metadata")
        ET.SubElement(metadata, "ScanID").text = scan_result.scan_id
        ET.SubElement(metadata, "Timestamp").text = scan_result.timestamp.isoformat()
        ET.SubElement(metadata, "TargetPath").text = str(scan_result.target_path)
        ET.SubElement(metadata, "FilesScanned").text = str(scan_result.total_files_scanned)
        ET.SubElement(metadata, "LinesScanned").text = str(scan_result.total_lines_scanned)
        ET.SubElement(metadata, "Duration").text = f"{scan_result.scan_duration_seconds:.2f}"
        
        # Add summary
        summary = ET.SubElement(root, "Summary")
        stats = scan_result.get_summary_stats()
        for key, value in stats.items():
            if isinstance(value, dict):
                sub_elem = ET.SubElement(summary, key)
                for sub_key, sub_value in value.items():
                    ET.SubElement(sub_elem, sub_key).text = str(sub_value)
            else:
                ET.SubElement(summary, key).text = str(value)
        
        # Add vulnerabilities
        vulns_elem = ET.SubElement(root, "Vulnerabilities")
        for vuln in scan_result.vulnerabilities:
            vuln_elem = ET.SubElement(vulns_elem, "Vulnerability")
            self._add_vulnerability_xml(vuln_elem, vuln)
        
        # Add errors if any
        if scan_result.scan_errors:
            errors_elem = ET.SubElement(root, "ScanErrors")
            for error in scan_result.scan_errors:
                error_elem = ET.SubElement(errors_elem, "Error")
                for key, value in error.items():
                    ET.SubElement(error_elem, key).text = str(value)
        
        # Write to file
        tree = ET.ElementTree(root)
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
    
    def _add_vulnerability_xml(self, parent: ET.Element, vuln: Vulnerability) -> None:
        """Add vulnerability to XML element."""
        ET.SubElement(parent, "ID").text = vuln.id
        ET.SubElement(parent, "Type").text = vuln.type.value
        ET.SubElement(parent, "Severity").text = vuln.severity.value
        ET.SubElement(parent, "Title").text = vuln.title
        ET.SubElement(parent, "Description").text = vuln.description
        
        # Location
        location = ET.SubElement(parent, "Location")
        ET.SubElement(location, "File").text = str(vuln.location.file_path)
        ET.SubElement(location, "LineStart").text = str(vuln.location.line_start)
        ET.SubElement(location, "LineEnd").text = str(vuln.location.line_end)
        
        # Other fields
        ET.SubElement(parent, "Remediation").text = vuln.remediation
        ET.SubElement(parent, "Confidence").text = f"{vuln.confidence:.2f}"
        ET.SubElement(parent, "Suppressed").text = str(vuln.suppressed)
        
        if vuln.code_snippet:
            ET.SubElement(parent, "CodeSnippet").text = vuln.code_snippet
        
        if vuln.cwe_ids:
            cwe_elem = ET.SubElement(parent, "CWEIDs")
            for cwe in vuln.cwe_ids:
                ET.SubElement(cwe_elem, "CWE").text = cwe
        
        if vuln.compliance_mappings:
            compliance_elem = ET.SubElement(parent, "ComplianceMappings")
            for framework, requirements in vuln.compliance_mappings.items():
                framework_elem = ET.SubElement(compliance_elem, framework)
                for req in requirements:
                    ET.SubElement(framework_elem, "Requirement").text = req
    
    def _convert_paths_to_strings(self, obj: Any) -> Any:
        """Recursively convert Path objects to strings."""
        if isinstance(obj, Path):
            return str(obj)
        elif isinstance(obj, dict):
            return {k: self._convert_paths_to_strings(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_paths_to_strings(item) for item in obj]
        else:
            return obj
    
    def generate_compliance_report_file(self, compliance_report: ComplianceReport, 
                                      output_path: str, format: str = "json") -> None:
        """Generate compliance report file."""
        output = Path(output_path)
        
        if format == "json":
            data = compliance_report.model_dump()
            with open(output, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        elif format == "xml":
            self._export_compliance_xml(compliance_report, output)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_compliance_xml(self, report: ComplianceReport, output_path: Path) -> None:
        """Export compliance report as XML."""
        root = ET.Element("ComplianceReport")
        
        # Metadata
        ET.SubElement(root, "ReportID").text = report.report_id
        ET.SubElement(root, "Timestamp").text = report.timestamp.isoformat()
        ET.SubElement(root, "ScanResultID").text = report.scan_result_id
        
        # Executive Summary
        ET.SubElement(root, "ExecutiveSummary").text = report.executive_summary
        
        # Frameworks
        frameworks_elem = ET.SubElement(root, "Frameworks")
        for framework in report.frameworks:
            ET.SubElement(frameworks_elem, "Framework").text = framework.value
        
        # Compliance Scores
        scores_elem = ET.SubElement(root, "ComplianceScores")
        for framework, score in report.compliance_scores.items():
            score_elem = ET.SubElement(scores_elem, framework.value)
            score_elem.text = f"{score:.2f}"
        
        # Requirements
        requirements_elem = ET.SubElement(root, "Requirements")
        for req in report.requirements:
            req_elem = ET.SubElement(requirements_elem, "Requirement")
            ET.SubElement(req_elem, "Framework").text = req.framework.value
            ET.SubElement(req_elem, "ID").text = req.requirement_id
            ET.SubElement(req_elem, "Description").text = req.description
            ET.SubElement(req_elem, "Status").text = req.status
            
            if req.vulnerabilities:
                vulns_elem = ET.SubElement(req_elem, "Vulnerabilities")
                for vuln_id in req.vulnerabilities:
                    ET.SubElement(vulns_elem, "VulnerabilityID").text = vuln_id
        
        # Recommendations
        recommendations_elem = ET.SubElement(root, "Recommendations")
        for rec in report.recommendations:
            ET.SubElement(recommendations_elem, "Recommendation").text = rec
        
        # Write to file
        tree = ET.ElementTree(root)
        tree.write(output_path, encoding='utf-8', xml_declaration=True)