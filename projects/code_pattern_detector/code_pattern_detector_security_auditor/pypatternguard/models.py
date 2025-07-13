"""Data models for PyPatternGuard."""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class SeverityLevel(str, Enum):
    """Vulnerability severity levels based on CVSS scoring."""
    
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class VulnerabilityType(str, Enum):
    """Types of vulnerabilities based on OWASP Top 10."""
    
    INJECTION = "injection"
    BROKEN_AUTH = "broken_authentication"
    SENSITIVE_DATA_EXPOSURE = "sensitive_data_exposure"
    XXE = "xml_external_entities"
    BROKEN_ACCESS_CONTROL = "broken_access_control"
    SECURITY_MISCONFIGURATION = "security_misconfiguration"
    XSS = "cross_site_scripting"
    INSECURE_DESERIALIZATION = "insecure_deserialization"
    COMPONENTS_VULNERABILITIES = "components_with_vulnerabilities"
    INSUFFICIENT_LOGGING = "insufficient_logging_monitoring"
    CRYPTO_FAILURE = "cryptographic_failure"
    HARDCODED_SECRET = "hardcoded_secret"
    INPUT_VALIDATION = "input_validation"


class ComplianceFramework(str, Enum):
    """Supported compliance frameworks."""
    
    PCI_DSS = "PCI-DSS"
    SOC2 = "SOC2"
    OWASP = "OWASP"


class Location(BaseModel):
    """Code location information."""
    
    model_config = ConfigDict(json_encoders={Path: str})
    
    file_path: Path
    line_start: int
    line_end: int
    column_start: Optional[int] = None
    column_end: Optional[int] = None


class Vulnerability(BaseModel):
    """Represents a detected security vulnerability."""
    
    id: str
    type: VulnerabilityType
    severity: SeverityLevel
    title: str
    description: str
    location: Location
    code_snippet: Optional[str] = None
    remediation: str
    cwe_ids: List[str] = Field(default_factory=list)
    cvss_score: Optional[float] = None
    confidence: float = Field(ge=0.0, le=1.0)
    false_positive: bool = False
    suppressed: bool = False
    suppression_reason: Optional[str] = None
    compliance_mappings: Dict[ComplianceFramework, List[str]] = Field(
        default_factory=dict
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def get_risk_score(self) -> float:
        """Calculate risk score based on severity and confidence."""
        severity_weights = {
            SeverityLevel.CRITICAL: 10.0,
            SeverityLevel.HIGH: 8.0,
            SeverityLevel.MEDIUM: 5.0,
            SeverityLevel.LOW: 2.0,
            SeverityLevel.INFO: 0.5,
        }
        return severity_weights.get(self.severity, 0) * self.confidence


class ScanResult(BaseModel):
    """Results from a security scan."""
    
    model_config = ConfigDict(json_encoders={Path: str, datetime: lambda v: v.isoformat()})
    
    scan_id: str
    timestamp: datetime
    target_path: Path
    total_files_scanned: int
    total_lines_scanned: int
    scan_duration_seconds: float
    vulnerabilities: List[Vulnerability]
    scan_errors: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def get_vulnerabilities_by_severity(self) -> Dict[SeverityLevel, List[Vulnerability]]:
        """Group vulnerabilities by severity level."""
        result = {level: [] for level in SeverityLevel}
        for vuln in self.vulnerabilities:
            if not vuln.suppressed:
                result[vuln.severity].append(vuln)
        return result
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics for the scan."""
        severity_counts = {
            level.value: len(vulns)
            for level, vulns in self.get_vulnerabilities_by_severity().items()
        }
        return {
            "total_vulnerabilities": len(
                [v for v in self.vulnerabilities if not v.suppressed]
            ),
            "severity_distribution": severity_counts,
            "suppressed_count": len([v for v in self.vulnerabilities if v.suppressed]),
            "false_positive_count": len(
                [v for v in self.vulnerabilities if v.false_positive]
            ),
            "files_scanned": self.total_files_scanned,
            "lines_scanned": self.total_lines_scanned,
            "scan_duration": self.scan_duration_seconds,
        }


class ComplianceRequirement(BaseModel):
    """Represents a compliance requirement."""
    
    framework: ComplianceFramework
    requirement_id: str
    description: str
    vulnerabilities: List[str] = Field(default_factory=list)  # Vulnerability IDs
    status: str = "not_compliant"
    evidence: List[Dict[str, Any]] = Field(default_factory=list)


class ComplianceReport(BaseModel):
    """Compliance report mapping vulnerabilities to regulatory requirements."""
    
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
    
    report_id: str
    timestamp: datetime
    scan_result_id: str
    frameworks: List[ComplianceFramework]
    requirements: List[ComplianceRequirement]
    executive_summary: str
    compliance_scores: Dict[ComplianceFramework, float] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SuppressionRule(BaseModel):
    """Rule for suppressing false positives."""
    
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
    
    id: str
    pattern: str  # Regex pattern or vulnerability ID
    reason: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    created_by: str
    approved_by: Optional[str] = None
    active: bool = True