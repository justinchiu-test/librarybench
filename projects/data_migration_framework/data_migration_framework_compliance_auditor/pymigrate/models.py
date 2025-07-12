"""Core data models for PyMigrate compliance framework."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field, ConfigDict


class OperationType(str, Enum):
    """Types of data operations that can be tracked."""

    READ = "READ"
    WRITE = "WRITE"
    TRANSFORM = "TRANSFORM"
    DELETE = "DELETE"
    COPY = "COPY"
    VALIDATE = "VALIDATE"
    ARCHIVE = "ARCHIVE"
    AUDIT = "AUDIT"


class ComplianceFramework(str, Enum):
    """Supported regulatory compliance frameworks."""

    GDPR = "GDPR"
    SOX = "SOX"
    HIPAA = "HIPAA"
    BASEL_III = "BASEL_III"
    PCI_DSS = "PCI_DSS"
    CCPA = "CCPA"


class AccessLevel(str, Enum):
    """Access control levels."""

    READ = "READ"
    WRITE = "WRITE"
    DELETE = "DELETE"
    ADMIN = "ADMIN"
    AUDIT = "AUDIT"


class AuditEvent(BaseModel):
    """Represents an auditable event in the system."""

    model_config = ConfigDict(frozen=True)

    event_id: str = Field(..., description="Unique identifier for the event")
    timestamp: datetime = Field(..., description="When the event occurred")
    actor: str = Field(..., description="User or system that performed the action")
    operation: OperationType = Field(..., description="Type of operation performed")
    resource: str = Field(..., description="Resource that was accessed or modified")
    details: Dict[str, Any] = Field(
        default_factory=dict, description="Additional event details"
    )
    previous_hash: Optional[str] = Field(
        None, description="Hash of the previous event in the chain"
    )
    hash: Optional[str] = Field(None, description="Cryptographic hash of this event")
    signature: Optional[str] = Field(None, description="Digital signature of the event")


class DataLineageNode(BaseModel):
    """Represents a node in the data lineage graph."""

    node_id: str = Field(..., description="Unique identifier for the node")
    name: str = Field(..., description="Name of the data element or dataset")
    node_type: str = Field(
        ..., description="Type of node (source, transformation, destination)"
    )
    timestamp: datetime = Field(
        ..., description="When this node was created or modified"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional node metadata"
    )
    parent_ids: List[str] = Field(
        default_factory=list, description="IDs of parent nodes"
    )
    child_ids: List[str] = Field(default_factory=list, description="IDs of child nodes")


class ComplianceRule(BaseModel):
    """Defines a compliance rule that data operations must satisfy."""

    rule_id: str = Field(..., description="Unique identifier for the rule")
    name: str = Field(..., description="Human-readable name for the rule")
    framework: ComplianceFramework = Field(
        ..., description="Regulatory framework this rule belongs to"
    )
    description: str = Field(
        ..., description="Detailed description of what the rule checks"
    )
    severity: str = Field(
        ..., description="Severity level (CRITICAL, HIGH, MEDIUM, LOW)"
    )
    rule_logic: Dict[str, Any] = Field(..., description="Logic for evaluating the rule")
    version: str = Field(..., description="Version of the rule")
    effective_date: datetime = Field(
        ..., description="When this rule becomes effective"
    )
    expiry_date: Optional[datetime] = Field(None, description="When this rule expires")


class ComplianceViolation(BaseModel):
    """Represents a violation of a compliance rule."""

    violation_id: str = Field(..., description="Unique identifier for the violation")
    rule_id: str = Field(..., description="ID of the rule that was violated")
    timestamp: datetime = Field(..., description="When the violation occurred")
    resource: str = Field(..., description="Resource involved in the violation")
    details: Dict[str, Any] = Field(..., description="Details about the violation")
    remediation_required: bool = Field(
        ..., description="Whether remediation is required"
    )
    remediation_status: Optional[str] = Field(
        None, description="Status of remediation efforts"
    )


class EvidencePackage(BaseModel):
    """Contains all evidence for audit purposes."""

    package_id: str = Field(
        ..., description="Unique identifier for the evidence package"
    )
    created_at: datetime = Field(..., description="When the package was created")
    created_by: str = Field(..., description="User who created the package")
    purpose: str = Field(..., description="Purpose of the evidence package")
    framework: ComplianceFramework = Field(
        ..., description="Compliance framework this package addresses"
    )
    start_date: datetime = Field(..., description="Start date of the audit period")
    end_date: datetime = Field(..., description="End date of the audit period")
    audit_events: List[AuditEvent] = Field(
        default_factory=list, description="Relevant audit events"
    )
    lineage_graphs: List[Dict[str, Any]] = Field(
        default_factory=list, description="Data lineage information"
    )
    compliance_reports: List[Dict[str, Any]] = Field(
        default_factory=list, description="Compliance validation reports"
    )
    cryptographic_proofs: List[Dict[str, Any]] = Field(
        default_factory=list, description="Cryptographic verification data"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional package metadata"
    )


class AccessControlEntry(BaseModel):
    """Represents an access control entry."""

    ace_id: str = Field(..., description="Unique identifier for the ACE")
    principal: str = Field(..., description="User or role this entry applies to")
    resource: str = Field(..., description="Resource being controlled")
    permissions: Set[AccessLevel] = Field(..., description="Granted permissions")
    conditions: Dict[str, Any] = Field(
        default_factory=dict, description="Conditions for access"
    )
    granted_by: str = Field(..., description="Who granted this access")
    granted_at: datetime = Field(..., description="When access was granted")
    expires_at: Optional[datetime] = Field(None, description="When access expires")
    is_active: bool = Field(True, description="Whether this entry is currently active")


class AccessAttempt(BaseModel):
    """Records an attempt to access a resource."""

    attempt_id: str = Field(..., description="Unique identifier for the attempt")
    timestamp: datetime = Field(..., description="When the attempt occurred")
    principal: str = Field(..., description="Who attempted access")
    resource: str = Field(..., description="Resource that was accessed")
    operation: AccessLevel = Field(..., description="Type of access attempted")
    granted: bool = Field(..., description="Whether access was granted")
    reason: str = Field(..., description="Reason for grant/denial")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional attempt metadata"
    )
