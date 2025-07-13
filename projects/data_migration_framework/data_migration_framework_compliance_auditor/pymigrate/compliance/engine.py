"""Compliance rule engine implementation."""

import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

import pytz

from pymigrate.audit.logger import AuditLogger
from pymigrate.compliance.rules import RuleEvaluator, RuleRegistry
from pymigrate.models import (
    ComplianceFramework,
    ComplianceRule,
    ComplianceViolation,
    OperationType,
)


class ComplianceRuleEngine:
    """Processes and enforces compliance rules for data operations."""

    def __init__(
        self,
        rule_registry: Optional[RuleRegistry] = None,
        audit_logger: Optional[AuditLogger] = None,
        enforcement_mode: bool = True,
    ):
        """Initialize the compliance rule engine.

        Args:
            rule_registry: Registry of compliance rules
            audit_logger: Audit logger for compliance events
            enforcement_mode: If True, violations prevent operations; if False, only log
        """
        self.rule_registry = rule_registry or RuleRegistry()
        self.audit_logger = audit_logger
        self.enforcement_mode = enforcement_mode
        self._violation_history: List[ComplianceViolation] = []

    def validate_data_operation(
        self,
        operation_type: str,
        data: Dict[str, Any],
        context: Dict[str, Any],
        frameworks: Optional[List[ComplianceFramework]] = None,
    ) -> Dict[str, Any]:
        """Validate a data operation against compliance rules.

        Args:
            operation_type: Type of operation being performed
            data: Data involved in the operation
            context: Additional context (user, roles, metadata)
            frameworks: Specific frameworks to check (None = all)

        Returns:
            Dictionary with validation results
        """
        # Add operation context
        full_context = {
            **context,
            "operation_type": operation_type,
            "validation_timestamp": datetime.now(pytz.UTC),
        }

        # Get applicable rules
        if frameworks:
            rules = []
            for framework in frameworks:
                rules.extend(self.rule_registry.get_rules_by_framework(framework))
        else:
            rules = self.rule_registry.get_active_rules()

        # Evaluate each rule
        violations = []
        passed_rules = []

        for rule in rules:
            evaluator = self.rule_registry.get_evaluator(rule.rule_id)
            if not evaluator:
                continue

            try:
                if evaluator.evaluate(data, full_context):
                    passed_rules.append(rule.rule_id)
                else:
                    # Create violation record
                    violation_details = evaluator.get_violation_details(
                        data, full_context
                    )
                    violation = self._create_violation(
                        rule=rule,
                        resource=context.get("resource", "unknown"),
                        details=violation_details,
                    )
                    violations.append(violation)

            except Exception as e:
                # Rule evaluation error
                violation = self._create_violation(
                    rule=rule,
                    resource=context.get("resource", "unknown"),
                    details={"error": "Rule evaluation failed", "exception": str(e)},
                )
                violations.append(violation)

        # Log the validation
        if self.audit_logger:
            actor = context.get("actor", "system")
            self.audit_logger.log_event(
                actor=actor,
                operation=OperationType.VALIDATE,
                resource=context.get("resource", "unknown"),
                details={
                    "operation_type": operation_type,
                    "rules_evaluated": len(rules),
                    "rules_passed": len(passed_rules),
                    "violations_found": len(violations),
                    "enforcement_mode": self.enforcement_mode,
                },
            )

        # Determine if operation is allowed
        is_compliant = len(violations) == 0
        allow_operation = is_compliant or not self.enforcement_mode

        result = {
            "is_compliant": is_compliant,
            "allow_operation": allow_operation,
            "violations": violations,
            "passed_rules": passed_rules,
            "rules_evaluated": len(rules),
            "timestamp": datetime.now(pytz.UTC),
        }

        # Store violations in history
        self._violation_history.extend(violations)

        return result

    def _create_violation(
        self, rule: ComplianceRule, resource: str, details: Dict[str, Any]
    ) -> ComplianceViolation:
        """Create a compliance violation record.

        Args:
            rule: Rule that was violated
            resource: Resource involved
            details: Violation details

        Returns:
            Compliance violation record
        """
        return ComplianceViolation(
            violation_id=str(uuid.uuid4()),
            rule_id=rule.rule_id,
            timestamp=datetime.now(pytz.UTC),
            resource=resource,
            details={
                "rule_name": rule.name,
                "framework": rule.framework,
                "severity": rule.severity,
                **details,
            },
            remediation_required=rule.severity in ["CRITICAL", "HIGH"],
            remediation_status="PENDING",
        )

    def check_data_compliance(
        self, data: Dict[str, Any], frameworks: List[ComplianceFramework]
    ) -> Dict[str, Any]:
        """Check if data meets compliance requirements.

        Args:
            data: Data to check
            frameworks: Frameworks to validate against

        Returns:
            Compliance check results
        """
        return self.validate_data_operation(
            operation_type="data_check",
            data=data,
            context={"purpose": "compliance_check"},
            frameworks=frameworks,
        )

    def validate_migration(
        self,
        source_data: Dict[str, Any],
        destination_data: Dict[str, Any],
        transformation_details: Dict[str, Any],
        actor: str,
    ) -> Dict[str, Any]:
        """Validate a complete data migration for compliance.

        Args:
            source_data: Original data
            destination_data: Migrated data
            transformation_details: Details of transformations applied
            actor: User performing the migration

        Returns:
            Validation results
        """
        # Validate source data access
        source_result = self.validate_data_operation(
            operation_type="read",
            data=source_data,
            context={
                "actor": actor,
                "resource": "source_data",
                "stage": "pre_migration",
            },
        )

        # Validate transformation
        transform_result = self.validate_data_operation(
            operation_type="transform",
            data=transformation_details,
            context={
                "actor": actor,
                "resource": "transformation",
                "source_data": source_data,
                "stage": "migration",
            },
        )

        # Validate destination data
        destination_result = self.validate_data_operation(
            operation_type="write",
            data=destination_data,
            context={
                "actor": actor,
                "resource": "destination_data",
                "stage": "post_migration",
            },
        )

        # Combine results
        all_violations = []
        all_violations.extend(source_result.get("violations", []))
        all_violations.extend(transform_result.get("violations", []))
        all_violations.extend(destination_result.get("violations", []))

        is_compliant = (
            source_result["is_compliant"]
            and transform_result["is_compliant"]
            and destination_result["is_compliant"]
        )

        return {
            "is_compliant": is_compliant,
            "allow_migration": is_compliant or not self.enforcement_mode,
            "source_validation": source_result,
            "transform_validation": transform_result,
            "destination_validation": destination_result,
            "total_violations": len(all_violations),
            "violations": all_violations,
            "timestamp": datetime.now(pytz.UTC),
        }

    def get_violation_history(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        rule_id: Optional[str] = None,
        resource: Optional[str] = None,
    ) -> List[ComplianceViolation]:
        """Get violation history with optional filters.

        Args:
            start_time: Start of time range
            end_time: End of time range
            rule_id: Filter by specific rule
            resource: Filter by specific resource

        Returns:
            List of violations matching criteria
        """
        violations = self._violation_history

        if start_time:
            if start_time.tzinfo is None:
                start_time = pytz.UTC.localize(start_time)
            violations = [v for v in violations if v.timestamp >= start_time]

        if end_time:
            if end_time.tzinfo is None:
                end_time = pytz.UTC.localize(end_time)
            violations = [v for v in violations if v.timestamp <= end_time]

        if rule_id:
            violations = [v for v in violations if v.rule_id == rule_id]

        if resource:
            violations = [v for v in violations if v.resource == resource]

        return violations

    def update_violation_status(
        self,
        violation_id: str,
        status: str,
        remediation_details: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Update the remediation status of a violation.

        Args:
            violation_id: ID of the violation
            status: New status (e.g., "REMEDIATED", "IN_PROGRESS")
            remediation_details: Details of remediation actions

        Returns:
            True if updated, False if not found
        """
        for violation in self._violation_history:
            if violation.violation_id == violation_id:
                violation.remediation_status = status
                if remediation_details:
                    violation.details["remediation_details"] = remediation_details

                # Log the update
                if self.audit_logger:
                    self.audit_logger.log_event(
                        actor="system",
                        operation=OperationType.WRITE,
                        resource=f"violation:{violation_id}",
                        details={
                            "action": "update_violation_status",
                            "new_status": status,
                            "remediation_details": remediation_details,
                        },
                    )

                return True

        return False

    def generate_compliance_report(
        self, framework: ComplianceFramework, start_time: datetime, end_time: datetime
    ) -> Dict[str, Any]:
        """Generate a compliance report for a specific framework.

        Args:
            framework: Compliance framework
            start_time: Report start time
            end_time: Report end time

        Returns:
            Compliance report data
        """
        # Get rules for framework
        rules = self.rule_registry.get_rules_by_framework(framework)

        # Get violations for time period
        violations = self.get_violation_history(
            start_time=start_time, end_time=end_time
        )

        # Filter violations by framework
        framework_violations = [
            v for v in violations if any(r.rule_id == v.rule_id for r in rules)
        ]

        # Calculate statistics
        total_violations = len(framework_violations)
        critical_violations = len(
            [v for v in framework_violations if v.details.get("severity") == "CRITICAL"]
        )
        high_violations = len(
            [v for v in framework_violations if v.details.get("severity") == "HIGH"]
        )

        remediated_violations = len(
            [v for v in framework_violations if v.remediation_status == "REMEDIATED"]
        )

        pending_violations = len(
            [v for v in framework_violations if v.remediation_status == "PENDING"]
        )

        # Group violations by rule
        violations_by_rule = {}
        for violation in framework_violations:
            rule_id = violation.rule_id
            if rule_id not in violations_by_rule:
                violations_by_rule[rule_id] = []
            violations_by_rule[rule_id].append(violation)

        return {
            "framework": framework,
            "report_period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
            },
            "summary": {
                "total_rules": len(rules),
                "total_violations": total_violations,
                "critical_violations": critical_violations,
                "high_violations": high_violations,
                "remediated_violations": remediated_violations,
                "pending_violations": pending_violations,
                "compliance_rate": 1.0
                - (pending_violations / max(total_violations, 1)),
            },
            "violations_by_rule": {
                rule_id: {
                    "rule_name": next(
                        (r.name for r in rules if r.rule_id == rule_id), "Unknown"
                    ),
                    "violation_count": len(violations),
                    "violations": [v.dict() for v in violations],
                }
                for rule_id, violations in violations_by_rule.items()
            },
            "generated_at": datetime.now(pytz.UTC).isoformat(),
        }

    def add_custom_rule(
        self,
        rule: ComplianceRule,
        evaluator_func: Callable[[Dict[str, Any], Dict[str, Any]], bool],
        violation_details_func: Callable[
            [Dict[str, Any], Dict[str, Any]], Dict[str, Any]
        ],
    ) -> None:
        """Add a custom compliance rule.

        Args:
            rule: Compliance rule definition
            evaluator_func: Function to evaluate compliance
            violation_details_func: Function to get violation details
        """

        # Create a custom evaluator
        class CustomEvaluator(RuleEvaluator):
            def evaluate(self, data: Dict[str, Any], context: Dict[str, Any]) -> bool:
                return evaluator_func(data, context)

            def get_violation_details(
                self, data: Dict[str, Any], context: Dict[str, Any]
            ) -> Dict[str, Any]:
                return violation_details_func(data, context)

        self.rule_registry.register_rule(rule, CustomEvaluator())
