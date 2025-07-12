"""Tests for PyMigrate data models."""

import pytest
from datetime import datetime, timedelta
import pytz

from pymigrate.models import (
    OperationType,
    ComplianceFramework,
    AccessLevel,
    AuditEvent,
    DataLineageNode,
    ComplianceRule,
    ComplianceViolation,
    EvidencePackage,
    AccessControlEntry,
    AccessAttempt,
)


class TestEnums:
    """Test enumeration types."""

    def test_operation_type_values(self):
        """Test OperationType enum values."""
        assert OperationType.READ.value == "READ"
        assert OperationType.WRITE.value == "WRITE"
        assert OperationType.TRANSFORM.value == "TRANSFORM"
        assert OperationType.DELETE.value == "DELETE"
        assert OperationType.AUDIT.value == "AUDIT"

    def test_compliance_framework_values(self):
        """Test ComplianceFramework enum values."""
        assert ComplianceFramework.GDPR.value == "GDPR"
        assert ComplianceFramework.SOX.value == "SOX"
        assert ComplianceFramework.HIPAA.value == "HIPAA"
        assert ComplianceFramework.BASEL_III.value == "BASEL_III"

    def test_access_level_values(self):
        """Test AccessLevel enum values."""
        assert AccessLevel.READ.value == "READ"
        assert AccessLevel.WRITE.value == "WRITE"
        assert AccessLevel.DELETE.value == "DELETE"
        assert AccessLevel.ADMIN.value == "ADMIN"
        assert AccessLevel.AUDIT.value == "AUDIT"


class TestAuditEvent:
    """Test AuditEvent model."""

    def test_audit_event_creation(self):
        """Test creating an audit event."""
        now = datetime.now(pytz.UTC)
        event = AuditEvent(
            event_id="test-123",
            timestamp=now,
            actor="test_user",
            operation=OperationType.READ,
            resource="test_resource",
            details={"key": "value"},
            previous_hash="abc123",
            hash="def456",
            signature="sig789",
        )

        assert event.event_id == "test-123"
        assert event.timestamp == now
        assert event.actor == "test_user"
        assert event.operation == OperationType.READ
        assert event.resource == "test_resource"
        assert event.details == {"key": "value"}
        assert event.previous_hash == "abc123"
        assert event.hash == "def456"
        assert event.signature == "sig789"

    def test_audit_event_immutability(self):
        """Test that audit events are immutable."""
        event = AuditEvent(
            event_id="test-123",
            timestamp=datetime.now(pytz.UTC),
            actor="test_user",
            operation=OperationType.READ,
            resource="test_resource",
        )

        # Should not be able to modify
        from pydantic_core import ValidationError

        with pytest.raises(ValidationError):
            event.actor = "modified_user"

    def test_audit_event_optional_fields(self):
        """Test audit event with optional fields."""
        event = AuditEvent(
            event_id="test-123",
            timestamp=datetime.now(pytz.UTC),
            actor="test_user",
            operation=OperationType.READ,
            resource="test_resource",
        )

        assert event.details == {}
        assert event.previous_hash is None
        assert event.hash is None
        assert event.signature is None


class TestDataLineageNode:
    """Test DataLineageNode model."""

    def test_lineage_node_creation(self):
        """Test creating a lineage node."""
        now = datetime.now(pytz.UTC)
        node = DataLineageNode(
            node_id="node-123",
            name="Test Node",
            node_type="source",
            timestamp=now,
            metadata={"type": "database"},
            parent_ids=["parent-1", "parent-2"],
            child_ids=["child-1"],
        )

        assert node.node_id == "node-123"
        assert node.name == "Test Node"
        assert node.node_type == "source"
        assert node.timestamp == now
        assert node.metadata == {"type": "database"}
        assert node.parent_ids == ["parent-1", "parent-2"]
        assert node.child_ids == ["child-1"]

    def test_lineage_node_defaults(self):
        """Test lineage node with default values."""
        node = DataLineageNode(
            node_id="node-123",
            name="Test Node",
            node_type="transformation",
            timestamp=datetime.now(pytz.UTC),
        )

        assert node.metadata == {}
        assert node.parent_ids == []
        assert node.child_ids == []


class TestComplianceRule:
    """Test ComplianceRule model."""

    def test_compliance_rule_creation(self):
        """Test creating a compliance rule."""
        effective = datetime.now(pytz.UTC)
        expiry = effective + timedelta(days=365)

        rule = ComplianceRule(
            rule_id="gdpr-001",
            name="Data Retention Rule",
            framework=ComplianceFramework.GDPR,
            description="Ensure data is not retained beyond limit",
            severity="HIGH",
            rule_logic={"max_days": 730},
            version="1.0",
            effective_date=effective,
            expiry_date=expiry,
        )

        assert rule.rule_id == "gdpr-001"
        assert rule.name == "Data Retention Rule"
        assert rule.framework == ComplianceFramework.GDPR
        assert rule.severity == "HIGH"
        assert rule.rule_logic == {"max_days": 730}
        assert rule.version == "1.0"
        assert rule.effective_date == effective
        assert rule.expiry_date == expiry

    def test_compliance_rule_no_expiry(self):
        """Test compliance rule without expiry date."""
        rule = ComplianceRule(
            rule_id="sox-001",
            name="Access Control",
            framework=ComplianceFramework.SOX,
            description="Restrict access",
            severity="CRITICAL",
            rule_logic={},
            version="1.0",
            effective_date=datetime.now(pytz.UTC),
        )

        assert rule.expiry_date is None


class TestComplianceViolation:
    """Test ComplianceViolation model."""

    def test_compliance_violation_creation(self):
        """Test creating a compliance violation."""
        now = datetime.now(pytz.UTC)
        violation = ComplianceViolation(
            violation_id="vio-123",
            rule_id="gdpr-001",
            timestamp=now,
            resource="customer_data",
            details={"issue": "retention exceeded"},
            remediation_required=True,
            remediation_status="PENDING",
        )

        assert violation.violation_id == "vio-123"
        assert violation.rule_id == "gdpr-001"
        assert violation.timestamp == now
        assert violation.resource == "customer_data"
        assert violation.details == {"issue": "retention exceeded"}
        assert violation.remediation_required is True
        assert violation.remediation_status == "PENDING"

    def test_compliance_violation_optional_status(self):
        """Test compliance violation with optional status."""
        violation = ComplianceViolation(
            violation_id="vio-123",
            rule_id="gdpr-001",
            timestamp=datetime.now(pytz.UTC),
            resource="data",
            details={},
            remediation_required=False,
        )

        assert violation.remediation_status is None


class TestEvidencePackage:
    """Test EvidencePackage model."""

    def test_evidence_package_creation(self):
        """Test creating an evidence package."""
        now = datetime.now(pytz.UTC)
        start = now - timedelta(days=30)
        end = now

        event = AuditEvent(
            event_id="evt-1",
            timestamp=now,
            actor="user",
            operation=OperationType.READ,
            resource="data",
        )

        package = EvidencePackage(
            package_id="pkg-123",
            created_at=now,
            created_by="auditor",
            purpose="Monthly audit",
            framework=ComplianceFramework.SOX,
            start_date=start,
            end_date=end,
            audit_events=[event],
            lineage_graphs=[{"nodes": [], "edges": []}],
            compliance_reports=[{"status": "compliant"}],
            cryptographic_proofs=[{"type": "hash"}],
            metadata={"version": "1.0"},
        )

        assert package.package_id == "pkg-123"
        assert package.created_at == now
        assert package.created_by == "auditor"
        assert package.purpose == "Monthly audit"
        assert package.framework == ComplianceFramework.SOX
        assert len(package.audit_events) == 1
        assert len(package.lineage_graphs) == 1
        assert len(package.compliance_reports) == 1
        assert len(package.cryptographic_proofs) == 1

    def test_evidence_package_defaults(self):
        """Test evidence package with default values."""
        package = EvidencePackage(
            package_id="pkg-123",
            created_at=datetime.now(pytz.UTC),
            created_by="auditor",
            purpose="Test",
            framework=ComplianceFramework.GDPR,
            start_date=datetime.now(pytz.UTC) - timedelta(days=1),
            end_date=datetime.now(pytz.UTC),
        )

        assert package.audit_events == []
        assert package.lineage_graphs == []
        assert package.compliance_reports == []
        assert package.cryptographic_proofs == []
        assert package.metadata == {}


class TestAccessControlEntry:
    """Test AccessControlEntry model."""

    def test_access_control_entry_creation(self):
        """Test creating an access control entry."""
        now = datetime.now(pytz.UTC)
        expires = now + timedelta(days=30)

        ace = AccessControlEntry(
            ace_id="ace-123",
            principal="user1",
            resource="database",
            permissions={AccessLevel.READ, AccessLevel.WRITE},
            conditions={"department": "finance"},
            granted_by="admin",
            granted_at=now,
            expires_at=expires,
            is_active=True,
        )

        assert ace.ace_id == "ace-123"
        assert ace.principal == "user1"
        assert ace.resource == "database"
        assert AccessLevel.READ in ace.permissions
        assert AccessLevel.WRITE in ace.permissions
        assert ace.conditions == {"department": "finance"}
        assert ace.granted_by == "admin"
        assert ace.granted_at == now
        assert ace.expires_at == expires
        assert ace.is_active is True

    def test_access_control_entry_no_expiry(self):
        """Test access control entry without expiry."""
        ace = AccessControlEntry(
            ace_id="ace-123",
            principal="user1",
            resource="file",
            permissions={AccessLevel.READ},
            granted_by="admin",
            granted_at=datetime.now(pytz.UTC),
        )

        assert ace.expires_at is None
        assert ace.conditions == {}
        assert ace.is_active is True


class TestAccessAttempt:
    """Test AccessAttempt model."""

    def test_access_attempt_creation(self):
        """Test creating an access attempt."""
        now = datetime.now(pytz.UTC)
        attempt = AccessAttempt(
            attempt_id="att-123",
            timestamp=now,
            principal="user1",
            resource="secure_data",
            operation=AccessLevel.WRITE,
            granted=False,
            reason="Insufficient permissions",
            metadata={"ip": "192.168.1.1"},
        )

        assert attempt.attempt_id == "att-123"
        assert attempt.timestamp == now
        assert attempt.principal == "user1"
        assert attempt.resource == "secure_data"
        assert attempt.operation == AccessLevel.WRITE
        assert attempt.granted is False
        assert attempt.reason == "Insufficient permissions"
        assert attempt.metadata == {"ip": "192.168.1.1"}

    def test_access_attempt_granted(self):
        """Test successful access attempt."""
        attempt = AccessAttempt(
            attempt_id="att-123",
            timestamp=datetime.now(pytz.UTC),
            principal="admin",
            resource="config",
            operation=AccessLevel.ADMIN,
            granted=True,
            reason="Admin role",
        )

        assert attempt.granted is True
        assert attempt.metadata == {}
