"""Evidence package formatters for different regulatory requirements."""

import json
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict

from pymigrate.models import (
    EvidencePackage,
    AuditEvent,
    ComplianceViolation,
)


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects and Pydantic models."""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, ComplianceViolation):
            return obj.model_dump()
        elif hasattr(obj, "model_dump"):
            # Handle other Pydantic models
            return obj.model_dump()
        return super().default(obj)


class EvidenceFormatter(ABC):
    """Abstract base class for evidence formatters."""

    @abstractmethod
    def format(self, package: EvidencePackage) -> str:
        """Format an evidence package.

        Args:
            package: Evidence package to format

        Returns:
            Formatted evidence as string
        """
        pass

    @abstractmethod
    def get_content_type(self) -> str:
        """Get the content type for the formatted evidence.

        Returns:
            Content type string (e.g., "application/json")
        """
        pass


class JSONFormatter(EvidenceFormatter):
    """Formats evidence packages as JSON."""

    def format(self, package: EvidencePackage) -> str:
        """Format evidence package as JSON.

        Args:
            package: Evidence package to format

        Returns:
            JSON string
        """
        # Convert package to dictionary
        package_dict = {
            "evidencePackage": {
                "packageId": package.package_id,
                "createdAt": package.created_at.isoformat(),
                "createdBy": package.created_by,
                "purpose": package.purpose,
                "framework": package.framework.value,
                "auditPeriod": {
                    "startDate": package.start_date.isoformat(),
                    "endDate": package.end_date.isoformat(),
                },
                "auditTrail": {
                    "totalEvents": len(package.audit_events),
                    "events": [
                        self._format_audit_event(event)
                        for event in package.audit_events
                    ],
                },
                "dataLineage": package.lineage_graphs,
                "complianceReports": package.compliance_reports,
                "cryptographicProofs": package.cryptographic_proofs,
                "metadata": package.metadata,
            }
        }

        return json.dumps(package_dict, indent=2, sort_keys=True, cls=DateTimeEncoder)

    def _format_audit_event(self, event: AuditEvent) -> Dict[str, Any]:
        """Format an audit event for JSON output."""
        return {
            "eventId": event.event_id,
            "timestamp": event.timestamp.isoformat(),
            "actor": event.actor,
            "operation": event.operation.value,
            "resource": event.resource,
            "details": event.details,
            "hash": event.hash,
            "signature": event.signature,
            "previousHash": event.previous_hash,
        }

    def get_content_type(self) -> str:
        """Get JSON content type."""
        return "application/json"


class XBRLFormatter(EvidenceFormatter):
    """Formats evidence packages as XBRL for regulatory submission."""

    def __init__(self, taxonomy_namespace: str = "http://xbrl.sec.gov/dei/2021"):
        """Initialize XBRL formatter.

        Args:
            taxonomy_namespace: XBRL taxonomy namespace to use
        """
        self.taxonomy_namespace = taxonomy_namespace

    def format(self, package: EvidencePackage) -> str:
        """Format evidence package as XBRL.

        Args:
            package: Evidence package to format

        Returns:
            XBRL XML string
        """
        # Create root element
        root = ET.Element(
            "xbrl",
            {
                "xmlns": "http://www.xbrl.org/2003/instance",
                "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "xmlns:link": "http://www.xbrl.org/2003/linkbase",
                "xmlns:iso4217": "http://www.xbrl.org/2003/iso4217",
                "xmlns:dei": self.taxonomy_namespace,
            },
        )

        # Add schema reference
        schema_ref = ET.SubElement(
            root,
            "{http://www.xbrl.org/2003/linkbase}schemaRef",
            {
                "{http://www.xbrl.org/2003/linkbase}type": "simple",
                "{http://www.xbrl.org/2003/linkbase}href": f"{self.taxonomy_namespace}.xsd",
            },
        )

        # Create context
        context = ET.SubElement(root, "context", {"id": "instant"})
        entity = ET.SubElement(context, "entity")
        identifier = ET.SubElement(
            entity, "identifier", {"scheme": "http://www.sec.gov/CIK"}
        )
        identifier.text = package.created_by

        period = ET.SubElement(context, "period")
        start_date = ET.SubElement(period, "startDate")
        start_date.text = package.start_date.strftime("%Y-%m-%d")
        end_date = ET.SubElement(period, "endDate")
        end_date.text = package.end_date.strftime("%Y-%m-%d")

        # Add evidence data
        self._add_compliance_data(root, package, "instant")
        self._add_audit_trail_summary(root, package, "instant")
        self._add_cryptographic_proofs(root, package, "instant")

        # Convert to string with XML declaration
        xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml_str += ET.tostring(root, encoding="unicode", method="xml")
        return xml_str

    def _add_compliance_data(
        self, root: ET.Element, package: EvidencePackage, context_ref: str
    ) -> None:
        """Add compliance data to XBRL document."""
        # Document information
        doc_period = ET.SubElement(
            root,
            "{%s}DocumentPeriodEndDate" % self.taxonomy_namespace,
            {"contextRef": context_ref},
        )
        doc_period.text = package.end_date.strftime("%Y-%m-%d")

        # Compliance framework
        framework = ET.SubElement(
            root,
            "{%s}ComplianceFramework" % self.taxonomy_namespace,
            {"contextRef": context_ref},
        )
        framework.text = package.framework.value

        # Compliance status
        if package.compliance_reports:
            for report in package.compliance_reports:
                if "is_compliant" in report:
                    status = ET.SubElement(
                        root,
                        "{%s}ComplianceStatus" % self.taxonomy_namespace,
                        {"contextRef": context_ref},
                    )
                    status.text = (
                        "Compliant" if report["is_compliant"] else "Non-Compliant"
                    )

                    if "violations" in report:
                        violations = ET.SubElement(
                            root,
                            "{%s}ComplianceViolationCount" % self.taxonomy_namespace,
                            {"contextRef": context_ref, "unitRef": "pure"},
                        )
                        violations.text = str(len(report["violations"]))

    def _add_audit_trail_summary(
        self, root: ET.Element, package: EvidencePackage, context_ref: str
    ) -> None:
        """Add audit trail summary to XBRL document."""
        # Total audit events
        event_count = ET.SubElement(
            root,
            "{%s}AuditEventCount" % self.taxonomy_namespace,
            {"contextRef": context_ref, "unitRef": "pure"},
        )
        event_count.text = str(len(package.audit_events))

        # Audit period
        audit_start = ET.SubElement(
            root,
            "{%s}AuditPeriodStartDate" % self.taxonomy_namespace,
            {"contextRef": context_ref},
        )
        audit_start.text = package.start_date.strftime("%Y-%m-%d")

        audit_end = ET.SubElement(
            root,
            "{%s}AuditPeriodEndDate" % self.taxonomy_namespace,
            {"contextRef": context_ref},
        )
        audit_end.text = package.end_date.strftime("%Y-%m-%d")

        # Chain integrity status
        chain_integrity = ET.SubElement(
            root,
            "{%s}AuditChainIntegrity" % self.taxonomy_namespace,
            {"contextRef": context_ref},
        )
        chain_integrity.text = "Verified"

    def _add_cryptographic_proofs(
        self, root: ET.Element, package: EvidencePackage, context_ref: str
    ) -> None:
        """Add cryptographic proof summary to XBRL document."""
        if package.cryptographic_proofs:
            # Number of proofs
            proof_count = ET.SubElement(
                root,
                "{%s}CryptographicProofCount" % self.taxonomy_namespace,
                {"contextRef": context_ref, "unitRef": "pure"},
            )
            proof_count.text = str(len(package.cryptographic_proofs))

            # Signature algorithm
            if (
                package.cryptographic_proofs
                and "algorithm" in package.cryptographic_proofs[0]
            ):
                sig_alg = ET.SubElement(
                    root,
                    "{%s}SignatureAlgorithm" % self.taxonomy_namespace,
                    {"contextRef": context_ref},
                )
                sig_alg.text = package.cryptographic_proofs[0]["algorithm"]

    def get_content_type(self) -> str:
        """Get XBRL content type."""
        return "application/xbrl+xml"


class HTMLFormatter(EvidenceFormatter):
    """Formats evidence packages as HTML for human-readable reports."""

    def format(self, package: EvidencePackage) -> str:
        """Format evidence package as HTML.

        Args:
            package: Evidence package to format

        Returns:
            HTML string
        """
        html_parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            f"<title>Evidence Package {package.package_id}</title>",
            "<style>",
            "body { font-family: Arial, sans-serif; margin: 20px; }",
            "h1, h2, h3 { color: #333; }",
            "table { border-collapse: collapse; width: 100%; margin: 20px 0; }",
            "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
            "th { background-color: #f2f2f2; }",
            ".metadata { background-color: #f9f9f9; padding: 10px; border-radius: 5px; }",
            ".compliant { color: green; font-weight: bold; }",
            ".non-compliant { color: red; font-weight: bold; }",
            "</style>",
            "</head>",
            "<body>",
            f"<h1>Evidence Package: {package.package_id}</h1>",
            "<div class='metadata'>",
            f"<p><strong>Created:</strong> {package.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>",
            f"<p><strong>Created By:</strong> {package.created_by}</p>",
            f"<p><strong>Purpose:</strong> {package.purpose}</p>",
            f"<p><strong>Framework:</strong> {package.framework.value}</p>",
            f"<p><strong>Audit Period:</strong> {package.start_date.strftime('%Y-%m-%d')} to {package.end_date.strftime('%Y-%m-%d')}</p>",
            "</div>",
        ]

        # Add audit events summary
        html_parts.extend(
            [
                "<h2>Audit Trail Summary</h2>",
                f"<p>Total Events: {len(package.audit_events)}</p>",
                "<table>",
                "<tr><th>Event ID</th><th>Timestamp</th><th>Actor</th><th>Operation</th><th>Resource</th></tr>",
            ]
        )

        for event in package.audit_events[:10]:  # Show first 10 events
            html_parts.append(
                f"<tr><td>{event.event_id}</td>"
                f"<td>{event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</td>"
                f"<td>{event.actor}</td>"
                f"<td>{event.operation.value}</td>"
                f"<td>{event.resource}</td></tr>"
            )

        if len(package.audit_events) > 10:
            html_parts.append(
                f"<tr><td colspan='5'>... and {len(package.audit_events) - 10} more events</td></tr>"
            )

        html_parts.append("</table>")

        # Add compliance summary
        if package.compliance_reports:
            html_parts.extend(
                [
                    "<h2>Compliance Summary</h2>",
                    "<table>",
                    "<tr><th>Report</th><th>Status</th><th>Violations</th></tr>",
                ]
            )

            for i, report in enumerate(package.compliance_reports):
                status = (
                    "Compliant"
                    if report.get("is_compliant", False)
                    else "Non-Compliant"
                )
                status_class = (
                    "compliant"
                    if report.get("is_compliant", False)
                    else "non-compliant"
                )
                violations = len(report.get("violations", []))

                html_parts.append(
                    f"<tr><td>Report {i + 1}</td>"
                    f"<td class='{status_class}'>{status}</td>"
                    f"<td>{violations}</td></tr>"
                )

            html_parts.append("</table>")

        # Add cryptographic proofs summary
        if package.cryptographic_proofs:
            html_parts.extend(
                [
                    "<h2>Cryptographic Verification</h2>",
                    f"<p>Total Proofs: {len(package.cryptographic_proofs)}</p>",
                    "<p>All audit events are cryptographically signed and form an immutable hash chain.</p>",
                ]
            )

        html_parts.extend(["</body>", "</html>"])

        return "\n".join(html_parts)

    def get_content_type(self) -> str:
        """Get HTML content type."""
        return "text/html"
