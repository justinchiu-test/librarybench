"""Tests for data models."""

import pytest
from datetime import datetime
from pathlib import Path

from pypatternguard.models import (
    Vulnerability,
    VulnerabilityType,
    SeverityLevel,
    Location,
    ScanResult,
    ComplianceReport,
    ComplianceRequirement,
    ComplianceFramework,
    SuppressionRule,
)


class TestVulnerability:
    """Test Vulnerability model."""
    
    def test_vulnerability_creation(self):
        """Test creating a vulnerability."""
        vuln = Vulnerability(
            id="TEST-001",
            type=VulnerabilityType.INJECTION,
            severity=SeverityLevel.CRITICAL,
            title="SQL Injection",
            description="Test SQL injection vulnerability",
            location=Location(
                file_path=Path("/test/file.py"),
                line_start=10,
                line_end=15
            ),
            remediation="Use parameterized queries",
            confidence=0.95
        )
        
        assert vuln.id == "TEST-001"
        assert vuln.type == VulnerabilityType.INJECTION
        assert vuln.severity == SeverityLevel.CRITICAL
        assert vuln.confidence == 0.95
        assert not vuln.false_positive
        assert not vuln.suppressed
    
    def test_risk_score_calculation(self):
        """Test risk score calculation."""
        vuln_critical = Vulnerability(
            id="TEST-001",
            type=VulnerabilityType.INJECTION,
            severity=SeverityLevel.CRITICAL,
            title="Critical Issue",
            description="Test",
            location=Location(file_path=Path("/test.py"), line_start=1, line_end=1),
            remediation="Fix it",
            confidence=0.9
        )
        
        vuln_low = Vulnerability(
            id="TEST-002",
            type=VulnerabilityType.INSUFFICIENT_LOGGING,
            severity=SeverityLevel.LOW,
            title="Low Issue",
            description="Test",
            location=Location(file_path=Path("/test.py"), line_start=1, line_end=1),
            remediation="Fix it",
            confidence=0.8
        )
        
        assert vuln_critical.get_risk_score() == 9.0  # 10.0 * 0.9
        assert vuln_low.get_risk_score() == 1.6  # 2.0 * 0.8
    
    def test_compliance_mappings(self):
        """Test compliance mappings."""
        vuln = Vulnerability(
            id="TEST-001",
            type=VulnerabilityType.CRYPTO_FAILURE,
            severity=SeverityLevel.HIGH,
            title="Weak Crypto",
            description="Test",
            location=Location(file_path=Path("/test.py"), line_start=1, line_end=1),
            remediation="Use strong crypto",
            confidence=0.9,
            compliance_mappings={
                ComplianceFramework.PCI_DSS: ["3.4", "4.1"],
                ComplianceFramework.SOC2: ["CC6.1"]
            }
        )
        
        assert ComplianceFramework.PCI_DSS in vuln.compliance_mappings
        assert "3.4" in vuln.compliance_mappings[ComplianceFramework.PCI_DSS]
        assert len(vuln.compliance_mappings[ComplianceFramework.SOC2]) == 1


class TestScanResult:
    """Test ScanResult model."""
    
    def test_scan_result_creation(self):
        """Test creating a scan result."""
        scan_result = ScanResult(
            scan_id="scan-123",
            timestamp=datetime.now(),
            target_path=Path("/project"),
            total_files_scanned=10,
            total_lines_scanned=1000,
            scan_duration_seconds=5.5,
            vulnerabilities=[]
        )
        
        assert scan_result.scan_id == "scan-123"
        assert scan_result.total_files_scanned == 10
        assert scan_result.total_lines_scanned == 1000
        assert scan_result.scan_duration_seconds == 5.5
        assert len(scan_result.vulnerabilities) == 0
    
    def test_vulnerabilities_by_severity(self):
        """Test grouping vulnerabilities by severity."""
        vulnerabilities = [
            Vulnerability(
                id=f"TEST-{i}",
                type=VulnerabilityType.INJECTION,
                severity=severity,
                title=f"Test {severity.value}",
                description="Test",
                location=Location(file_path=Path("/test.py"), line_start=i, line_end=i),
                remediation="Fix it",
                confidence=0.9,
                suppressed=(i == 3)  # Suppress one vulnerability
            )
            for i, severity in enumerate([
                SeverityLevel.CRITICAL,
                SeverityLevel.CRITICAL,
                SeverityLevel.HIGH,
                SeverityLevel.HIGH,  # This one is suppressed
                SeverityLevel.MEDIUM,
                SeverityLevel.LOW,
            ])
        ]
        
        scan_result = ScanResult(
            scan_id="scan-123",
            timestamp=datetime.now(),
            target_path=Path("/project"),
            total_files_scanned=1,
            total_lines_scanned=100,
            scan_duration_seconds=1.0,
            vulnerabilities=vulnerabilities
        )
        
        by_severity = scan_result.get_vulnerabilities_by_severity()
        
        assert len(by_severity[SeverityLevel.CRITICAL]) == 2
        assert len(by_severity[SeverityLevel.HIGH]) == 1  # One is suppressed
        assert len(by_severity[SeverityLevel.MEDIUM]) == 1
        assert len(by_severity[SeverityLevel.LOW]) == 1
        assert len(by_severity[SeverityLevel.INFO]) == 0
    
    def test_summary_stats(self):
        """Test summary statistics."""
        vulnerabilities = [
            Vulnerability(
                id=f"TEST-{i}",
                type=VulnerabilityType.INJECTION,
                severity=SeverityLevel.HIGH,
                title="Test",
                description="Test",
                location=Location(file_path=Path("/test.py"), line_start=i, line_end=i),
                remediation="Fix it",
                confidence=0.9,
                suppressed=(i < 2),
                false_positive=(i == 3)
            )
            for i in range(5)
        ]
        
        scan_result = ScanResult(
            scan_id="scan-123",
            timestamp=datetime.now(),
            target_path=Path("/project"),
            total_files_scanned=10,
            total_lines_scanned=1000,
            scan_duration_seconds=5.5,
            vulnerabilities=vulnerabilities
        )
        
        stats = scan_result.get_summary_stats()
        
        assert stats["total_vulnerabilities"] == 3  # 5 total - 2 suppressed
        assert stats["suppressed_count"] == 2
        assert stats["false_positive_count"] == 1
        assert stats["files_scanned"] == 10
        assert stats["lines_scanned"] == 1000
        assert stats["scan_duration"] == 5.5


class TestComplianceReport:
    """Test ComplianceReport model."""
    
    def test_compliance_report_creation(self):
        """Test creating a compliance report."""
        requirements = [
            ComplianceRequirement(
                framework=ComplianceFramework.PCI_DSS,
                requirement_id="6.5.1",
                description="Injection flaws",
                vulnerabilities=["VULN-001", "VULN-002"],
                status="not_compliant"
            ),
            ComplianceRequirement(
                framework=ComplianceFramework.SOC2,
                requirement_id="CC6.1",
                description="Logical access controls",
                vulnerabilities=[],
                status="compliant"
            )
        ]
        
        report = ComplianceReport(
            report_id="report-123",
            timestamp=datetime.now(),
            scan_result_id="scan-123",
            frameworks=[ComplianceFramework.PCI_DSS, ComplianceFramework.SOC2],
            requirements=requirements,
            executive_summary="Test summary",
            compliance_scores={
                ComplianceFramework.PCI_DSS: 75.0,
                ComplianceFramework.SOC2: 100.0
            },
            recommendations=["Fix injection vulnerabilities"]
        )
        
        assert report.report_id == "report-123"
        assert len(report.requirements) == 2
        assert report.compliance_scores[ComplianceFramework.PCI_DSS] == 75.0
        assert report.compliance_scores[ComplianceFramework.SOC2] == 100.0
        assert len(report.recommendations) == 1


class TestSuppressionRule:
    """Test SuppressionRule model."""
    
    def test_suppression_rule_creation(self):
        """Test creating a suppression rule."""
        rule = SuppressionRule(
            id="suppress-001",
            pattern="TEST-.*",
            reason="Test pattern false positive",
            created_at=datetime.now(),
            created_by="security_team",
            active=True
        )
        
        assert rule.id == "suppress-001"
        assert rule.pattern == "TEST-.*"
        assert rule.reason == "Test pattern false positive"
        assert rule.active
        assert rule.expires_at is None
        assert rule.approved_by is None