"""Access control policies and policy engine."""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set

import pytz

from pymigrate.models import AccessLevel


class AccessPolicy(ABC):
    """Abstract base class for access policies."""

    @abstractmethod
    def evaluate(
        self,
        principal: str,
        resource: str,
        action: AccessLevel,
        context: Dict[str, Any],
    ) -> bool:
        """Evaluate if access should be granted.

        Args:
            principal: User or role requesting access
            resource: Resource being accessed
            action: Type of access requested
            context: Additional context

        Returns:
            True if access should be granted
        """
        pass

    @abstractmethod
    def get_policy_name(self) -> str:
        """Get the name of this policy.

        Returns:
            Policy name
        """
        pass


class RoleBasedPolicy(AccessPolicy):
    """Role-based access control policy."""

    def __init__(self, role_permissions: Dict[str, Set[AccessLevel]]):
        """Initialize RBAC policy.

        Args:
            role_permissions: Mapping of roles to allowed permissions
        """
        self.role_permissions = role_permissions

    def evaluate(
        self,
        principal: str,
        resource: str,
        action: AccessLevel,
        context: Dict[str, Any],
    ) -> bool:
        """Evaluate RBAC policy."""
        user_roles = context.get("roles", [])

        for role in user_roles:
            if role in self.role_permissions:
                if action in self.role_permissions[role]:
                    return True

        return False

    def get_policy_name(self) -> str:
        """Get policy name."""
        return "RoleBasedAccessControl"


class TimeBasedPolicy(AccessPolicy):
    """Time-based access control policy."""

    def __init__(
        self,
        allowed_hours: Optional[tuple] = None,
        allowed_days: Optional[Set[int]] = None,
        max_session_duration: Optional[timedelta] = None,
    ):
        """Initialize time-based policy.

        Args:
            allowed_hours: Tuple of (start_hour, end_hour) in 24h format
            allowed_days: Set of allowed days (0=Monday, 6=Sunday)
            max_session_duration: Maximum session duration
        """
        self.allowed_hours = allowed_hours
        self.allowed_days = allowed_days
        self.max_session_duration = max_session_duration

    def evaluate(
        self,
        principal: str,
        resource: str,
        action: AccessLevel,
        context: Dict[str, Any],
    ) -> bool:
        """Evaluate time-based policy."""
        # Use timestamp from context if available, otherwise use current time
        current_time = context.get("timestamp", datetime.now(pytz.UTC))
        if isinstance(current_time, str):
            current_time = datetime.fromisoformat(current_time)
        if current_time.tzinfo is None:
            current_time = pytz.UTC.localize(current_time)

        # Check allowed hours
        if self.allowed_hours:
            current_hour = current_time.hour
            start_hour, end_hour = self.allowed_hours

            if start_hour <= end_hour:
                if not (start_hour <= current_hour < end_hour):
                    return False
            else:  # Spans midnight
                if not (current_hour >= start_hour or current_hour < end_hour):
                    return False

        # Check allowed days
        if self.allowed_days:
            current_day = current_time.weekday()
            if current_day not in self.allowed_days:
                return False

        # Check session duration
        if self.max_session_duration:
            session_start = context.get("session_start")
            if session_start:
                if isinstance(session_start, str):
                    session_start = datetime.fromisoformat(session_start)
                if session_start.tzinfo is None:
                    session_start = pytz.UTC.localize(session_start)

                session_duration = current_time - session_start
                if session_duration > self.max_session_duration:
                    return False

        return True

    def get_policy_name(self) -> str:
        """Get policy name."""
        return "TimeBasedAccessControl"


class ResourcePatternPolicy(AccessPolicy):
    """Resource pattern-based access control policy."""

    def __init__(self, patterns: Dict[str, Dict[str, Set[AccessLevel]]]):
        """Initialize resource pattern policy.

        Args:
            patterns: Mapping of resource patterns to principal permissions
        """
        self.patterns = patterns

    def evaluate(
        self,
        principal: str,
        resource: str,
        action: AccessLevel,
        context: Dict[str, Any],
    ) -> bool:
        """Evaluate resource pattern policy."""
        import fnmatch

        for pattern, permissions in self.patterns.items():
            if fnmatch.fnmatch(resource, pattern):
                if principal in permissions:
                    if action in permissions[principal]:
                        return True

                # Check for wildcard principal
                if "*" in permissions:
                    if action in permissions["*"]:
                        return True

        return False

    def get_policy_name(self) -> str:
        """Get policy name."""
        return "ResourcePatternAccessControl"


class AttributeBasedPolicy(AccessPolicy):
    """Attribute-based access control policy."""

    def __init__(self, rules: List[Dict[str, Any]]):
        """Initialize ABAC policy.

        Args:
            rules: List of attribute-based rules
        """
        self.rules = rules

    def evaluate(
        self,
        principal: str,
        resource: str,
        action: AccessLevel,
        context: Dict[str, Any],
    ) -> bool:
        """Evaluate ABAC policy."""
        for rule in self.rules:
            if self._evaluate_rule(rule, principal, resource, action, context):
                return True

        return False

    def _evaluate_rule(
        self,
        rule: Dict[str, Any],
        principal: str,
        resource: str,
        action: AccessLevel,
        context: Dict[str, Any],
    ) -> bool:
        """Evaluate a single ABAC rule."""
        # Check principal attributes
        if "principal_attributes" in rule:
            user_attributes = context.get("user_attributes", {})
            for attr, value in rule["principal_attributes"].items():
                if user_attributes.get(attr) != value:
                    return False

        # Check resource attributes
        if "resource_attributes" in rule:
            resource_attributes = context.get("resource_attributes", {})
            for attr, value in rule["resource_attributes"].items():
                if resource_attributes.get(attr) != value:
                    return False

        # Check action
        if "allowed_actions" in rule:
            if action not in rule["allowed_actions"]:
                return False

        # Check environment attributes
        if "environment" in rule:
            for attr, value in rule["environment"].items():
                if context.get(attr) != value:
                    return False

        return True

    def get_policy_name(self) -> str:
        """Get policy name."""
        return "AttributeBasedAccessControl"


class PolicyEngine:
    """Engine for evaluating multiple access policies."""

    def __init__(self, default_deny: bool = True):
        """Initialize policy engine.

        Args:
            default_deny: If True, deny access by default
        """
        self.policies: List[AccessPolicy] = []
        self.default_deny = default_deny

    def add_policy(self, policy: AccessPolicy) -> None:
        """Add a policy to the engine.

        Args:
            policy: Policy to add
        """
        self.policies.append(policy)

    def evaluate(
        self,
        principal: str,
        resource: str,
        action: AccessLevel,
        context: Dict[str, Any],
    ) -> tuple[bool, List[str]]:
        """Evaluate all policies.

        Args:
            principal: User or role requesting access
            resource: Resource being accessed
            action: Type of access requested
            context: Additional context

        Returns:
            Tuple of (allow_access, list_of_allowing_policies)
        """
        allowing_policies = []

        for policy in self.policies:
            if policy.evaluate(principal, resource, action, context):
                allowing_policies.append(policy.get_policy_name())

        # If any policy allows, grant access
        if allowing_policies:
            return True, allowing_policies

        # Otherwise, use default behavior
        return not self.default_deny, []

    def get_applicable_policies(
        self, principal: str, context: Dict[str, Any]
    ) -> List[str]:
        """Get all policies that might apply to a principal.

        Args:
            principal: User or role
            context: Additional context

        Returns:
            List of policy names
        """
        return [policy.get_policy_name() for policy in self.policies]
