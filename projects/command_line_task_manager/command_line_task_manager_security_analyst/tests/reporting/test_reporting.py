"""Tests for the Report Generator module."""

import os
import time
import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, Any

import pytest

from securetask.reporting.redaction import (
    RedactionEngine, RedactionPattern, RedactionLevel
)
from securetask.reporting.generator import (
    ReportGenerator, ReportType, ReportFormat, Report
)
from securetask.findings.models import Finding
from securetask.findings.repository import FindingRepository
from securetask.evidence.vault import EvidenceVault
from securetask.evidence.models import Evidence, EvidenceType, AccessLevel
from securetask.remediation.tracker import RemediationTracker
from securetask.remediation.workflow import RemediationState, RemediationPriority
from securetask.compliance.repository import ComplianceRepository
from securetask.compliance.frameworks import ComplianceControlStatus
from securetask.utils.crypto import CryptoManager


def create_test_finding() -> Finding:
    """Create a test finding for report testing."""
    return Finding(
        id=str(uuid.uuid4()),
        title="SQL Injection in Login Form",
        description="The login form is vulnerable to SQL injection at example.com/login.php via the 'username' parameter. This allows an attacker to bypass authentication and access sensitive data.",
        affected_systems=["web-01.example.com", "web-02.example.com"],
        discovered_date=datetime.now() - timedelta(days=7),
        discovered_by="security_analyst",
        status="open",
        severity="high",
        cvss_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        cvss_score=9.8,
        cvss_severity="Critical",
        remediation_plan="Update login.php to use parameterized queries instead of string concatenation. Implement input validation and consider using a secure authentication library."
    )


def test_redaction_pattern():
    """Test redaction patterns."""
    # Create a redaction pattern for IP addresses
    pattern = RedactionPattern(
        name="ip_address",
        pattern=r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
        replacement="[IP REDACTED]",
        description="IP address",
        levels={RedactionLevel.MEDIUM, RedactionLevel.HIGH, RedactionLevel.MAXIMUM}
    )
    
    # Test text with IP addresses
    test_text = "The server at 192.168.1.1 communicates with 10.0.0.1 over port 443."
    
    # Should not redact at NONE level
    assert pattern.apply(test_text, RedactionLevel.NONE) == test_text
    
    # Should not redact at LOW level
    assert pattern.apply(test_text, RedactionLevel.LOW) == test_text
    
    # Should redact at MEDIUM level
    redacted_medium = pattern.apply(test_text, RedactionLevel.MEDIUM)
    assert redacted_medium == "The server at [IP REDACTED] communicates with [IP REDACTED] over port 443."
    
    # Should redact at HIGH level
    redacted_high = pattern.apply(test_text, RedactionLevel.HIGH)
    assert redacted_high == "The server at [IP REDACTED] communicates with [IP REDACTED] over port 443."
    
    # Test match detection
    assert pattern.matches("Server IP: 192.168.1.1") == True
    assert pattern.matches("No IP addresses here") == False


def test_redaction_engine():
    """Test the redaction engine."""
    engine = RedactionEngine()
    
    # Test text with various sensitive information
    test_text = """
    Server: web-01.internal (192.168.1.1)
    Database connection: jdbc:mysql://db.example.com:3306/users?user=admin&password=s3cr3t
    API Key: api_key="abcdef1234567890abcdef"
    Contact: admin@example.com
    Credit card: 4111-1111-1111-1111
    Authentication: authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
    """
    
    # No redaction
    assert engine.redact_text(test_text, RedactionLevel.NONE) == test_text
    
    # LOW redaction
    low_redacted = engine.redact_text(test_text, RedactionLevel.LOW)
    assert "192.168.1.1" in low_redacted  # IP address remains
    assert "admin@example.com" in low_redacted  # Email remains
    assert "web-01.internal" not in low_redacted  # Internal hostname redacted
    assert "s3cr3t" not in low_redacted  # Password redacted
    assert "abcdef1234567890abcdef" not in low_redacted  # API key redacted
    assert "4111-1111-1111-1111" not in low_redacted  # Credit card redacted
    assert "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in low_redacted  # Auth token redacted
    
    # MEDIUM redaction
    medium_redacted = engine.redact_text(test_text, RedactionLevel.MEDIUM)
    assert "192.168.1.1" not in medium_redacted  # IP address redacted
    assert "admin@example.com" not in medium_redacted  # Email redacted
    assert "web-01.internal" not in medium_redacted  # Internal hostname redacted
    
    # Custom pattern
    engine.add_pattern(RedactionPattern(
        name="custom_pattern",
        pattern=r"Server:\s+(\S+)",
        replacement="Server: [SERVER REDACTED]",
        levels={RedactionLevel.LOW, RedactionLevel.MEDIUM, RedactionLevel.HIGH}
    ))
    
    # Test custom pattern
    custom_redacted = engine.redact_text(test_text, RedactionLevel.LOW)
    assert "Server: [SERVER REDACTED]" in custom_redacted
    
    # Remove pattern
    assert engine.remove_pattern("custom_pattern") == True
    
    # Test dictionary redaction
    test_dict = {
        "server": "web-01.internal",
        "ip": "192.168.1.1",
        "credentials": {
            "username": "admin",
            "password": "s3cr3t"
        },
        "contacts": ["admin@example.com", "user@example.com"]
    }
    
    # Medium redaction of dictionary
    redacted_dict = engine.redact_dict(test_dict, RedactionLevel.MEDIUM)
    assert redacted_dict["server"] != "web-01.internal"  # Redacted
    assert redacted_dict["ip"] != "192.168.1.1"  # Redacted
    assert redacted_dict["credentials"]["password"] != "s3cr3t"  # Redacted
    assert redacted_dict["contacts"][0] != "admin@example.com"  # Redacted
    
    # Field-specific redaction
    field_levels = {
        "server": RedactionLevel.MAXIMUM,
        "credentials": RedactionLevel.HIGH,
        "ip": RedactionLevel.NONE  # Don't redact IP
    }
    
    redacted_field_specific = engine.redact_dict(test_dict, RedactionLevel.LOW, field_levels)
    assert redacted_field_specific["server"] != "web-01.internal"  # Redacted (MAXIMUM)
    assert redacted_field_specific["ip"] == "192.168.1.1"  # Not redacted (NONE)
    assert redacted_field_specific["credentials"]["password"] != "s3cr3t"  # Redacted (HIGH)


def test_report_model():
    """Test the Report model."""
    # Create a report
    report = Report(
        id=str(uuid.uuid4()),
        title="Security Assessment Report",
        type=ReportType.TECHNICAL_SUMMARY,
        content={
            "overview": {
                "title": "Overview",
                "content": "This is an overview of the security assessment."
            },
            "findings": {
                "title": "Findings",
                "content": "These are the findings identified during the assessment."
            }
        },
        generated_at=datetime.now(),
        generated_by="security_analyst",
        redaction_level=RedactionLevel.MEDIUM
    )
    
    # Test dictionary conversion
    report_dict = report.to_dict()
    assert report_dict["id"] == report.id
    assert report_dict["title"] == "Security Assessment Report"
    assert report_dict["type"] == ReportType.TECHNICAL_SUMMARY.value
    assert "overview" in report_dict["content"]
    assert "findings" in report_dict["content"]
    
    # Test JSON conversion
    report_json = report.to_json()
    parsed_json = json.loads(report_json)
    assert parsed_json["id"] == report.id
    
    # Test creation from dictionary
    recreated_report = Report.from_dict(report_dict)
    assert recreated_report.id == report.id
    assert recreated_report.title == "Security Assessment Report"
    assert recreated_report.type == ReportType.TECHNICAL_SUMMARY
    assert recreated_report.redaction_level == RedactionLevel.MEDIUM


def test_report_generator_integration(temp_dir):
    """Test report generator integration with other components."""
    # Create crypto manager for all components
    crypto_manager = CryptoManager()
    
    # Setup findings repository
    findings_dir = os.path.join(temp_dir, "findings")
    findings_repo = FindingRepository(findings_dir, crypto_manager)
    
    # Setup evidence vault
    evidence_dir = os.path.join(temp_dir, "evidence")
    evidence_vault = EvidenceVault(evidence_dir, crypto_manager)
    
    # Setup remediation tracker
    remediation_dir = os.path.join(temp_dir, "remediation")
    remediation_tracker = RemediationTracker(remediation_dir, crypto_manager)
    
    # Setup compliance repository
    compliance_dir = os.path.join(temp_dir, "compliance")
    compliance_repo = ComplianceRepository(compliance_dir, crypto_manager)
    
    # Setup report generator
    report_generator = ReportGenerator(
        findings_repo=findings_repo,
        evidence_vault=evidence_vault,
        remediation_tracker=remediation_tracker,
        compliance_repo=compliance_repo
    )
    
    # Create test data
    # 1. Create findings
    finding1 = Finding(
        id=str(uuid.uuid4()),
        title="SQL Injection in Login Form",
        description="The login form at example.com/login.php is vulnerable to SQL injection via the 'username' parameter. This allows attackers to bypass authentication.",
        affected_systems=["web-01.example.com", "web-02.example.com"],
        discovered_date=datetime.now() - timedelta(days=7),
        discovered_by="security_analyst",
        status="open",
        severity="high",
        cvss_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        cvss_score=9.8,
        cvss_severity="Critical",
        remediation_plan="Update login.php to use parameterized queries instead of string concatenation."
    )
    
    finding2 = Finding(
        id=str(uuid.uuid4()),
        title="Cross-Site Scripting in Comments",
        description="The comment system at example.com/blog does not properly sanitize user input, leading to stored XSS vulnerabilities.",
        affected_systems=["web-02.example.com"],
        discovered_date=datetime.now() - timedelta(days=5),
        discovered_by="security_analyst",
        status="open",
        severity="medium",
        cvss_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N",
        cvss_score=6.1,
        cvss_severity="Medium",
        remediation_plan="Implement proper input sanitization and output encoding for all user-generated content."
    )
    
    # Save findings
    findings_repo.create(finding1)
    findings_repo.create(finding2)
    
    # 2. Create evidence for findings
    # Create a temp file for evidence
    evidence_file = os.path.join(temp_dir, "proof.txt")
    with open(evidence_file, "w") as f:
        f.write("This is proof of the vulnerability. The attack string ' OR 1=1 -- bypasses authentication.")
    
    # Store evidence
    evidence1 = evidence_vault.store(
        file_path=evidence_file,
        title="SQL Injection Proof",
        description="Screenshot showing SQL injection vulnerability",
        evidence_type=EvidenceType.SCREENSHOT,
        uploaded_by="security_analyst"
    )
    
    evidence2 = evidence_vault.store(
        file_path=evidence_file,
        title="XSS Proof",
        description="Screenshot showing XSS vulnerability",
        evidence_type=EvidenceType.SCREENSHOT,
        uploaded_by="security_analyst"
    )
    
    # Link evidence to findings
    finding1.add_evidence(evidence1.id)
    finding2.add_evidence(evidence2.id)
    
    # Update findings with evidence
    findings_repo.update(finding1)
    findings_repo.update(finding2)
    
    # 3. Create remediation tasks
    task1 = remediation_tracker.create_task(
        finding_id=finding1.id,
        title="Fix SQL Injection in Login Form",
        description="Implement parameterized queries in login form",
        priority=RemediationPriority.HIGH,
        created_by="security_analyst",
        due_date=datetime.now() + timedelta(days=7)
    )
    
    task2 = remediation_tracker.create_task(
        finding_id=finding2.id,
        title="Fix XSS in Comments",
        description="Implement input sanitization in comment system",
        priority=RemediationPriority.MEDIUM,
        created_by="security_analyst",
        due_date=datetime.now() + timedelta(days=14)
    )
    
    # 4. Create compliance framework and controls
    pci_framework = compliance_repo.create_framework(
        id="PCI-DSS-4.0",
        name="Payment Card Industry Data Security Standard",
        description="Standard for organizations that handle credit cards",
        version="4.0"
    )
    
    # Add controls
    pci_control1 = compliance_repo.add_control(
        framework_id="PCI-DSS-4.0",
        id="PCI-DSS-6.5.1",
        name="Injection Flaws",
        description="Prevent injection flaws, particularly SQL injection",
        section="6.5.1"
    )
    
    pci_control2 = compliance_repo.add_control(
        framework_id="PCI-DSS-4.0",
        id="PCI-DSS-6.5.7",
        name="Cross-Site Scripting",
        description="Prevent XSS vulnerabilities",
        section="6.5.7"
    )
    
    # Map findings to controls
    compliance_repo.map_finding_to_control(finding1.id, "PCI-DSS-4.0", "PCI-DSS-6.5.1")
    compliance_repo.map_finding_to_control(finding2.id, "PCI-DSS-4.0", "PCI-DSS-6.5.7")
    
    # Update control status
    compliance_repo.update_control_status(
        "PCI-DSS-4.0",
        "PCI-DSS-6.5.1",
        ComplianceControlStatus.NON_COMPLIANT,
        "SQL injection vulnerability found"
    )
    
    compliance_repo.update_control_status(
        "PCI-DSS-4.0",
        "PCI-DSS-6.5.7",
        ComplianceControlStatus.NON_COMPLIANT,
        "XSS vulnerability found"
    )
    
    # Now, generate a report
    report = report_generator.generate_report(
        report_type=ReportType.DETAILED_FINDINGS,
        title="Security Assessment Report for Example.com",
        findings=[finding1.id, finding2.id],
        audience_level=RedactionLevel.MEDIUM,
        report_format=ReportFormat.JSON,
        generated_by="security_analyst",
        metadata={
            "target": "Example.com Web Application",
            "start_date": "2022-01-01",
            "end_date": "2022-01-14",
            "assessment_type": "Penetration Test"
        }
    )
    
    # Test report attributes
    assert report.title == "Security Assessment Report for Example.com"
    assert report.type == ReportType.DETAILED_FINDINGS
    assert report.redaction_level == RedactionLevel.MEDIUM
    assert "Example.com Web Application" in report.metadata.get("target", "")
    
    # Test report content
    assert "overview" in report.content
    assert "findings" in report.content
    
    # Check for redactions in content
    findings_content = report.content["findings"]["content"]
    
    # IP addresses should be redacted at MEDIUM level
    assert "web-01.example.com" not in findings_content
    assert "web-02.example.com" not in findings_content
    
    # Email addresses should be redacted at MEDIUM level
    assert "admin@example.com" not in findings_content
    
    # Render report in different formats
    json_report = report_generator.render_report(report, ReportFormat.JSON)
    assert json_report.startswith("{")
    
    markdown_report = report_generator.render_report(report, ReportFormat.MARKDOWN)
    assert "# Security Assessment Report for Example.com" in markdown_report
    
    html_report = report_generator.render_report(report, ReportFormat.HTML)
    assert "<html>" in html_report
    assert "</html>" in html_report
    
    text_report = report_generator.render_report(report, ReportFormat.TEXT)
    assert "Security Assessment Report for Example.com" in text_report
    
    # Save report to file
    report_file = os.path.join(temp_dir, "report.json")
    report_generator.save_report(report, report_file, ReportFormat.JSON)
    
    assert os.path.exists(report_file)
    
    # Load the report from file and verify content
    with open(report_file, "r") as f:
        saved_report = json.load(f)
        
    assert saved_report["id"] == report.id
    assert saved_report["title"] == report.title
    assert "overview" in saved_report["content"]


def test_report_generator_performance(temp_dir):
    """Test performance of report generation."""
    # Create crypto manager for all components
    crypto_manager = CryptoManager()
    
    # Setup minimal components for performance testing
    findings_dir = os.path.join(temp_dir, "findings")
    findings_repo = FindingRepository(findings_dir, crypto_manager)
    
    evidence_dir = os.path.join(temp_dir, "evidence")
    evidence_vault = EvidenceVault(evidence_dir, crypto_manager)
    
    remediation_dir = os.path.join(temp_dir, "remediation")
    remediation_tracker = RemediationTracker(remediation_dir, crypto_manager)
    
    compliance_dir = os.path.join(temp_dir, "compliance")
    compliance_repo = ComplianceRepository(compliance_dir, crypto_manager)
    
    # Setup report generator
    report_generator = ReportGenerator(
        findings_repo=findings_repo,
        evidence_vault=evidence_vault,
        remediation_tracker=remediation_tracker,
        compliance_repo=compliance_repo
    )
    
    # Create 510 findings (requirement: process 500+ findings in <30 seconds)
    finding_ids = []
    for i in range(510):
        finding = Finding(
            id=str(uuid.uuid4()),
            title=f"Test Finding {i+1}",
            description=f"Description for test finding {i+1}",
            affected_systems=[f"system-{i+1}"],
            discovered_date=datetime.now() - timedelta(days=i % 30),
            discovered_by="performance-tester",
            status="open",
            severity="high" if i % 5 == 0 else "medium" if i % 5 == 1 else "low" if i % 5 == 2 else "critical" if i % 5 == 3 else "info"
        )
        
        # Save finding
        findings_repo.create(finding)
        finding_ids.append(finding.id)
    
    # Measure time to generate report with 510 findings
    start_time = time.time()
    
    report = report_generator.generate_report(
        report_type=ReportType.TECHNICAL_SUMMARY,
        title="Performance Test Report",
        findings=finding_ids,
        audience_level=RedactionLevel.MEDIUM,
        report_format=ReportFormat.JSON,
        generated_by="performance-tester"
    )
    
    generation_time = time.time() - start_time
    
    # Verify time is less than 30 seconds for 510 findings
    assert generation_time < 30.0, f"Report generation took {generation_time:.2f}s for 510 findings, should be <30s"
    
    # Test report render performance (10 pages per second)
    # Estimate a page as 4000 characters
    report_content = report_generator.render_report(report, ReportFormat.TEXT)
    num_pages = len(report_content) / 4000
    
    start_time = time.time()
    
    # Re-render 10 times to simulate multiple pages
    for _ in range(10):
        report_generator.render_report(report, ReportFormat.TEXT)
    
    render_time = time.time() - start_time
    pages_per_second = (10 * num_pages) / render_time
    
    # Verify can process at least 10 pages per second
    assert pages_per_second >= 10, f"Rendering performance: {pages_per_second:.2f} pages/second, should be ≥10"