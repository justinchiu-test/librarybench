"""
Compliance report generation.

This module provides tools for generating compliance reports mapped to 
specific regulatory frameworks.
"""

import os
import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Set, Optional, Any, Union, Type

from pydantic import BaseModel, Field

# Import from common library
from common.core.base import Serializable
from common.core.reporting import BaseReporter, ReportFormat
from common.utils.crypto import CryptoProvider
from common.utils.types import ScanResult as CommonScanResult
from common.utils.types import ScanSummary as CommonScanSummary

# Import from local package
from file_system_analyzer.detection.scanner import ScanResult, ScanSummary, SensitiveDataMatch
from file_system_analyzer.detection.patterns import ComplianceCategory, SensitivityLevel
from file_system_analyzer.reporting.frameworks import (
    ComplianceFramework, 
    ComplianceRequirement,
    RiskLevel,
    FrameworkRegistry
)


class FindingStatus(str, Enum):
    """Status of a compliance finding."""
    NEW = "new"
    KNOWN = "known"
    REMEDIATED = "remediated"
    FALSE_POSITIVE = "false_positive"
    ACCEPTED_RISK = "accepted_risk"


class ComplianceFinding(BaseModel, Serializable):
    """A compliance finding related to a specific regulatory requirement."""
    finding_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    requirement_id: str
    file_path: str
    matched_content: str
    context: str
    risk_level: RiskLevel
    sensitivity: SensitivityLevel
    category: ComplianceCategory
    status: FindingStatus = FindingStatus.NEW
    remediation_guidance: str
    related_matches: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    
    # Implement Serializable interface
    def to_dict(self) -> dict:
        """Convert to a dictionary suitable for serialization."""
        data = self.model_dump()
        data["timestamp"] = data["timestamp"].isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ComplianceFinding':
        """Create a ComplianceFinding from a dictionary."""
        if "timestamp" in data and isinstance(data["timestamp"], str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


class ComplianceReport(BaseModel, Serializable):
    """A report of compliance findings for a specific regulatory framework."""
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    framework_id: str
    framework_name: str
    generation_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    scan_summary: ScanSummary
    findings: Dict[str, List[ComplianceFinding]] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    verification_info: Optional[Dict[str, Any]] = None
    
    @property
    def total_findings(self) -> int:
        """Get the total number of findings in the report."""
        return sum(len(findings) for findings in self.findings.values())
    
    @property
    def findings_by_risk(self) -> Dict[RiskLevel, int]:
        """Get a count of findings by risk level."""
        result = {level: 0 for level in RiskLevel}
        for req_findings in self.findings.values():
            for finding in req_findings:
                result[finding.risk_level] += 1
        return result
    
    @property
    def findings_by_status(self) -> Dict[FindingStatus, int]:
        """Get a count of findings by status."""
        result = {status: 0 for status in FindingStatus}
        for req_findings in self.findings.values():
            for finding in req_findings:
                result[finding.status] += 1
        return result
    
    def sign(self, crypto_provider: CryptoProvider) -> None:
        """Sign the report with cryptographic verification."""
        # Create a canonical representation of the report
        report_data = self.model_dump(exclude={"verification_info"})
        report_json = json.dumps(report_data, sort_keys=True, default=str).encode()
        
        # Create a hash of the report
        report_hash = crypto_provider.secure_hash(report_json)
        
        # Create a timestamped signature
        signature = crypto_provider.timestamp_signature(report_json)
        
        self.verification_info = {
            "report_hash": report_hash,
            "signature": signature,
            "verification_method": "crypto_provider",
            "key_id": crypto_provider.key_id
        }
    
    def verify(self, crypto_provider: CryptoProvider) -> bool:
        """Verify the cryptographic signature of the report."""
        if not self.verification_info:
            return False
            
        # Recreate the report data without verification_info
        report_data = self.model_dump(exclude={"verification_info"})
        report_json = json.dumps(report_data, sort_keys=True, default=str).encode()
        
        # Verify the hash
        calculated_hash = crypto_provider.secure_hash(report_json)
        stored_hash = self.verification_info.get("report_hash")
        if calculated_hash != stored_hash:
            return False
            
        # Verify the signature
        signature = self.verification_info.get("signature", {})
        return crypto_provider.verify_timestamped_signature(report_json, signature)
    
    def to_json(self) -> str:
        """Convert the report to a JSON string."""
        return json.dumps(self.to_dict(), default=str)
    
    def save(self, file_path: str, verify: bool = False, crypto_provider: Optional[CryptoProvider] = None) -> None:
        """Save the report to a file, optionally with verification."""
        if verify and crypto_provider and not self.verification_info:
            self.sign(crypto_provider)
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w') as f:
            f.write(self.to_json())
    
    # Implement Serializable interface
    def to_dict(self) -> dict:
        """Convert to a dictionary suitable for serialization."""
        data = self.model_dump()
        data["generation_time"] = data["generation_time"].isoformat()
        
        # Convert scan summary
        scan_summary_dict = {}
        if hasattr(self.scan_summary, "to_dict") and callable(self.scan_summary.to_dict):
            scan_summary_dict = self.scan_summary.to_dict()
        else:
            scan_summary_dict = self.scan_summary.model_dump()
            if hasattr(scan_summary_dict.get("start_time", None), "isoformat"):
                scan_summary_dict["start_time"] = scan_summary_dict["start_time"].isoformat()
            if hasattr(scan_summary_dict.get("end_time", None), "isoformat"):
                scan_summary_dict["end_time"] = scan_summary_dict["end_time"].isoformat()
        data["scan_summary"] = scan_summary_dict
            
        # Convert findings
        findings_dict = {}
        for req_id, req_findings in self.findings.items():
            findings_dict[req_id] = [finding.to_dict() for finding in req_findings]
        data["findings"] = findings_dict
        
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ComplianceReport':
        """Create a ComplianceReport from a dictionary."""
        # Convert timestamps
        if "generation_time" in data and isinstance(data["generation_time"], str):
            data["generation_time"] = datetime.fromisoformat(data["generation_time"])
        
        # Convert scan summary
        if "scan_summary" in data:
            if isinstance(data["scan_summary"], dict):
                # Handle datetime conversion
                if "start_time" in data["scan_summary"] and isinstance(data["scan_summary"]["start_time"], str):
                    data["scan_summary"]["start_time"] = datetime.fromisoformat(data["scan_summary"]["start_time"])
                if "end_time" in data["scan_summary"] and isinstance(data["scan_summary"]["end_time"], str):
                    data["scan_summary"]["end_time"] = datetime.fromisoformat(data["scan_summary"]["end_time"])
                data["scan_summary"] = ScanSummary(**data["scan_summary"])
        
        # Convert findings
        if "findings" in data:
            findings_dict = {}
            for req_id, req_findings in data["findings"].items():
                findings_dict[req_id] = [ComplianceFinding.from_dict(finding) for finding in req_findings]
            data["findings"] = findings_dict
        
        return cls(**data)


class ReportGenerator(BaseReporter):
    """Generator for compliance reports from scan results."""
    
    def __init__(self, framework_id: str):
        """Initialize with a specific compliance framework."""
        super().__init__()
        self.framework = FrameworkRegistry.get_framework(framework_id)
    
    def _match_to_findings(
        self, 
        match: SensitiveDataMatch, 
        file_path: str
    ) -> List[ComplianceFinding]:
        """Convert a sensitive data match to compliance findings."""
        findings = []
        
        # Find all requirements that relate to this match's category
        requirements = self.framework.get_requirements_for_category(match.category)
        
        for req in requirements:
            # Determine risk level for this requirement
            risk_level = req.get_risk_level(match.category, match.sensitivity)
            
            finding = ComplianceFinding(
                requirement_id=req.id,
                file_path=file_path,
                matched_content=match.matched_content,
                context=match.context,
                risk_level=risk_level,
                sensitivity=match.sensitivity,
                category=match.category,
                remediation_guidance=req.remediation_guidance,
                related_matches=[match.matched_content]
            )
            
            findings.append(finding)
            
        return findings
    
    def generate_report(self, scan_results: List[ScanResult], scan_summary: ScanSummary) -> ComplianceReport:
        """Generate a compliance report from scan results."""
        # Initialize the report
        report = ComplianceReport(
            framework_id=self.framework.id,
            framework_name=self.framework.name,
            scan_summary=scan_summary,
            metadata={
                "framework_version": self.framework.version,
                "framework_description": self.framework.description
            }
        )
        
        # Initialize findings dictionary with empty lists for each requirement
        report.findings = {req_id: [] for req_id in self.framework.requirements}
        
        # Process each scan result
        for result in scan_results:
            if result.has_sensitive_data:
                for match in result.matches:
                    # Convert match to findings
                    findings = self._match_to_findings(match, result.file_metadata.file_path)
                    
                    # Add findings to the report
                    for finding in findings:
                        if finding.requirement_id in report.findings:
                            report.findings[finding.requirement_id].append(finding)
        
        return report
    
    # Implement BaseReporter interface methods
    def generate(self, data: Any, options: Optional[Dict[str, Any]] = None) -> Any:
        """Generate a report from data with the given options."""
        if not options:
            options = {}
            
        if not isinstance(data, dict) or "scan_results" not in data or "scan_summary" not in data:
            raise ValueError("Data must contain 'scan_results' and 'scan_summary' keys")
            
        scan_results = data["scan_results"]
        scan_summary = data["scan_summary"]
        
        return self.generate_report(scan_results, scan_summary)
    
    def supports_format(self, format_type: str) -> bool:
        """Check if this reporter supports the given format."""
        return format_type.lower() in ["json", "html", "pdf"]
    
    def to_common_format(self, report: ComplianceReport) -> dict:
        """Convert the compliance report to a common format."""
        # Prepare a common format dictionary compatible with common.utils.export functions
        return {
            "report_id": report.report_id,
            "type": "compliance_report",
            "framework": report.framework_name,
            "generation_time": report.generation_time.isoformat(),
            "total_findings": report.total_findings,
            "findings_by_risk": {k.value: v for k, v in report.findings_by_risk.items()},
            "findings_by_status": {k.value: v for k, v in report.findings_by_status.items()},
            "metadata": report.metadata,
            "scan_summary": report.scan_summary.model_dump() if hasattr(report.scan_summary, "model_dump") else {},
            "raw_data": report.to_dict()
        }