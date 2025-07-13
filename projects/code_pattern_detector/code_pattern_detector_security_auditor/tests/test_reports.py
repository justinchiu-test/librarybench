"""Tests for report generation."""

import pytest
import json
import xml.etree.ElementTree as ET
import tempfile
from datetime import datetime
from pathlib import Path

from pypatternguard.reports import ReportGenerator
from pypatternguard.models import (
    ScanResult,
    Vulnerability,
    VulnerabilityType,
    SeverityLevel,
    Location,
    ComplianceReport,
    ComplianceRequirement,
    ComplianceFramework,
)


class TestReportGenerator:
    """Test report generation functionality."""
    
    @pytest.fixture
    def sample_scan_result(self):
        """Create a sample scan result."""
        vulnerabilities = [
            Vulnerability(
                id="VULN-001",
                type=VulnerabilityType.INJECTION,
                severity=SeverityLevel.CRITICAL,
                title="SQL Injection",
                description="SQL injection in user query",
                location=Location(
                    file_path=Path("/app/db.py"),
                    line_start=42,
                    line_end=45,
                    column_start=10,
                    column_end=50
                ),
                code_snippet="query = 'SELECT * FROM users WHERE id=' + user_id",
                remediation="Use parameterized queries",
                cwe_ids=["CWE-89"],
                cvss_score=9.8,
                confidence=0.95,
                compliance_mappings={
                    ComplianceFramework.PCI_DSS: ["6.5.1"],
                    ComplianceFramework.SOC2: ["CC6.1"]
                }
            ),
            Vulnerability(
                id="VULN-002",
                type=VulnerabilityType.HARDCODED_SECRET,
                severity=SeverityLevel.HIGH,
                title="Hardcoded Password",
                description="Password hardcoded in source",
                location=Location(
                    file_path=Path("/app/config.py"),
                    line_start=15,
                    line_end=15
                ),
                remediation="Use environment variables",
                confidence=0.9,
                suppressed=True,
                suppression_reason="Test environment only"
            )
        ]
        
        return ScanResult(
            scan_id="scan-001",
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
            target_path=Path("/test/project"),
            total_files_scanned=25,
            total_lines_scanned=5000,
            scan_duration_seconds=12.5,
            vulnerabilities=vulnerabilities,
            scan_errors=[
                {
                    "file": "/test/broken.py",
                    "error": "SyntaxError: invalid syntax",
                    "type": "parse_error"
                }
            ],
            metadata={
                "scanner_version": "1.0.0",
                "config": {"max_workers": 4}
            }
        )
    
    @pytest.fixture
    def sample_compliance_report(self):
        """Create a sample compliance report."""
        requirements = [
            ComplianceRequirement(
                framework=ComplianceFramework.PCI_DSS,
                requirement_id="6.5.1",
                description="Injection flaws",
                vulnerabilities=["VULN-001"],
                status="not_compliant",
                evidence=[{"note": "SQL injection found"}]
            )
        ]
        
        return ComplianceReport(
            report_id="report-001",
            timestamp=datetime(2024, 1, 15, 11, 0, 0),
            scan_result_id="scan-001",
            frameworks=[ComplianceFramework.PCI_DSS, ComplianceFramework.SOC2],
            requirements=requirements,
            executive_summary="1 critical vulnerability found",
            compliance_scores={
                ComplianceFramework.PCI_DSS: 85.0,
                ComplianceFramework.SOC2: 90.0
            },
            recommendations=["Fix SQL injection vulnerability"],
            metadata={"scan_duration": 12.5}
        )
    
    def test_export_json(self, sample_scan_result):
        """Test exporting scan results as JSON."""
        generator = ReportGenerator()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.export(sample_scan_result, str(output_path), "json")
            
            # Verify file exists and is valid JSON
            assert output_path.exists()
            
            with open(output_path, 'r') as f:
                data = json.load(f)
            
            # Verify structure
            assert data["scan_id"] == "scan-001"
            assert data["total_files_scanned"] == 25
            assert data["total_lines_scanned"] == 5000
            assert len(data["vulnerabilities"]) == 2
            assert len(data["scan_errors"]) == 1
            
            # Verify vulnerability data
            vuln = data["vulnerabilities"][0]
            assert vuln["id"] == "VULN-001"
            assert vuln["severity"] == "critical"
            assert vuln["type"] == "injection"
            
            # Verify paths are strings
            assert isinstance(data["target_path"], str)
            assert isinstance(vuln["location"]["file_path"], str)
        
        finally:
            output_path.unlink()
    
    def test_export_xml(self, sample_scan_result):
        """Test exporting scan results as XML."""
        generator = ReportGenerator()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.export(sample_scan_result, str(output_path), "xml")
            
            # Verify file exists and is valid XML
            assert output_path.exists()
            
            tree = ET.parse(output_path)
            root = tree.getroot()
            
            assert root.tag == "SecurityScanResult"
            
            # Check metadata
            metadata = root.find("Metadata")
            assert metadata.find("ScanID").text == "scan-001"
            assert metadata.find("FilesScanned").text == "25"
            assert metadata.find("LinesScanned").text == "5000"
            
            # Check vulnerabilities
            vulnerabilities = root.find("Vulnerabilities")
            vuln_elements = vulnerabilities.findall("Vulnerability")
            assert len(vuln_elements) == 2
            
            # Check first vulnerability
            vuln = vuln_elements[0]
            assert vuln.find("ID").text == "VULN-001"
            assert vuln.find("Severity").text == "critical"
            assert vuln.find("Type").text == "injection"
            
            # Check location
            location = vuln.find("Location")
            assert location.find("LineStart").text == "42"
            assert location.find("LineEnd").text == "45"
            
            # Check CWE IDs
            cwe_ids = vuln.find("CWEIDs")
            assert cwe_ids.find("CWE").text == "CWE-89"
            
            # Check compliance mappings
            compliance = vuln.find("ComplianceMappings")
            pci_dss = compliance.find("PCI-DSS")
            assert pci_dss.find("Requirement").text == "6.5.1"
        
        finally:
            output_path.unlink()
    
    def test_export_invalid_format(self, sample_scan_result):
        """Test exporting with invalid format."""
        generator = ReportGenerator()
        
        with pytest.raises(ValueError, match="Unsupported format"):
            generator.export(sample_scan_result, "output.txt", "txt")
    
    def test_export_compliance_report_json(self, sample_compliance_report):
        """Test exporting compliance report as JSON."""
        generator = ReportGenerator()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate_compliance_report_file(
                sample_compliance_report, str(output_path), "json"
            )
            
            with open(output_path, 'r') as f:
                data = json.load(f)
            
            assert data["report_id"] == "report-001"
            assert data["scan_result_id"] == "scan-001"
            assert len(data["frameworks"]) == 2
            assert len(data["requirements"]) == 1
            assert data["compliance_scores"]["PCI-DSS"] == 85.0
        
        finally:
            output_path.unlink()
    
    def test_export_compliance_report_xml(self, sample_compliance_report):
        """Test exporting compliance report as XML."""
        generator = ReportGenerator()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.generate_compliance_report_file(
                sample_compliance_report, str(output_path), "xml"
            )
            
            tree = ET.parse(output_path)
            root = tree.getroot()
            
            assert root.tag == "ComplianceReport"
            assert root.find("ReportID").text == "report-001"
            assert root.find("ScanResultID").text == "scan-001"
            
            # Check frameworks
            frameworks = root.find("Frameworks")
            framework_elements = frameworks.findall("Framework")
            assert len(framework_elements) == 2
            
            # Check compliance scores
            scores = root.find("ComplianceScores")
            assert scores.find("PCI-DSS").text == "85.00"
            
            # Check requirements
            requirements = root.find("Requirements")
            req_elements = requirements.findall("Requirement")
            assert len(req_elements) == 1
            
            req = req_elements[0]
            assert req.find("Framework").text == "PCI-DSS"
            assert req.find("ID").text == "6.5.1"
            assert req.find("Status").text == "not_compliant"
        
        finally:
            output_path.unlink()
    
    def test_summary_stats_in_xml(self, sample_scan_result):
        """Test that summary stats are included in XML export."""
        generator = ReportGenerator()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.export(sample_scan_result, str(output_path), "xml")
            
            tree = ET.parse(output_path)
            root = tree.getroot()
            
            summary = root.find("Summary")
            assert summary is not None
            
            # Check that summary contains expected fields
            assert summary.find("total_vulnerabilities") is not None
            assert summary.find("files_scanned") is not None
            assert summary.find("scan_duration") is not None
            
            # Check severity distribution
            severity_dist = summary.find("severity_distribution")
            assert severity_dist is not None
            assert severity_dist.find("critical") is not None
            assert severity_dist.find("high") is not None
        
        finally:
            output_path.unlink()
    
    def test_scan_errors_in_export(self, sample_scan_result):
        """Test that scan errors are included in exports."""
        generator = ReportGenerator()
        
        # Test JSON
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json_path = Path(f.name)
        
        try:
            generator.export(sample_scan_result, str(json_path), "json")
            
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            assert "scan_errors" in data
            assert len(data["scan_errors"]) == 1
            assert data["scan_errors"][0]["type"] == "parse_error"
        
        finally:
            json_path.unlink()
        
        # Test XML
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            xml_path = Path(f.name)
        
        try:
            generator.export(sample_scan_result, str(xml_path), "xml")
            
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            errors = root.find("ScanErrors")
            assert errors is not None
            error_elements = errors.findall("Error")
            assert len(error_elements) == 1
            assert error_elements[0].find("type").text == "parse_error"
        
        finally:
            xml_path.unlink()
    
    def test_code_snippet_in_export(self, sample_scan_result):
        """Test that code snippets are included in exports."""
        generator = ReportGenerator()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            generator.export(sample_scan_result, str(output_path), "json")
            
            with open(output_path, 'r') as f:
                data = json.load(f)
            
            # First vulnerability has code snippet
            vuln = data["vulnerabilities"][0]
            assert "code_snippet" in vuln
            assert "SELECT * FROM users" in vuln["code_snippet"]
        
        finally:
            output_path.unlink()