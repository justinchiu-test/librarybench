"""Access control manager implementation."""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set

import pytz

from pymigrate.access.policies import PolicyEngine, RoleBasedPolicy
from pymigrate.audit.logger import AuditLogger
from pymigrate.models import (
    AccessAttempt,
    AccessControlEntry,
    AccessLevel,
    OperationType,
)


class AccessControlManager:
    """Manages access control with privileged operation logging."""

    def __init__(
        self,
        audit_logger: Optional[AuditLogger] = None,
        policy_engine: Optional[PolicyEngine] = None,
        enable_caching: bool = True,
    ):
        """Initialize access control manager.

        Args:
            audit_logger: Audit logger for access events
            policy_engine: Policy engine for access decisions
            enable_caching: Whether to cache access decisions
        """
        self.audit_logger = audit_logger
        self.policy_engine = policy_engine or self._create_default_policy_engine()
        self.enable_caching = enable_caching

        # Access control entries storage
        self._access_entries: Dict[str, AccessControlEntry] = {}

        # Access attempt history
        self._access_attempts: List[AccessAttempt] = []

        # Cache for access decisions
        self._access_cache: Dict[str, tuple[bool, datetime]] = {}
        self._cache_ttl = timedelta(minutes=5)

    def _create_default_policy_engine(self) -> PolicyEngine:
        """Create default policy engine with basic policies."""
        engine = PolicyEngine(default_deny=True)

        # Add default RBAC policy
        default_roles = {
            "admin": {
                AccessLevel.READ,
                AccessLevel.WRITE,
                AccessLevel.DELETE,
                AccessLevel.ADMIN,
                AccessLevel.AUDIT,
            },
            "auditor": {AccessLevel.READ, AccessLevel.AUDIT},
            "operator": {AccessLevel.READ, AccessLevel.WRITE},
            "viewer": {AccessLevel.READ},
        }
        engine.add_policy(RoleBasedPolicy(default_roles))

        # Don't add time-based policy by default as it can interfere with tests
        # Users can add it explicitly if needed

        return engine

    def grant_access(
        self,
        principal: str,
        resource: str,
        permissions: Set[AccessLevel],
        granted_by: str,
        expires_at: Optional[datetime] = None,
        conditions: Optional[Dict[str, Any]] = None,
    ) -> AccessControlEntry:
        """Grant access to a resource.

        Args:
            principal: User or role to grant access to
            resource: Resource to grant access to
            permissions: Set of permissions to grant
            granted_by: User granting the access
            expires_at: When the access expires
            conditions: Additional conditions for access

        Returns:
            Created access control entry
        """
        ace = AccessControlEntry(
            ace_id=str(uuid.uuid4()),
            principal=principal,
            resource=resource,
            permissions=permissions,
            conditions=conditions or {},
            granted_by=granted_by,
            granted_at=datetime.now(pytz.UTC),
            expires_at=expires_at,
            is_active=True,
        )

        self._access_entries[ace.ace_id] = ace

        # Clear cache for this principal/resource
        self._clear_cache_for_principal_resource(principal, resource)

        # Log the grant
        if self.audit_logger:
            self.audit_logger.log_event(
                actor=granted_by,
                operation=OperationType.WRITE,
                resource=f"access:{resource}",
                details={
                    "action": "grant_access",
                    "principal": principal,
                    "permissions": [p.value for p in permissions],
                    "expires_at": expires_at.isoformat() if expires_at else None,
                    "ace_id": ace.ace_id,
                },
            )

        return ace

    def revoke_access(self, ace_id: str, revoked_by: str) -> bool:
        """Revoke an access control entry.

        Args:
            ace_id: ID of the access control entry
            revoked_by: User revoking the access

        Returns:
            True if revoked, False if not found
        """
        if ace_id not in self._access_entries:
            return False

        ace = self._access_entries[ace_id]
        ace.is_active = False

        # Clear cache
        self._clear_cache_for_principal_resource(ace.principal, ace.resource)

        # Log the revocation
        if self.audit_logger:
            self.audit_logger.log_event(
                actor=revoked_by,
                operation=OperationType.DELETE,
                resource=f"access:{ace.resource}",
                details={
                    "action": "revoke_access",
                    "principal": ace.principal,
                    "ace_id": ace_id,
                },
            )

        return True

    def check_access(
        self,
        principal: str,
        resource: str,
        action: AccessLevel,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Check if a principal has access to perform an action on a resource.

        Args:
            principal: User or role requesting access
            resource: Resource being accessed
            action: Type of access requested
            context: Additional context

        Returns:
            True if access is allowed
        """
        # Check cache first
        if self.enable_caching:
            cache_key = f"{principal}:{resource}:{action.value}"
            if cache_key in self._access_cache:
                cached_result, cache_time = self._access_cache[cache_key]
                if datetime.now(pytz.UTC) - cache_time < self._cache_ttl:
                    return cached_result

        # Build full context
        full_context = context or {}
        full_context["timestamp"] = datetime.now(pytz.UTC)

        # Check explicit ACEs first
        has_explicit_access = self._check_explicit_access(
            principal, resource, action, full_context
        )

        # If explicit access exists, use it
        if has_explicit_access is not None:
            granted = has_explicit_access
            allowing_policies = ["Explicit ACE"] if granted else []
        else:
            # Otherwise, use policy engine
            granted, allowing_policies = self.policy_engine.evaluate(
                principal, resource, action, full_context
            )

        full_context["allowing_policies"] = allowing_policies

        # Record the access attempt
        attempt = AccessAttempt(
            attempt_id=str(uuid.uuid4()),
            timestamp=datetime.now(pytz.UTC),
            principal=principal,
            resource=resource,
            operation=action,
            granted=granted,
            reason="Explicit ACE"
            if has_explicit_access is not None
            else f"Policies: {allowing_policies}"
            if granted
            else "Access denied",
            metadata=full_context,
        )
        self._access_attempts.append(attempt)

        # Log the attempt
        if self.audit_logger:
            self.audit_logger.log_event(
                actor=principal,
                operation=OperationType.READ if granted else OperationType.VALIDATE,
                resource=resource,
                details={
                    "action": "access_attempt",
                    "requested_operation": action.value,
                    "granted": granted,
                    "attempt_id": attempt.attempt_id,
                },
            )

        # Cache the result
        if self.enable_caching:
            self._access_cache[cache_key] = (granted, datetime.now(pytz.UTC))

        return granted

    def _check_explicit_access(
        self,
        principal: str,
        resource: str,
        action: AccessLevel,
        context: Dict[str, Any],
    ) -> Optional[bool]:
        """Check explicit access control entries.

        Args:
            principal: User or role
            resource: Resource
            action: Requested action
            context: Context

        Returns:
            True if allowed, False if denied, None if no explicit entry
        """
        current_time = context.get("timestamp", datetime.now(pytz.UTC))

        for ace in self._access_entries.values():
            if not ace.is_active:
                continue

            if ace.principal != principal or ace.resource != resource:
                continue

            # Check expiration
            if ace.expires_at and ace.expires_at < current_time:
                continue

            # Check permissions
            if action in ace.permissions:
                # Check conditions
                if self._evaluate_conditions(ace.conditions, context):
                    return True
                else:
                    # Conditions not met, explicitly deny
                    return False

        return None

    def _evaluate_conditions(
        self, conditions: Dict[str, Any], context: Dict[str, Any]
    ) -> bool:
        """Evaluate access conditions.

        Args:
            conditions: Conditions to evaluate
            context: Context to evaluate against

        Returns:
            True if all conditions are met
        """
        for key, expected_value in conditions.items():
            if key not in context:
                return False

            actual_value = context[key]

            # Handle different condition types
            if isinstance(expected_value, list):
                if actual_value not in expected_value:
                    return False
            elif isinstance(expected_value, dict):
                # Handle complex conditions (e.g., ranges)
                if "min" in expected_value and actual_value < expected_value["min"]:
                    return False
                if "max" in expected_value and actual_value > expected_value["max"]:
                    return False
            else:
                if actual_value != expected_value:
                    return False

        return True

    def _clear_cache_for_principal_resource(
        self, principal: str, resource: str
    ) -> None:
        """Clear cache entries for a principal/resource combination."""
        if not self.enable_caching:
            return

        keys_to_remove = []
        for key in self._access_cache:
            if key.startswith(f"{principal}:{resource}:"):
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self._access_cache[key]

    def get_principal_permissions(
        self, principal: str, resource: Optional[str] = None
    ) -> Dict[str, Set[AccessLevel]]:
        """Get all permissions for a principal.

        Args:
            principal: User or role
            resource: Optional resource filter

        Returns:
            Dictionary of resource to permissions
        """
        permissions_by_resource = {}
        current_time = datetime.now(pytz.UTC)

        for ace in self._access_entries.values():
            if not ace.is_active or ace.principal != principal:
                continue

            if resource and ace.resource != resource:
                continue

            if ace.expires_at and ace.expires_at < current_time:
                continue

            if ace.resource not in permissions_by_resource:
                permissions_by_resource[ace.resource] = set()

            permissions_by_resource[ace.resource].update(ace.permissions)

        return permissions_by_resource

    def get_resource_principals(
        self, resource: str, permission: Optional[AccessLevel] = None
    ) -> List[str]:
        """Get all principals with access to a resource.

        Args:
            resource: Resource to check
            permission: Optional permission filter

        Returns:
            List of principals
        """
        principals = set()
        current_time = datetime.now(pytz.UTC)

        for ace in self._access_entries.values():
            if not ace.is_active or ace.resource != resource:
                continue

            if ace.expires_at and ace.expires_at < current_time:
                continue

            if permission and permission not in ace.permissions:
                continue

            principals.add(ace.principal)

        return list(principals)

    def get_access_attempts(
        self,
        principal: Optional[str] = None,
        resource: Optional[str] = None,
        granted: Optional[bool] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[AccessAttempt]:
        """Get access attempt history.

        Args:
            principal: Filter by principal
            resource: Filter by resource
            granted: Filter by granted status
            start_time: Filter by start time
            end_time: Filter by end time

        Returns:
            List of access attempts
        """
        attempts = self._access_attempts

        if principal:
            attempts = [a for a in attempts if a.principal == principal]

        if resource:
            attempts = [a for a in attempts if a.resource == resource]

        if granted is not None:
            attempts = [a for a in attempts if a.granted == granted]

        if start_time:
            if start_time.tzinfo is None:
                start_time = pytz.UTC.localize(start_time)
            attempts = [a for a in attempts if a.timestamp >= start_time]

        if end_time:
            if end_time.tzinfo is None:
                end_time = pytz.UTC.localize(end_time)
            attempts = [a for a in attempts if a.timestamp <= end_time]

        return attempts

    def perform_access_review(
        self, reviewer: str, include_expired: bool = False
    ) -> Dict[str, Any]:
        """Perform an access review.

        Args:
            reviewer: User performing the review
            include_expired: Whether to include expired entries

        Returns:
            Access review report
        """
        current_time = datetime.now(pytz.UTC)

        active_entries = []
        expired_entries = []

        for ace in self._access_entries.values():
            if not ace.is_active:
                continue

            if ace.expires_at and ace.expires_at < current_time:
                expired_entries.append(ace)
            else:
                active_entries.append(ace)

        # Group by principal
        access_by_principal = {}
        for ace in active_entries:
            if ace.principal not in access_by_principal:
                access_by_principal[ace.principal] = []
            access_by_principal[ace.principal].append(
                {
                    "resource": ace.resource,
                    "permissions": [p.value for p in ace.permissions],
                    "granted_by": ace.granted_by,
                    "granted_at": ace.granted_at.isoformat(),
                    "expires_at": ace.expires_at.isoformat()
                    if ace.expires_at
                    else None,
                }
            )

        # Recent access attempts summary
        recent_attempts = self.get_access_attempts(
            start_time=current_time - timedelta(days=7)
        )

        denied_attempts = [a for a in recent_attempts if not a.granted]

        report = {
            "review_timestamp": current_time.isoformat(),
            "reviewer": reviewer,
            "summary": {
                "total_active_entries": len(active_entries),
                "total_expired_entries": len(expired_entries),
                "unique_principals": len(access_by_principal),
                "recent_access_attempts": len(recent_attempts),
                "recent_denied_attempts": len(denied_attempts),
            },
            "access_by_principal": access_by_principal,
        }

        if include_expired:
            report["expired_entries"] = [
                {
                    "principal": ace.principal,
                    "resource": ace.resource,
                    "expired_at": ace.expires_at.isoformat(),
                }
                for ace in expired_entries
            ]

        # Log the review
        if self.audit_logger:
            self.audit_logger.log_event(
                actor=reviewer,
                operation=OperationType.AUDIT,
                resource="access_control",
                details={
                    "action": "access_review",
                    "entries_reviewed": len(active_entries) + len(expired_entries),
                },
            )

        return report
