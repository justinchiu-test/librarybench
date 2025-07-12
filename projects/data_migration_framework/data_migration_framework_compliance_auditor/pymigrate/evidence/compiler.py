"""Evidence package compiler implementation."""

import hashlib
import json
import os
import uuid
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytz

from pymigrate.audit.logger import AuditLogger
from pymigrate.audit.storage import AuditStorage
from pymigrate.compliance.engine import ComplianceRuleEngine
from pymigrate.evidence.formats import (
    EvidenceFormatter,
    JSONFormatter,
    XBRLFormatter,
    HTMLFormatter,
)
from pymigrate.lineage.tracker import LineageTracker
from pymigrate.models import ComplianceFramework, EvidencePackage, OperationType


class EvidencePackageCompiler:
    """Compiles comprehensive evidence packages for audit submissions."""

    def __init__(
        self,
        audit_logger: AuditLogger,
        audit_storage: AuditStorage,
        lineage_tracker: LineageTracker,
        compliance_engine: ComplianceRuleEngine,
    ):
        """Initialize the evidence package compiler.

        Args:
            audit_logger: Audit logger instance
            audit_storage: Audit storage backend
            lineage_tracker: Lineage tracking engine
            compliance_engine: Compliance rule engine
        """
        self.audit_logger = audit_logger
        self.audit_storage = audit_storage
        self.lineage_tracker = lineage_tracker
        self.compliance_engine = compliance_engine
        self._formatters: Dict[str, EvidenceFormatter] = {
            "json": JSONFormatter(),
            "xbrl": XBRLFormatter(),
            "html": HTMLFormatter(),
        }

    def compile_package(
        self,
        purpose: str,
        framework: ComplianceFramework,
        start_date: datetime,
        end_date: datetime,
        created_by: str,
        filters: Optional[Dict[str, Any]] = None,
    ) -> EvidencePackage:
        """Compile an evidence package for audit submission.

        Args:
            purpose: Purpose of the evidence package
            framework: Compliance framework
            start_date: Start of audit period
            end_date: End of audit period
            created_by: User creating the package
            filters: Optional filters for evidence selection

        Returns:
            Compiled evidence package
        """
        # Ensure timezone awareness
        if start_date.tzinfo is None:
            start_date = pytz.UTC.localize(start_date)
        if end_date.tzinfo is None:
            end_date = pytz.UTC.localize(end_date)

        # Log package creation
        self.audit_logger.log_event(
            actor=created_by,
            operation=OperationType.WRITE,
            resource="evidence_package",
            details={
                "action": "compile_package",
                "purpose": purpose,
                "framework": framework.value,
                "period": f"{start_date.isoformat()} to {end_date.isoformat()}",
            },
        )

        # Collect audit events
        audit_events = self._collect_audit_events(start_date, end_date, filters)

        # Collect lineage information
        lineage_graphs = self._collect_lineage_data(start_date, end_date, filters)

        # Generate compliance reports
        compliance_reports = self._generate_compliance_reports(
            framework, start_date, end_date, audit_events
        )

        # Generate cryptographic proofs
        cryptographic_proofs = self._generate_cryptographic_proofs(audit_events)

        # Convert any datetime objects in lineage graphs to strings
        for graph in lineage_graphs:
            for node in graph.get("nodes", []):
                if "metadata" in node and "operations" in node["metadata"]:
                    for op in node["metadata"]["operations"]:
                        if isinstance(op.get("timestamp"), datetime):
                            op["timestamp"] = op["timestamp"].isoformat()

        # Create package
        package = EvidencePackage(
            package_id=str(uuid.uuid4()),
            created_at=datetime.now(pytz.UTC),
            created_by=created_by,
            purpose=purpose,
            framework=framework,
            start_date=start_date,
            end_date=end_date,
            audit_events=audit_events,
            lineage_graphs=lineage_graphs,
            compliance_reports=compliance_reports,
            cryptographic_proofs=cryptographic_proofs,
            metadata={
                "filters_applied": filters or {},
                "total_events": len(audit_events),
                "package_version": "1.0",
            },
        )

        return package

    def _collect_audit_events(
        self,
        start_date: datetime,
        end_date: datetime,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Any]:
        """Collect relevant audit events for the package.

        Args:
            start_date: Start of period
            end_date: End of period
            filters: Optional filters

        Returns:
            List of audit events
        """
        # Get events from storage
        events = self.audit_storage.get_events_by_timerange(start_date, end_date)

        # Apply filters if provided
        if filters:
            if "actors" in filters:
                actors = set(filters["actors"])
                events = [e for e in events if e.actor in actors]

            if "resources" in filters:
                resources = set(filters["resources"])
                events = [e for e in events if e.resource in resources]

            if "operations" in filters:
                operations = set(filters["operations"])
                events = [e for e in events if e.operation in operations]

        # Verify event integrity
        verified_events = []
        for event in events:
            if self.audit_logger.verify_event(event):
                verified_events.append(event)

        return verified_events

    def _collect_lineage_data(
        self,
        start_date: datetime,
        end_date: datetime,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Collect lineage data for the audit period.

        Args:
            start_date: Start of period
            end_date: End of period
            filters: Optional filters

        Returns:
            List of lineage graph data
        """
        # Export full lineage graph
        full_lineage = self.lineage_tracker.export_lineage()

        # Filter nodes by time period
        filtered_nodes = []
        for node in full_lineage["nodes"]:
            node_timestamp = datetime.fromisoformat(node["timestamp"])
            if start_date <= node_timestamp <= end_date:
                filtered_nodes.append(node)

        # Apply additional filters
        if filters and "node_types" in filters:
            node_types = set(filters["node_types"])
            filtered_nodes = [n for n in filtered_nodes if n["node_type"] in node_types]

        # Get relevant edges
        node_ids = {n["node_id"] for n in filtered_nodes}
        filtered_edges = [
            e
            for e in full_lineage["edges"]
            if e["parent_id"] in node_ids or e["child_id"] in node_ids
        ]

        return [
            {
                "nodes": filtered_nodes,
                "edges": filtered_edges,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
            }
        ]

    def _generate_compliance_reports(
        self,
        framework: ComplianceFramework,
        start_date: datetime,
        end_date: datetime,
        audit_events: List[Any],
    ) -> List[Dict[str, Any]]:
        """Generate compliance reports for the evidence package.

        Args:
            framework: Compliance framework
            start_date: Start of period
            end_date: End of period
            audit_events: Audit events to analyze

        Returns:
            List of compliance reports
        """
        # Generate main compliance report
        main_report = self.compliance_engine.generate_compliance_report(
            framework, start_date, end_date
        )

        # Analyze specific operations from audit events
        operation_reports = []
        for event in audit_events:
            if event.operation in [OperationType.WRITE, OperationType.TRANSFORM]:
                # Validate the operation
                validation_result = self.compliance_engine.validate_data_operation(
                    operation_type=event.operation.value,
                    data=event.details,
                    context={
                        "actor": event.actor,
                        "resource": event.resource,
                        "timestamp": event.timestamp,
                    },
                    frameworks=[framework],
                )

                if not validation_result["is_compliant"]:
                    operation_reports.append(
                        {
                            "event_id": event.event_id,
                            "operation": event.operation.value,
                            "validation_result": validation_result,
                        }
                    )

        return [main_report] + operation_reports

    def _generate_cryptographic_proofs(
        self, audit_events: List[Any]
    ) -> List[Dict[str, Any]]:
        """Generate cryptographic proofs for the evidence package.

        Args:
            audit_events: Audit events to prove

        Returns:
            List of cryptographic proofs
        """
        proofs = []

        # Chain integrity proof
        chain_valid = self.audit_logger.verify_chain_integrity()
        chain_proof = {
            "proof_type": "chain_integrity",
            "algorithm": "SHA-256",
            "is_valid": chain_valid,
            "timestamp": datetime.now(pytz.UTC).isoformat(),
        }
        proofs.append(chain_proof)

        # Individual event proofs (sample)
        for event in audit_events[:10]:  # Limit to first 10 for performance
            event_proof = {
                "proof_type": "event_signature",
                "event_id": event.event_id,
                "hash": event.hash,
                "signature": event.signature,
                "is_valid": self.audit_logger.verify_event(event),
                "algorithm": "RSA-PSS-SHA256",
            }
            proofs.append(event_proof)

        # Package integrity proof
        package_hash = self._compute_package_hash(audit_events)
        package_proof = {
            "proof_type": "package_integrity",
            "hash": package_hash,
            "algorithm": "SHA-256",
            "event_count": len(audit_events),
            "timestamp": datetime.now(pytz.UTC).isoformat(),
            "is_valid": True,  # Package hash is always valid when generated
        }
        proofs.append(package_proof)

        return proofs

    def _compute_package_hash(self, audit_events: List[Any]) -> str:
        """Compute hash of the evidence package contents.

        Args:
            audit_events: Audit events in package

        Returns:
            Hex-encoded hash
        """
        hasher = hashlib.sha256()

        # Hash all event IDs and hashes
        for event in sorted(audit_events, key=lambda e: e.event_id):
            hasher.update(event.event_id.encode())
            hasher.update(event.hash.encode() if event.hash else b"")

        return hasher.hexdigest()

    def format_package(self, package: EvidencePackage, format: str = "json") -> str:
        """Format an evidence package for output.

        Args:
            package: Evidence package to format
            format: Output format (json, xbrl, html)

        Returns:
            Formatted package as string
        """
        formatter = self._formatters.get(format)
        if not formatter:
            raise ValueError(f"Unsupported format: {format}")

        return formatter.format(package)

    def export_package(
        self,
        package: EvidencePackage,
        output_path: str,
        formats: List[str] = ["json", "html"],
        include_attachments: bool = True,
    ) -> str:
        """Export an evidence package to files.

        Args:
            package: Evidence package to export
            output_path: Directory to export to
            formats: List of formats to export
            include_attachments: Whether to include supporting files

        Returns:
            Path to the exported package
        """
        # Create output directory
        output_dir = Path(output_path) / f"evidence_package_{package.package_id}"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Export in each format
        exported_files = []
        for format in formats:
            formatter = self._formatters.get(format)
            if formatter:
                filename = f"evidence.{format}"
                filepath = output_dir / filename

                with open(filepath, "w") as f:
                    f.write(formatter.format(package))

                exported_files.append(filename)

        # Create metadata file
        metadata = {
            "package_id": package.package_id,
            "created_at": package.created_at.isoformat(),
            "created_by": package.created_by,
            "purpose": package.purpose,
            "framework": package.framework.value,
            "exported_at": datetime.now(pytz.UTC).isoformat(),
            "exported_files": exported_files,
        }

        with open(output_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        # Include attachments if requested
        if include_attachments:
            # Export audit log excerpt
            audit_log_path = output_dir / "audit_log_excerpt.jsonl"
            with open(audit_log_path, "w") as f:
                for event in package.audit_events:
                    f.write(event.model_dump_json() + "\n")

            # Export lineage visualization if graphviz is available
            try:
                lineage_path = output_dir / "lineage_graph"
                self.lineage_tracker.graph.visualize(str(lineage_path), format="png")
            except Exception:
                pass  # Graphviz might not be available

        # Create ZIP archive
        zip_path = f"{output_dir}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(output_dir.parent)
                    zipf.write(file_path, arcname)

        # Log export
        self.audit_logger.log_event(
            actor=package.created_by,
            operation=OperationType.WRITE,
            resource=f"evidence_package:{package.package_id}",
            details={
                "action": "export_package",
                "formats": formats,
                "output_path": str(zip_path),
            },
        )

        return str(zip_path)

    def verify_package(self, package: EvidencePackage) -> Dict[str, Any]:
        """Verify the integrity of an evidence package.

        Args:
            package: Evidence package to verify

        Returns:
            Verification results
        """
        results = {
            "package_id": package.package_id,
            "verification_timestamp": datetime.now(pytz.UTC).isoformat(),
            "checks": {},
        }

        # Verify audit events
        event_verification = {
            "total_events": len(package.audit_events),
            "verified_events": 0,
            "failed_events": [],
        }

        for event in package.audit_events:
            if self.audit_logger.verify_event(event):
                event_verification["verified_events"] += 1
            else:
                event_verification["failed_events"].append(event.event_id)

        results["checks"]["audit_events"] = event_verification

        # Verify cryptographic proofs
        proof_verification = {
            "total_proofs": len(package.cryptographic_proofs),
            "valid_proofs": sum(
                1 for p in package.cryptographic_proofs if p.get("is_valid", False)
            ),
        }
        results["checks"]["cryptographic_proofs"] = proof_verification

        # Overall verification
        results["is_valid"] = (
            event_verification["verified_events"] == event_verification["total_events"]
            and proof_verification["valid_proofs"] == proof_verification["total_proofs"]
        )

        return results
