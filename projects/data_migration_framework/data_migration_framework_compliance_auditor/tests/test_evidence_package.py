"""Tests for the evidence package compiler."""

import json
import os
import pytest
import zipfile
from datetime import datetime, timedelta
import pytz

from pymigrate.evidence import EvidencePackageCompiler
from pymigrate.audit import AuditLogger, InMemoryAuditStorage
from pymigrate.compliance import ComplianceRuleEngine
from pymigrate.lineage import LineageTracker
from pymigrate.models import ComplianceFramework, OperationType


class TestEvidencePackageCompiler:
    """Test suite for EvidencePackageCompiler."""

    @pytest.fixture
    def setup_compiler(self):
        """Set up compiler with all dependencies."""
        storage = InMemoryAuditStorage()
        audit_logger = AuditLogger(storage, enable_signatures=True)
        lineage_tracker = LineageTracker(audit_logger)
        compliance_engine = ComplianceRuleEngine(audit_logger=audit_logger)

        compiler = EvidencePackageCompiler(
            audit_logger=audit_logger,
            audit_storage=storage,
            lineage_tracker=lineage_tracker,
            compliance_engine=compliance_engine,
        )

        return compiler, audit_logger, lineage_tracker, compliance_engine

    def test_compile_basic_package(self, setup_compiler):
        """Test compiling a basic evidence package."""
        compiler, audit_logger, lineage_tracker, _ = setup_compiler

        # Generate some audit events
        start_date = datetime.now(pytz.UTC) - timedelta(hours=2)

        audit_logger.log_event("user1", OperationType.READ, "resource1")
        audit_logger.log_event("user2", OperationType.WRITE, "resource2")

        # Create some lineage
        source = lineage_tracker.create_source_node("TestSource", actor="user1")

        end_date = datetime.now(pytz.UTC)

        # Compile package
        package = compiler.compile_package(
            purpose="Quarterly audit",
            framework=ComplianceFramework.SOX,
            start_date=start_date,
            end_date=end_date,
            created_by="auditor1",
        )

        # Verify package
        assert package.purpose == "Quarterly audit"
        assert package.framework == ComplianceFramework.SOX
        assert len(package.audit_events) >= 2
        assert len(package.lineage_graphs) > 0
        assert len(package.cryptographic_proofs) > 0

    def test_package_with_filters(self, setup_compiler):
        """Test compiling package with filters."""
        compiler, audit_logger, _, _ = setup_compiler

        start_date = datetime.now(pytz.UTC) - timedelta(hours=1)

        # Log events for different actors
        audit_logger.log_event("alice", OperationType.READ, "file1")
        audit_logger.log_event("bob", OperationType.WRITE, "file2")
        audit_logger.log_event("alice", OperationType.DELETE, "file3")

        end_date = datetime.now(pytz.UTC)

        # Compile with actor filter
        package = compiler.compile_package(
            purpose="User audit",
            framework=ComplianceFramework.GDPR,
            start_date=start_date,
            end_date=end_date,
            created_by="auditor",
            filters={"actors": ["alice"]},
        )

        # Should only include alice's events
        assert all(event.actor == "alice" for event in package.audit_events)
        assert len(package.audit_events) == 2

    def test_format_package_json(self, setup_compiler):
        """Test formatting package as JSON."""
        compiler, audit_logger, _, _ = setup_compiler

        # Create minimal package
        start_date = datetime.now(pytz.UTC) - timedelta(hours=1)
        audit_logger.log_event("user", OperationType.READ, "resource")

        package = compiler.compile_package(
            purpose="Test",
            framework=ComplianceFramework.GDPR,
            start_date=start_date,
            end_date=datetime.now(pytz.UTC),
            created_by="tester",
        )

        # Format as JSON
        json_output = compiler.format_package(package, format="json")

        # Verify JSON structure
        data = json.loads(json_output)
        assert "evidencePackage" in data
        assert data["evidencePackage"]["packageId"] == package.package_id
        assert data["evidencePackage"]["framework"] == "GDPR"

    def test_format_package_xbrl(self, setup_compiler):
        """Test formatting package as XBRL."""
        compiler, _, _, _ = setup_compiler

        # Create package with compliance data
        package = compiler.compile_package(
            purpose="Regulatory submission",
            framework=ComplianceFramework.SOX,
            start_date=datetime(2023, 1, 1, tzinfo=pytz.UTC),
            end_date=datetime(2023, 12, 31, tzinfo=pytz.UTC),
            created_by="compliance_officer",
        )

        # Format as XBRL
        xbrl_output = compiler.format_package(package, format="xbrl")

        # Verify XBRL structure
        assert "<?xml" in xbrl_output
        assert "xbrl" in xbrl_output
        assert "ComplianceFramework" in xbrl_output

    def test_format_package_html(self, setup_compiler):
        """Test formatting package as HTML."""
        compiler, audit_logger, _, _ = setup_compiler

        # Create package with events
        start_date = datetime.now(pytz.UTC) - timedelta(hours=1)
        for i in range(5):
            audit_logger.log_event(f"user{i}", OperationType.READ, f"resource{i}")

        package = compiler.compile_package(
            purpose="Human review",
            framework=ComplianceFramework.HIPAA,
            start_date=start_date,
            end_date=datetime.now(pytz.UTC),
            created_by="reviewer",
        )

        # Format as HTML
        html_output = compiler.format_package(package, format="html")

        # Verify HTML structure
        assert "<!DOCTYPE html>" in html_output
        assert package.package_id in html_output
        assert "HIPAA" in html_output
        assert "Audit Trail Summary" in html_output

    def test_export_package(self, setup_compiler, tmp_path):
        """Test exporting package to files."""
        compiler, audit_logger, _, _ = setup_compiler

        # Create package
        start_date = datetime.now(pytz.UTC) - timedelta(hours=1)
        audit_logger.log_event("user", OperationType.WRITE, "data")

        package = compiler.compile_package(
            purpose="Export test",
            framework=ComplianceFramework.GDPR,
            start_date=start_date,
            end_date=datetime.now(pytz.UTC),
            created_by="exporter",
        )

        # Export package
        zip_path = compiler.export_package(
            package, str(tmp_path), formats=["json", "html"], include_attachments=True
        )

        # Verify ZIP created
        assert os.path.exists(zip_path)
        assert zip_path.endswith(".zip")

        # Verify ZIP contents
        with zipfile.ZipFile(zip_path, "r") as zf:
            files = zf.namelist()
            assert any("evidence.json" in f for f in files)
            assert any("evidence.html" in f for f in files)
            assert any("metadata.json" in f for f in files)
            assert any("audit_log_excerpt.jsonl" in f for f in files)

    def test_verify_package_integrity(self, setup_compiler):
        """Test package integrity verification."""
        compiler, audit_logger, _, _ = setup_compiler

        # Create package with valid events
        start_date = datetime.now(pytz.UTC) - timedelta(hours=1)
        audit_logger.log_event("user", OperationType.READ, "data")

        package = compiler.compile_package(
            purpose="Integrity test",
            framework=ComplianceFramework.SOX,
            start_date=start_date,
            end_date=datetime.now(pytz.UTC),
            created_by="verifier",
        )

        # Verify package
        verification = compiler.verify_package(package)

        assert verification["is_valid"]
        assert verification["checks"]["audit_events"]["verified_events"] > 0
        assert verification["checks"]["cryptographic_proofs"]["valid_proofs"] > 0

    def test_compliance_report_inclusion(self, setup_compiler):
        """Test that compliance reports are included in package."""
        compiler, audit_logger, _, compliance_engine = setup_compiler

        start_date = datetime.now(pytz.UTC) - timedelta(hours=2)

        # Generate compliance violations
        data_with_pii = {"ssn": "123-45-6789", "name": "Test User"}
        compliance_engine.validate_data_operation(
            operation_type="write",
            data=data_with_pii,
            context={"actor": "app", "is_encrypted": False},
            frameworks=[ComplianceFramework.GDPR],
        )

        # Create package
        package = compiler.compile_package(
            purpose="Compliance review",
            framework=ComplianceFramework.GDPR,
            start_date=start_date,
            end_date=datetime.now(pytz.UTC),
            created_by="compliance_officer",
        )

        # Verify compliance reports included
        assert len(package.compliance_reports) > 0
        main_report = package.compliance_reports[0]
        assert "summary" in main_report
        assert main_report["framework"] == ComplianceFramework.GDPR

    def test_lineage_graph_collection(self, setup_compiler):
        """Test lineage graph collection in package."""
        compiler, _, lineage_tracker, _ = setup_compiler

        start_date = datetime.now(pytz.UTC) - timedelta(hours=1)

        # Create lineage within time period
        source = lineage_tracker.create_source_node("DataSource", actor="etl_user")
        transform = lineage_tracker.create_transformation_node(
            "Transform", [source.node_id], "cleanse", actor="etl_user"
        )

        # Create package
        package = compiler.compile_package(
            purpose="Lineage audit",
            framework=ComplianceFramework.SOX,
            start_date=start_date,
            end_date=datetime.now(pytz.UTC),
            created_by="auditor",
        )

        # Verify lineage included
        assert len(package.lineage_graphs) > 0
        lineage_data = package.lineage_graphs[0]
        assert len(lineage_data["nodes"]) >= 2
        assert any(n["name"] == "DataSource" for n in lineage_data["nodes"])

    def test_cryptographic_proof_generation(self, setup_compiler):
        """Test cryptographic proof generation."""
        compiler, audit_logger, _, _ = setup_compiler

        start_date = datetime.now(pytz.UTC) - timedelta(hours=1)

        # Create events
        for i in range(3):
            audit_logger.log_event(f"user{i}", OperationType.WRITE, f"resource{i}")

        # Create package
        package = compiler.compile_package(
            purpose="Proof test",
            framework=ComplianceFramework.SOX,
            start_date=start_date,
            end_date=datetime.now(pytz.UTC),
            created_by="security_admin",
        )

        # Verify proofs
        assert len(package.cryptographic_proofs) > 0

        # Check proof types
        proof_types = {p["proof_type"] for p in package.cryptographic_proofs}
        assert "chain_integrity" in proof_types
        assert "event_signature" in proof_types
        assert "package_integrity" in proof_types

        # Verify chain integrity proof
        chain_proof = next(
            p
            for p in package.cryptographic_proofs
            if p["proof_type"] == "chain_integrity"
        )
        assert chain_proof["is_valid"]

    def test_performance_with_large_dataset(self, setup_compiler):
        """Test performance with large number of events."""
        compiler, audit_logger, lineage_tracker, _ = setup_compiler

        start_date = datetime.now(pytz.UTC) - timedelta(hours=1)

        # Generate many events
        num_events = 100
        for i in range(num_events):
            audit_logger.log_event(
                actor=f"user_{i % 10}",
                operation=OperationType.READ,
                resource=f"resource_{i % 20}",
            )

        # Create some lineage
        sources = []
        for i in range(5):
            source = lineage_tracker.create_source_node(f"Source{i}")
            sources.append(source.node_id)

        # Time package compilation
        compile_start = datetime.now()

        package = compiler.compile_package(
            purpose="Performance test",
            framework=ComplianceFramework.GDPR,
            start_date=start_date,
            end_date=datetime.now(pytz.UTC),
            created_by="perf_tester",
        )

        compile_duration = (datetime.now() - compile_start).total_seconds()

        # Should complete reasonably fast
        assert compile_duration < 5  # Less than 5 seconds
        assert len(package.audit_events) >= num_events
        assert package.metadata["total_events"] >= num_events
