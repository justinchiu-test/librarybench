"""Tests for compliance mapping functionality."""

import pytest
from datetime import datetime
from pathlib import Path

from pypatternguard.compliance import ComplianceMapper
from pypatternguard.models import (
    ScanResult,
    Vulnerability,
    VulnerabilityType,
    SeverityLevel,
    Location,
    ComplianceFramework,
)


class TestComplianceMapper:
    """Test compliance mapping functionality."""
    
    @pytest.fixture
    def sample_scan_result(self):
        """Create a sample scan result with various vulnerabilities."""
        vulnerabilities = [
            # SQL Injection
            Vulnerability(
                id="SQLI-001",
                type=VulnerabilityType.INJECTION,
                severity=SeverityLevel.CRITICAL,
                title="SQL Injection",
                description="SQL injection vulnerability",
                location=Location(
                    file_path=Path("/app/db.py"),
                    line_start=50,
                    line_end=50
                ),
                remediation="Use parameterized queries",
                confidence=0.95
            ),
            # Hardcoded Secret
            Vulnerability(
                id="SEC-001",
                type=VulnerabilityType.HARDCODED_SECRET,
                severity=SeverityLevel.HIGH,
                title="Hardcoded API Key",
                description="API key hardcoded in source",
                location=Location(
                    file_path=Path("/app/config.py"),
                    line_start=10,
                    line_end=10
                ),
                remediation="Use environment variables",
                confidence=0.9
            ),
            # Crypto Failure
            Vulnerability(
                id="CRYPTO-001",
                type=VulnerabilityType.CRYPTO_FAILURE,
                severity=SeverityLevel.HIGH,
                title="Weak Hashing Algorithm",
                description="MD5 used for password hashing",
                location=Location(
                    file_path=Path("/app/auth.py"),
                    line_start=30,
                    line_end=30
                ),
                remediation="Use bcrypt or scrypt",
                confidence=0.95
            ),
            # XSS
            Vulnerability(
                id="XSS-001",
                type=VulnerabilityType.XSS,
                severity=SeverityLevel.HIGH,
                title="Cross-Site Scripting",
                description="Unescaped user input",
                location=Location(
                    file_path=Path("/app/views.py"),
                    line_start=100,
                    line_end=100
                ),
                remediation="Escape user input",
                confidence=0.85
            ),
            # Suppressed vulnerability (should not appear in compliance report)
            Vulnerability(
                id="SUPP-001",
                type=VulnerabilityType.COMPONENTS_VULNERABILITIES,
                severity=SeverityLevel.MEDIUM,
                title="Outdated Component",
                description="Using outdated library",
                location=Location(
                    file_path=Path("/requirements.txt"),
                    line_start=5,
                    line_end=5
                ),
                remediation="Update library",
                confidence=0.8,
                suppressed=True
            )
        ]
        
        return ScanResult(
            scan_id="test-scan-001",
            timestamp=datetime.now(),
            target_path=Path("/test/project"),
            total_files_scanned=10,
            total_lines_scanned=1000,
            scan_duration_seconds=5.5,
            vulnerabilities=vulnerabilities
        )
    
    def test_generate_compliance_report(self, sample_scan_result):
        """Test generating a compliance report."""
        mapper = ComplianceMapper()
        report = mapper.generate_report(sample_scan_result)
        
        assert report.report_id
        assert report.timestamp
        assert report.scan_result_id == sample_scan_result.scan_id
        assert ComplianceFramework.PCI_DSS in report.frameworks
        assert ComplianceFramework.SOC2 in report.frameworks
        assert len(report.requirements) > 0
        assert report.executive_summary
        assert report.compliance_scores
        assert len(report.recommendations) > 0
    
    def test_pci_dss_mappings(self, sample_scan_result):
        """Test PCI-DSS requirement mappings."""
        mapper = ComplianceMapper()
        report = mapper.generate_report(sample_scan_result)
        
        pci_requirements = [
            req for req in report.requirements 
            if req.framework == ComplianceFramework.PCI_DSS
        ]
        
        # Check that vulnerabilities are mapped to correct requirements
        req_6_5_1 = next((r for r in pci_requirements if r.requirement_id == "6.5.1"), None)
        assert req_6_5_1
        assert "SQLI-001" in req_6_5_1.vulnerabilities
        assert req_6_5_1.status == "not_compliant"
        
        req_3_4 = next((r for r in pci_requirements if r.requirement_id == "3.4"), None)
        assert req_3_4
        assert "CRYPTO-001" in req_3_4.vulnerabilities
        
        req_8_2_1 = next((r for r in pci_requirements if r.requirement_id == "8.2.1"), None)
        assert req_8_2_1
        assert "SEC-001" in req_8_2_1.vulnerabilities
    
    def test_soc2_mappings(self, sample_scan_result):
        """Test SOC2 control mappings."""
        mapper = ComplianceMapper()
        report = mapper.generate_report(sample_scan_result)
        
        soc2_requirements = [
            req for req in report.requirements 
            if req.framework == ComplianceFramework.SOC2
        ]
        
        # Check SOC2 controls
        cc6_1 = next((r for r in soc2_requirements if r.requirement_id == "CC6.1"), None)
        assert cc6_1
        assert len(cc6_1.vulnerabilities) > 0  # Multiple vulns map to CC6.1
        assert cc6_1.status == "not_compliant"
    
    def test_compliance_scores(self, sample_scan_result):
        """Test compliance score calculation."""
        mapper = ComplianceMapper()
        report = mapper.generate_report(sample_scan_result)
        
        assert ComplianceFramework.PCI_DSS in report.compliance_scores
        assert ComplianceFramework.SOC2 in report.compliance_scores
        
        # Scores should be percentages
        for framework, score in report.compliance_scores.items():
            assert 0 <= score <= 100
    
    def test_suppressed_vulnerabilities_excluded(self, sample_scan_result):
        """Test that suppressed vulnerabilities are excluded from compliance report."""
        mapper = ComplianceMapper()
        report = mapper.generate_report(sample_scan_result)
        
        # Suppressed vulnerability should not appear in any requirements
        all_vuln_ids = []
        for req in report.requirements:
            all_vuln_ids.extend(req.vulnerabilities)
        
        assert "SUPP-001" not in all_vuln_ids
    
    def test_executive_summary_generation(self, sample_scan_result):
        """Test executive summary generation."""
        mapper = ComplianceMapper()
        report = mapper.generate_report(sample_scan_result)
        
        summary = report.executive_summary
        
        # Should contain vulnerability counts
        assert "1" in summary  # 1 critical
        assert "3" in summary  # 3 high
        
        # Should contain compliance status
        assert "PCI-DSS" in summary
        assert "SOC2" in summary
        
        # Should have immediate action warning for critical vulnerabilities
        assert "IMMEDIATE ACTION REQUIRED" in summary
    
    def test_recommendations_generation(self, sample_scan_result):
        """Test recommendations generation."""
        mapper = ComplianceMapper()
        report = mapper.generate_report(sample_scan_result)
        
        recommendations = report.recommendations
        
        # Should have critical vulnerability recommendation
        assert any("CRITICAL" in rec for rec in recommendations)
        
        # Should have crypto recommendation
        assert any("cryptographic" in rec.lower() for rec in recommendations)
        
        # Should have input validation recommendation
        assert any("input validation" in rec.lower() for rec in recommendations)
        
        # Should have secret management recommendation
        assert any("secret" in rec.lower() for rec in recommendations)
        
        # Should have general recommendations
        assert any("CI/CD" in rec for rec in recommendations)
        assert any("training" in rec for rec in recommendations)
    
    def test_compliant_requirements(self):
        """Test handling of compliant requirements."""
        # Create scan result with no vulnerabilities
        clean_scan = ScanResult(
            scan_id="clean-scan",
            timestamp=datetime.now(),
            target_path=Path("/clean/project"),
            total_files_scanned=10,
            total_lines_scanned=1000,
            scan_duration_seconds=5.0,
            vulnerabilities=[]
        )
        
        mapper = ComplianceMapper()
        report = mapper.generate_report(clean_scan)
        
        # All requirements should be compliant
        for req in report.requirements:
            assert req.status == "compliant"
            assert len(req.vulnerabilities) == 0
        
        # Compliance scores should be 100%
        for framework, score in report.compliance_scores.items():
            assert score == 100.0
        
        # Should not have critical warning in summary
        assert "IMMEDIATE ACTION REQUIRED" not in report.executive_summary
    
    def test_metadata_in_report(self, sample_scan_result):
        """Test metadata is included in compliance report."""
        mapper = ComplianceMapper()
        report = mapper.generate_report(sample_scan_result)
        
        assert "total_vulnerabilities" in report.metadata
        assert "critical_count" in report.metadata
        assert "high_count" in report.metadata
        
        # Verify counts (excluding suppressed)
        assert report.metadata["total_vulnerabilities"] == 4
        assert report.metadata["critical_count"] == 1
        assert report.metadata["high_count"] == 3
    
    def test_all_pci_dss_requirements_present(self):
        """Test that all PCI-DSS requirements are present even if compliant."""
        clean_scan = ScanResult(
            scan_id="clean-scan",
            timestamp=datetime.now(),
            target_path=Path("/clean/project"),
            total_files_scanned=1,
            total_lines_scanned=100,
            scan_duration_seconds=1.0,
            vulnerabilities=[]
        )
        
        mapper = ComplianceMapper()
        report = mapper.generate_report(clean_scan)
        
        pci_requirements = [
            req for req in report.requirements 
            if req.framework == ComplianceFramework.PCI_DSS
        ]
        
        # Check that all defined PCI-DSS requirements are present
        expected_requirements = set(mapper.PCI_DSS_REQUIREMENTS.keys())
        actual_requirements = {req.requirement_id for req in pci_requirements}
        
        assert expected_requirements == actual_requirements