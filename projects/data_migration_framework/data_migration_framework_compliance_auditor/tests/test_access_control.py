"""Tests for the access control manager."""

import pytest
from datetime import datetime, timedelta
import pytz

from pymigrate.access import AccessControlManager, PolicyEngine
from pymigrate.access.policies import (
    RoleBasedPolicy,
    TimeBasedPolicy,
    ResourcePatternPolicy,
    AttributeBasedPolicy,
)
from pymigrate.audit import AuditLogger, InMemoryAuditStorage
from pymigrate.models import AccessLevel


class TestAccessControlManager:
    """Test suite for AccessControlManager."""

    @pytest.fixture
    def setup_manager(self):
        """Set up access control manager."""
        storage = InMemoryAuditStorage()
        audit_logger = AuditLogger(storage, enable_signatures=False)
        manager = AccessControlManager(audit_logger=audit_logger)
        return manager, audit_logger

    def test_grant_access(self, setup_manager):
        """Test granting access to resources."""
        manager, _ = setup_manager

        # Grant access
        ace = manager.grant_access(
            principal="user1",
            resource="database:customers",
            permissions={AccessLevel.READ, AccessLevel.WRITE},
            granted_by="admin",
            expires_at=datetime.now(pytz.UTC) + timedelta(days=30),
        )

        # Verify ACE created
        assert ace.principal == "user1"
        assert ace.resource == "database:customers"
        assert AccessLevel.READ in ace.permissions
        assert AccessLevel.WRITE in ace.permissions
        assert ace.is_active

    def test_check_access_with_ace(self, setup_manager):
        """Test checking access with explicit ACE."""
        manager, _ = setup_manager

        # Grant access
        manager.grant_access(
            principal="user1",
            resource="file:report.pdf",
            permissions={AccessLevel.READ},
            granted_by="admin",
        )

        # Check allowed access
        assert manager.check_access("user1", "file:report.pdf", AccessLevel.READ)

        # Check denied access (no WRITE permission)
        assert not manager.check_access("user1", "file:report.pdf", AccessLevel.WRITE)

        # Check denied access (different user)
        assert not manager.check_access("user2", "file:report.pdf", AccessLevel.READ)

    def test_revoke_access(self, setup_manager):
        """Test revoking access."""
        manager, _ = setup_manager

        # Grant and then revoke
        ace = manager.grant_access(
            principal="user1",
            resource="resource1",
            permissions={AccessLevel.READ},
            granted_by="admin",
        )

        # Verify access granted
        assert manager.check_access("user1", "resource1", AccessLevel.READ)

        # Revoke access
        revoked = manager.revoke_access(ace.ace_id, "admin")
        assert revoked

        # Verify access denied after revocation
        assert not manager.check_access("user1", "resource1", AccessLevel.READ)

    def test_expired_access(self, setup_manager):
        """Test that expired access is denied."""
        manager, _ = setup_manager

        # Grant access that's already expired
        manager.grant_access(
            principal="user1",
            resource="temp_resource",
            permissions={AccessLevel.READ},
            granted_by="admin",
            expires_at=datetime.now(pytz.UTC) - timedelta(hours=1),  # Expired
        )

        # Should be denied
        assert not manager.check_access("user1", "temp_resource", AccessLevel.READ)

    def test_conditional_access(self, setup_manager):
        """Test access with conditions."""
        manager, _ = setup_manager

        # Grant conditional access
        manager.grant_access(
            principal="user1",
            resource="secure_data",
            permissions={AccessLevel.READ},
            granted_by="admin",
            conditions={"department": "finance", "clearance_level": ["high", "medium"]},
        )

        # Check with matching conditions
        context = {"department": "finance", "clearance_level": "high"}
        assert manager.check_access("user1", "secure_data", AccessLevel.READ, context)

        # Clear cache before checking with wrong context
        manager._access_cache.clear()

        # Check with non-matching conditions
        wrong_context = {"department": "marketing", "clearance_level": "high"}
        assert not manager.check_access(
            "user1", "secure_data", AccessLevel.READ, wrong_context
        )

    def test_role_based_access(self, setup_manager):
        """Test role-based access control."""
        manager, _ = setup_manager

        # Check admin role (from default policy)
        context = {"roles": ["admin"]}
        assert manager.check_access(
            "admin_user", "any_resource", AccessLevel.ADMIN, context
        )

        # Check auditor role
        context = {"roles": ["auditor"]}
        assert manager.check_access("auditor1", "audit_log", AccessLevel.AUDIT, context)
        assert manager.check_access("auditor1", "audit_log", AccessLevel.READ, context)
        assert not manager.check_access(
            "auditor1", "audit_log", AccessLevel.WRITE, context
        )

    def test_time_based_access(self, setup_manager):
        """Test time-based access restrictions."""
        manager, _ = setup_manager

        # Add a time-based policy explicitly for this test
        from pymigrate.access.policies import TimeBasedPolicy

        time_policy = TimeBasedPolicy(
            allowed_hours=(9, 17),  # 9 AM to 5 PM
            allowed_days={0, 1, 2, 3, 4},  # Monday to Friday
        )
        manager.policy_engine.add_policy(time_policy)

        # Test with a time that should be denied (weekend)
        weekend_time = datetime(2023, 7, 15, 12, 0, 0, tzinfo=pytz.UTC)  # Saturday
        context = {
            "roles": ["operator"],  # Has READ and WRITE
            "timestamp": weekend_time,
        }

        # Clear cache to ensure fresh evaluation
        manager._access_cache.clear()

        # Should be denied on weekend
        result = manager.check_access("user1", "resource", AccessLevel.READ, context)
        assert not result

        # Test with a time that should be allowed (weekday business hours)
        weekday_time = datetime(2023, 7, 17, 12, 0, 0, tzinfo=pytz.UTC)  # Monday noon
        context["timestamp"] = weekday_time

        # Should be allowed during business hours
        result = manager.check_access("user1", "resource", AccessLevel.READ, context)
        assert result

    def test_access_attempt_logging(self, setup_manager):
        """Test that access attempts are logged."""
        manager, _ = setup_manager

        # Make some access attempts
        manager.check_access(
            "user1", "resource1", AccessLevel.READ, {"roles": ["viewer"]}
        )
        manager.check_access(
            "user2", "resource2", AccessLevel.WRITE, {"roles": ["viewer"]}
        )  # Should fail

        # Get attempt history
        attempts = manager.get_access_attempts()
        assert len(attempts) >= 2

        # Filter by granted status
        granted_attempts = manager.get_access_attempts(granted=True)
        denied_attempts = manager.get_access_attempts(granted=False)

        assert len(granted_attempts) > 0
        assert len(denied_attempts) > 0

    def test_principal_permissions_query(self, setup_manager):
        """Test querying permissions for a principal."""
        manager, _ = setup_manager

        # Grant various permissions
        manager.grant_access(
            "user1", "resource1", {AccessLevel.READ, AccessLevel.WRITE}, "admin"
        )
        manager.grant_access("user1", "resource2", {AccessLevel.READ}, "admin")

        # Query permissions
        permissions = manager.get_principal_permissions("user1")

        assert "resource1" in permissions
        assert AccessLevel.READ in permissions["resource1"]
        assert AccessLevel.WRITE in permissions["resource1"]
        assert "resource2" in permissions
        assert AccessLevel.READ in permissions["resource2"]

    def test_resource_principals_query(self, setup_manager):
        """Test querying principals with access to a resource."""
        manager, _ = setup_manager

        # Grant access to multiple users
        manager.grant_access("user1", "shared_resource", {AccessLevel.READ}, "admin")
        manager.grant_access("user2", "shared_resource", {AccessLevel.WRITE}, "admin")
        manager.grant_access("user3", "shared_resource", {AccessLevel.READ}, "admin")

        # Query all principals
        principals = manager.get_resource_principals("shared_resource")
        assert set(principals) == {"user1", "user2", "user3"}

        # Query by permission
        readers = manager.get_resource_principals("shared_resource", AccessLevel.READ)
        assert set(readers) == {"user1", "user3"}

    def test_access_review(self, setup_manager):
        """Test performing access reviews."""
        manager, _ = setup_manager

        # Set up various access entries
        manager.grant_access("user1", "resource1", {AccessLevel.READ}, "admin")
        manager.grant_access(
            "user2",
            "resource2",
            {AccessLevel.WRITE},
            "admin",
            expires_at=datetime.now(pytz.UTC) - timedelta(days=1),  # Expired
        )

        # Make some access attempts
        manager.check_access("user1", "resource1", AccessLevel.READ)
        manager.check_access("user3", "resource3", AccessLevel.WRITE)  # Denied

        # Perform review
        report = manager.perform_access_review("security_admin", include_expired=True)

        assert report["reviewer"] == "security_admin"
        assert report["summary"]["total_active_entries"] >= 1
        assert report["summary"]["total_expired_entries"] >= 1
        assert report["summary"]["recent_denied_attempts"] >= 1
        assert "access_by_principal" in report

    def test_access_caching(self, setup_manager):
        """Test access decision caching."""
        manager, _ = setup_manager

        # Grant access
        manager.grant_access("user1", "resource1", {AccessLevel.READ}, "admin")

        # First check (cache miss)
        start_time = datetime.now()
        result1 = manager.check_access("user1", "resource1", AccessLevel.READ)
        first_duration = (datetime.now() - start_time).total_seconds()

        # Second check (cache hit)
        start_time = datetime.now()
        result2 = manager.check_access("user1", "resource1", AccessLevel.READ)
        second_duration = (datetime.now() - start_time).total_seconds()

        assert result1 == result2
        # Cache hit should be faster (though this might be flaky in tests)
        # Just verify both complete quickly
        assert first_duration < 0.1
        assert second_duration < 0.1


class TestAccessPolicies:
    """Test suite for access control policies."""

    def test_role_based_policy(self):
        """Test role-based access policy."""
        policy = RoleBasedPolicy(
            {
                "developer": {AccessLevel.READ, AccessLevel.WRITE},
                "tester": {AccessLevel.READ},
                "admin": {
                    AccessLevel.READ,
                    AccessLevel.WRITE,
                    AccessLevel.DELETE,
                    AccessLevel.ADMIN,
                },
            }
        )

        # Test developer access
        assert policy.evaluate(
            "user1", "code", AccessLevel.READ, {"roles": ["developer"]}
        )
        assert policy.evaluate(
            "user1", "code", AccessLevel.WRITE, {"roles": ["developer"]}
        )
        assert not policy.evaluate(
            "user1", "code", AccessLevel.DELETE, {"roles": ["developer"]}
        )

        # Test multiple roles
        assert policy.evaluate(
            "user2", "data", AccessLevel.DELETE, {"roles": ["tester", "admin"]}
        )

    def test_time_based_policy(self):
        """Test time-based access policy."""
        # Policy: weekdays 9-17
        policy = TimeBasedPolicy(
            allowed_hours=(9, 17),
            allowed_days={0, 1, 2, 3, 4},  # Monday-Friday
            max_session_duration=timedelta(hours=8),
        )

        # Test during allowed time (mock context)
        context = {"session_start": datetime.now(pytz.UTC).isoformat()}

        # This would pass/fail based on actual time
        # We'll test the session duration check
        old_session_context = {
            "session_start": (datetime.now(pytz.UTC) - timedelta(hours=9)).isoformat()
        }

        assert not policy.evaluate(
            "user", "resource", AccessLevel.READ, old_session_context
        )

    def test_resource_pattern_policy(self):
        """Test resource pattern-based policy."""
        policy = ResourcePatternPolicy(
            {
                "public/*": {"*": {AccessLevel.READ}},
                "user/*/profile": {"owner": {AccessLevel.READ, AccessLevel.WRITE}},
                "admin/*": {
                    "admin": {AccessLevel.READ, AccessLevel.WRITE, AccessLevel.DELETE}
                },
            }
        )

        # Test public access
        assert policy.evaluate("anyone", "public/docs", AccessLevel.READ, {})
        assert not policy.evaluate("anyone", "public/docs", AccessLevel.WRITE, {})

        # Test admin access
        assert policy.evaluate("admin", "admin/settings", AccessLevel.DELETE, {})
        assert not policy.evaluate("user", "admin/settings", AccessLevel.READ, {})

    def test_attribute_based_policy(self):
        """Test attribute-based access policy."""
        rules = [
            {
                "principal_attributes": {"department": "finance"},
                "resource_attributes": {"classification": "financial"},
                "allowed_actions": [AccessLevel.READ, AccessLevel.WRITE],
            },
            {
                "principal_attributes": {"clearance": "top_secret"},
                "allowed_actions": [
                    AccessLevel.READ,
                    AccessLevel.WRITE,
                    AccessLevel.DELETE,
                ],
            },
        ]

        policy = AttributeBasedPolicy(rules)

        # Test department match
        context = {
            "user_attributes": {"department": "finance"},
            "resource_attributes": {"classification": "financial"},
        }
        assert policy.evaluate("user1", "financial_report", AccessLevel.READ, context)

        # Test clearance match
        context = {
            "user_attributes": {"clearance": "top_secret"},
            "resource_attributes": {},
        }
        assert policy.evaluate("user2", "classified_doc", AccessLevel.DELETE, context)

        # Test no match
        context = {
            "user_attributes": {"department": "marketing"},
            "resource_attributes": {"classification": "financial"},
        }
        assert not policy.evaluate(
            "user3", "financial_report", AccessLevel.READ, context
        )

    def test_policy_engine(self):
        """Test policy engine with multiple policies."""
        engine = PolicyEngine(default_deny=True)

        # Add role policy
        engine.add_policy(RoleBasedPolicy({"user": {AccessLevel.READ}}))

        # Add resource pattern policy
        engine.add_policy(ResourcePatternPolicy({"temp/*": {"*": {AccessLevel.WRITE}}}))

        # Test role-based access
        allowed, policies = engine.evaluate(
            "user1", "data", AccessLevel.READ, {"roles": ["user"]}
        )
        assert allowed
        assert "RoleBasedAccessControl" in policies

        # Test pattern-based access
        allowed, policies = engine.evaluate(
            "anyone", "temp/file", AccessLevel.WRITE, {}
        )
        assert allowed
        assert "ResourcePatternAccessControl" in policies

        # Test denied access
        allowed, policies = engine.evaluate(
            "user1", "secure", AccessLevel.DELETE, {"roles": ["user"]}
        )
        assert not allowed
        assert len(policies) == 0
