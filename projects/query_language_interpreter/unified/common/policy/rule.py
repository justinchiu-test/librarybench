"""Rule representation and validation for query language interpreters."""

from typing import Any, Callable, Dict, List, Optional, Set, Union
from abc import ABC, abstractmethod

from common.policy.context import PolicyContext


class PolicyRule(ABC):
    """Base class for policy rules."""

    def __init__(
        self,
        rule_id: str,
        description: str = "",
        actions: List[str] = None,
        severity: str = "medium",
    ):
        """Initialize a policy rule.

        Args:
            rule_id: Unique rule identifier
            description: Rule description
            actions: List of actions this rule applies to (None for all)
            severity: Rule violation severity
        """
        self.rule_id = rule_id
        self.description = description
        self.actions = actions or []
        self.severity = severity

    def applies_to_action(self, action: str) -> bool:
        """Check if this rule applies to the given action.

        Args:
            action: Action to check

        Returns:
            bool: True if applicable, False otherwise
        """
        # If no actions specified, applies to all
        if not self.actions:
            return True
        
        return action in self.actions

    @abstractmethod
    def evaluate(self, context: PolicyContext) -> bool:
        """Evaluate the rule against a context.

        Args:
            context: Context to evaluate against

        Returns:
            bool: True if the rule is satisfied, False if violated
        """
        pass

    def get_violation_message(self, context: PolicyContext) -> str:
        """Get a message describing why the rule was violated.

        Args:
            context: Context that violated the rule

        Returns:
            str: Violation message
        """
        return self.description


class SimpleRule(PolicyRule):
    """Simple rule that uses a custom evaluation function."""

    def __init__(
        self,
        rule_id: str,
        evaluation_func: Callable[[PolicyContext], bool],
        description: str = "",
        actions: List[str] = None,
        severity: str = "medium",
        violation_message: str = "",
    ):
        """Initialize a simple rule.

        Args:
            rule_id: Unique rule identifier
            evaluation_func: Function that evaluates the rule
            description: Rule description
            actions: List of actions this rule applies to
            severity: Rule violation severity
            violation_message: Message to show when rule is violated
        """
        super().__init__(rule_id, description, actions, severity)
        self.evaluation_func = evaluation_func
        self.violation_message = violation_message or description

    def evaluate(self, context: PolicyContext) -> bool:
        """Evaluate the rule using the evaluation function.

        Args:
            context: Context to evaluate against

        Returns:
            bool: True if the rule is satisfied, False if violated
        """
        return self.evaluation_func(context)

    def get_violation_message(self, context: PolicyContext) -> str:
        """Get the violation message.

        Args:
            context: Context that violated the rule

        Returns:
            str: Violation message
        """
        return self.violation_message


class PermissionRule(PolicyRule):
    """Rule that checks for required permissions."""

    def __init__(
        self,
        rule_id: str,
        required_permissions: List[str],
        description: str = "",
        actions: List[str] = None,
        severity: str = "high",
    ):
        """Initialize a permission rule.

        Args:
            rule_id: Unique rule identifier
            required_permissions: List of required permissions
            description: Rule description
            actions: List of actions this rule applies to
            severity: Rule violation severity
        """
        super().__init__(rule_id, description, actions, severity)
        self.required_permissions = required_permissions

    def evaluate(self, context: PolicyContext) -> bool:
        """Check if the context has all required permissions.

        Args:
            context: Context to evaluate against

        Returns:
            bool: True if all permissions present, False otherwise
        """
        user_permissions = context.get("permissions", [])
        return all(perm in user_permissions for perm in self.required_permissions)

    def get_violation_message(self, context: PolicyContext) -> str:
        """Get a message about missing permissions.

        Args:
            context: Context that violated the rule

        Returns:
            str: Violation message
        """
        user_permissions = context.get("permissions", [])
        missing = [p for p in self.required_permissions if p not in user_permissions]
        return f"Missing required permissions: {', '.join(missing)}"


class RoleRule(PolicyRule):
    """Rule that checks for required roles."""

    def __init__(
        self,
        rule_id: str,
        allowed_roles: List[str],
        description: str = "",
        actions: List[str] = None,
        severity: str = "high",
        require_all: bool = False,
    ):
        """Initialize a role rule.

        Args:
            rule_id: Unique rule identifier
            allowed_roles: List of allowed roles
            description: Rule description
            actions: List of actions this rule applies to
            severity: Rule violation severity
            require_all: Whether all roles are required (True) or any (False)
        """
        super().__init__(rule_id, description, actions, severity)
        self.allowed_roles = allowed_roles
        self.require_all = require_all

    def evaluate(self, context: PolicyContext) -> bool:
        """Check if the context has the required roles.

        Args:
            context: Context to evaluate against

        Returns:
            bool: True if roles satisfy the rule, False otherwise
        """
        user_roles = context.get("roles", [])
        
        if self.require_all:
            return all(role in user_roles for role in self.allowed_roles)
        else:
            return any(role in user_roles for role in self.allowed_roles)

    def get_violation_message(self, context: PolicyContext) -> str:
        """Get a message about missing roles.

        Args:
            context: Context that violated the rule

        Returns:
            str: Violation message
        """
        if self.require_all:
            return f"User must have all of these roles: {', '.join(self.allowed_roles)}"
        else:
            return f"User must have at least one of these roles: {', '.join(self.allowed_roles)}"