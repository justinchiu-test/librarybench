"""Policy enforcement engine for query language interpreters."""

from typing import Any, Dict, List, Optional, Set, Union
from abc import ABC, abstractmethod

from common.policy.rule import PolicyRule
from common.policy.context import PolicyContext


class PolicyViolation:
    """Represents a policy violation."""

    def __init__(
        self,
        rule_id: str,
        severity: str = "medium",
        message: str = "",
        details: Dict[str, Any] = None,
    ):
        """Initialize a policy violation.

        Args:
            rule_id: ID of the violated rule
            severity: Violation severity
            message: Violation message
            details: Additional details
        """
        self.rule_id = rule_id
        self.severity = severity
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        """String representation of the violation.

        Returns:
            str: String representation
        """
        return f"PolicyViolation(rule={self.rule_id}, severity={self.severity}, message={self.message})"


class BasePolicyEngine:
    """Base class for policy enforcement engines."""

    def __init__(self):
        """Initialize a policy engine."""
        self.rules: Dict[str, PolicyRule] = {}

    def add_rule(self, rule: PolicyRule) -> None:
        """Add a rule to the engine.

        Args:
            rule: Rule to add
        """
        self.rules[rule.rule_id] = rule

    def remove_rule(self, rule_id: str) -> bool:
        """Remove a rule from the engine.

        Args:
            rule_id: ID of the rule to remove

        Returns:
            bool: True if removed, False if not found
        """
        if rule_id in self.rules:
            del self.rules[rule_id]
            return True
        return False

    def check_policy(self, action: str, context: Dict[str, Any]) -> bool:
        """Check if an action is allowed in the given context.

        Args:
            action: Action to check
            context: Action context

        Returns:
            bool: True if allowed, False if violates policy
        """
        # Convert dict to PolicyContext if needed
        if not isinstance(context, PolicyContext):
            context = PolicyContext(context)
        
        # Check all rules
        for rule in self.rules.values():
            if rule.applies_to_action(action) and not rule.evaluate(context):
                return False
        
        return True

    def get_violations(self, action: str, context: Dict[str, Any]) -> List[PolicyViolation]:
        """Get policy violations for an action in the given context.

        Args:
            action: Action to check
            context: Action context

        Returns:
            List[PolicyViolation]: List of policy violations
        """
        violations = []
        
        # Convert dict to PolicyContext if needed
        if not isinstance(context, PolicyContext):
            context = PolicyContext(context)
        
        # Check all rules
        for rule in self.rules.values():
            if rule.applies_to_action(action) and not rule.evaluate(context):
                violation = PolicyViolation(
                    rule_id=rule.rule_id,
                    severity=rule.severity,
                    message=rule.get_violation_message(context),
                    details={"action": action}
                )
                violations.append(violation)
        
        return violations