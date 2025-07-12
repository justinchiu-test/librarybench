"""Compliance rule definitions and evaluation logic."""

import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

import pytz

from pymigrate.models import ComplianceFramework, ComplianceRule


class RuleEvaluator(ABC):
    """Abstract base class for rule evaluators."""

    @abstractmethod
    def evaluate(self, data: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate if data complies with the rule.

        Args:
            data: Data to evaluate
            context: Additional context for evaluation

        Returns:
            True if compliant, False otherwise
        """
        pass

    @abstractmethod
    def get_violation_details(
        self, data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get details about why the rule was violated.

        Args:
            data: Data that violated the rule
            context: Additional context

        Returns:
            Dictionary with violation details
        """
        pass


class DataRetentionEvaluator(RuleEvaluator):
    """Evaluates data retention compliance."""

    def __init__(self, max_retention_days: int):
        """Initialize the evaluator.

        Args:
            max_retention_days: Maximum allowed retention period in days
        """
        self.max_retention_days = max_retention_days

    def evaluate(self, data: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if data retention is within limits."""
        creation_date = data.get("creation_date")
        if not creation_date:
            return False

        if isinstance(creation_date, str):
            creation_date = datetime.fromisoformat(creation_date)

        if creation_date.tzinfo is None:
            creation_date = pytz.UTC.localize(creation_date)

        retention_period = datetime.now(pytz.UTC) - creation_date
        return retention_period.days <= self.max_retention_days

    def get_violation_details(
        self, data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get retention violation details."""
        creation_date = data.get("creation_date")
        if isinstance(creation_date, str):
            creation_date = datetime.fromisoformat(creation_date)

        if creation_date.tzinfo is None:
            creation_date = pytz.UTC.localize(creation_date)

        retention_period = datetime.now(pytz.UTC) - creation_date

        return {
            "violation_type": "data_retention_exceeded",
            "max_retention_days": self.max_retention_days,
            "actual_retention_days": retention_period.days,
            "creation_date": creation_date.isoformat(),
            "remediation": "Archive or delete data exceeding retention period",
        }


class PersonalDataEvaluator(RuleEvaluator):
    """Evaluates personal data handling compliance."""

    def __init__(self, allowed_fields: Set[str], encryption_required: bool = True):
        """Initialize the evaluator.

        Args:
            allowed_fields: Set of allowed personal data fields
            encryption_required: Whether encryption is required
        """
        self.allowed_fields = allowed_fields
        self.encryption_required = encryption_required
        self.pii_patterns = {
            "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
            "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
            "phone": re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"),
            "credit_card": re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"),
        }

    def evaluate(self, data: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if personal data is handled correctly."""
        # If data is empty or only contains allowed fields, check encryption
        data_fields = set(data.keys())

        # Check if all fields are allowed
        if data_fields.issubset(self.allowed_fields):
            # If encryption is required and data might contain personal info
            if self.encryption_required:
                is_encrypted = context.get("is_encrypted", False)
                # Even allowed fields need encryption if they contain personal data
                if not is_encrypted and len(data) > 0:
                    return False
            return True

        # Check for unauthorized personal data fields
        unauthorized_fields = data_fields - self.allowed_fields

        for field in unauthorized_fields:
            value = str(data.get(field, ""))
            # Check if field contains PII
            for pii_type, pattern in self.pii_patterns.items():
                if pattern.search(value):
                    return False

        # Check encryption if required
        if self.encryption_required:
            is_encrypted = context.get("is_encrypted", False)
            if not is_encrypted and self._contains_personal_data(data):
                return False

        return True

    def _contains_personal_data(self, data: Dict[str, Any]) -> bool:
        """Check if data contains personal information."""
        for value in data.values():
            value_str = str(value)
            for pattern in self.pii_patterns.values():
                if pattern.search(value_str):
                    return True
        return False

    def get_violation_details(
        self, data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get personal data violation details."""
        violations = []

        # Check if all fields are allowed but encryption is missing
        data_fields = set(data.keys())
        if data_fields.issubset(self.allowed_fields):
            if self.encryption_required:
                is_encrypted = context.get("is_encrypted", False)
                if not is_encrypted and len(data) > 0:
                    violations.append(
                        {
                            "issue": "Personal data not encrypted",
                            "requirement": "All personal data must be encrypted",
                        }
                    )
        else:
            # Check for unauthorized fields
            unauthorized_fields = data_fields - self.allowed_fields

            for field in unauthorized_fields:
                value = str(data.get(field, ""))
                for pii_type, pattern in self.pii_patterns.items():
                    if pattern.search(value):
                        violations.append(
                            {
                                "field": field,
                                "pii_type": pii_type,
                                "issue": "Unauthorized personal data field",
                            }
                        )

            # Check encryption
            if self.encryption_required:
                is_encrypted = context.get("is_encrypted", False)
                if not is_encrypted and self._contains_personal_data(data):
                    violations.append(
                        {
                            "issue": "Personal data not encrypted",
                            "requirement": "All personal data must be encrypted",
                        }
                    )

        return {
            "violation_type": "personal_data_compliance",
            "violations": violations,
            "remediation": "Remove unauthorized fields or apply proper encryption",
        }


class AccessControlEvaluator(RuleEvaluator):
    """Evaluates access control compliance."""

    def __init__(self, required_roles: Set[str], max_access_duration_hours: int = 24):
        """Initialize the evaluator.

        Args:
            required_roles: Set of roles required for access
            max_access_duration_hours: Maximum access duration allowed
        """
        self.required_roles = required_roles
        self.max_access_duration_hours = max_access_duration_hours

    def evaluate(self, data: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if access control requirements are met."""
        # Check if user has required roles
        user_roles = set(context.get("user_roles", []))
        if not user_roles.intersection(self.required_roles):
            return False

        # Check access duration
        access_granted_at = context.get("access_granted_at")
        if access_granted_at:
            if isinstance(access_granted_at, str):
                access_granted_at = datetime.fromisoformat(access_granted_at)

            if access_granted_at.tzinfo is None:
                access_granted_at = pytz.UTC.localize(access_granted_at)

            access_duration = datetime.now(pytz.UTC) - access_granted_at
            if access_duration.total_seconds() > self.max_access_duration_hours * 3600:
                return False

        return True

    def get_violation_details(
        self, data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get access control violation details."""
        violations = []

        # Check roles
        user_roles = set(context.get("user_roles", []))
        missing_roles = self.required_roles - user_roles
        if missing_roles:
            violations.append(
                {
                    "issue": "Missing required roles",
                    "required_roles": list(self.required_roles),
                    "user_roles": list(user_roles),
                    "missing_roles": list(missing_roles),
                }
            )

        # Check duration
        access_granted_at = context.get("access_granted_at")
        if access_granted_at:
            if isinstance(access_granted_at, str):
                access_granted_at = datetime.fromisoformat(access_granted_at)

            if access_granted_at.tzinfo is None:
                access_granted_at = pytz.UTC.localize(access_granted_at)

            access_duration = datetime.now(pytz.UTC) - access_granted_at
            duration_hours = access_duration.total_seconds() / 3600

            if duration_hours > self.max_access_duration_hours:
                violations.append(
                    {
                        "issue": "Access duration exceeded",
                        "max_hours": self.max_access_duration_hours,
                        "actual_hours": round(duration_hours, 2),
                        "access_granted_at": access_granted_at.isoformat(),
                    }
                )

        return {
            "violation_type": "access_control",
            "violations": violations,
            "remediation": "Grant required roles or refresh access tokens",
        }


class RuleRegistry:
    """Registry for compliance rules and their evaluators."""

    def __init__(self):
        """Initialize the rule registry."""
        self._rules: Dict[str, ComplianceRule] = {}
        self._evaluators: Dict[str, RuleEvaluator] = {}
        self._initialize_default_rules()

    def _initialize_default_rules(self) -> None:
        """Initialize default compliance rules."""
        # GDPR data retention rule
        gdpr_retention = ComplianceRule(
            rule_id="gdpr-retention-001",
            name="GDPR Data Retention Limit",
            framework=ComplianceFramework.GDPR,
            description="Personal data must not be retained longer than necessary",
            severity="HIGH",
            rule_logic={"max_retention_days": 730},  # 2 years
            version="1.0",
            effective_date=datetime(2018, 5, 25, tzinfo=pytz.UTC),
        )
        self.register_rule(
            gdpr_retention, DataRetentionEvaluator(max_retention_days=730)
        )

        # GDPR personal data protection
        gdpr_pii = ComplianceRule(
            rule_id="gdpr-pii-001",
            name="GDPR Personal Data Protection",
            framework=ComplianceFramework.GDPR,
            description="Personal data must be properly protected",
            severity="CRITICAL",
            rule_logic={
                "allowed_fields": ["name", "email", "user_id"],
                "encryption_required": True,
            },
            version="1.0",
            effective_date=datetime(2018, 5, 25, tzinfo=pytz.UTC),
        )
        self.register_rule(
            gdpr_pii,
            PersonalDataEvaluator(
                allowed_fields={"name", "email", "user_id"}, encryption_required=True
            ),
        )

        # SOX access control
        sox_access = ComplianceRule(
            rule_id="sox-access-001",
            name="SOX Financial Data Access Control",
            framework=ComplianceFramework.SOX,
            description="Financial data access must be restricted and time-limited",
            severity="CRITICAL",
            rule_logic={
                "required_roles": ["finance", "auditor"],
                "max_access_duration_hours": 8,
            },
            version="1.0",
            effective_date=datetime(2002, 7, 30, tzinfo=pytz.UTC),
        )
        self.register_rule(
            sox_access,
            AccessControlEvaluator(
                required_roles={"finance", "auditor"}, max_access_duration_hours=8
            ),
        )

        # HIPAA data retention
        hipaa_retention = ComplianceRule(
            rule_id="hipaa-retention-001",
            name="HIPAA Medical Records Retention",
            framework=ComplianceFramework.HIPAA,
            description="Medical records must be retained for minimum period",
            severity="HIGH",
            rule_logic={"min_retention_days": 2190},  # 6 years
            version="1.0",
            effective_date=datetime(1996, 8, 21, tzinfo=pytz.UTC),
        )
        # For HIPAA, we'll use a custom evaluator that checks minimum retention
        self.register_rule(
            hipaa_retention, DataRetentionEvaluator(max_retention_days=10000)
        )

    def register_rule(self, rule: ComplianceRule, evaluator: RuleEvaluator) -> None:
        """Register a compliance rule with its evaluator.

        Args:
            rule: Compliance rule to register
            evaluator: Evaluator for the rule
        """
        self._rules[rule.rule_id] = rule
        self._evaluators[rule.rule_id] = evaluator

    def get_rule(self, rule_id: str) -> Optional[ComplianceRule]:
        """Get a rule by ID.

        Args:
            rule_id: ID of the rule

        Returns:
            Rule if found, None otherwise
        """
        return self._rules.get(rule_id)

    def get_evaluator(self, rule_id: str) -> Optional[RuleEvaluator]:
        """Get an evaluator by rule ID.

        Args:
            rule_id: ID of the rule

        Returns:
            Evaluator if found, None otherwise
        """
        return self._evaluators.get(rule_id)

    def get_rules_by_framework(
        self, framework: ComplianceFramework
    ) -> List[ComplianceRule]:
        """Get all rules for a specific framework.

        Args:
            framework: Compliance framework

        Returns:
            List of rules for the framework
        """
        return [rule for rule in self._rules.values() if rule.framework == framework]

    def get_active_rules(
        self, as_of_date: Optional[datetime] = None
    ) -> List[ComplianceRule]:
        """Get all currently active rules.

        Args:
            as_of_date: Date to check (defaults to now)

        Returns:
            List of active rules
        """
        if as_of_date is None:
            as_of_date = datetime.now(pytz.UTC)
        elif as_of_date.tzinfo is None:
            as_of_date = pytz.UTC.localize(as_of_date)

        active_rules = []
        for rule in self._rules.values():
            if rule.effective_date <= as_of_date:
                if rule.expiry_date is None or rule.expiry_date > as_of_date:
                    active_rules.append(rule)

        return active_rules
