"""Tests for suppression management."""

import pytest
import tempfile
import json
from datetime import datetime, timedelta
from pathlib import Path

from pypatternguard.suppression import SuppressionManager
from pypatternguard.models import (
    Vulnerability,
    VulnerabilityType,
    SeverityLevel,
    Location,
    SuppressionRule,
)


class TestSuppressionManager:
    """Test suppression management functionality."""
    
    @pytest.fixture
    def temp_suppression_file(self):
        """Create a temporary suppression file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            suppression_data = {
                "rules": [
                    {
                        "id": "suppress-001",
                        "pattern": "TEST-.*",
                        "reason": "Test pattern false positive",
                        "created_at": datetime.now().isoformat(),
                        "created_by": "test_user",
                        "active": True
                    },
                    {
                        "id": "suppress-002",
                        "pattern": ".*/test_file.py:10",
                        "reason": "Known false positive at specific location",
                        "created_at": datetime.now().isoformat(),
                        "created_by": "test_user",
                        "active": True
                    }
                ],
                "audit_log": []
            }
            json.dump(suppression_data, f)
            temp_path = Path(f.name)
        
        yield temp_path
        temp_path.unlink()
    
    @pytest.fixture
    def sample_vulnerability(self):
        """Create a sample vulnerability for testing."""
        return Vulnerability(
            id="VULN-001",
            type=VulnerabilityType.HARDCODED_SECRET,
            severity=SeverityLevel.HIGH,
            title="Hardcoded Password",
            description="Test vulnerability",
            location=Location(
                file_path=Path("/project/auth.py"),
                line_start=25,
                line_end=25
            ),
            remediation="Remove hardcoded password",
            confidence=0.9
        )
    
    def test_load_rules_from_file(self, temp_suppression_file):
        """Test loading suppression rules from file."""
        manager = SuppressionManager(temp_suppression_file)
        
        assert len(manager.rules) == 2
        assert manager.rules[0].id == "suppress-001"
        assert manager.rules[0].pattern == "TEST-.*"
        assert manager.rules[0].active
    
    def test_add_rule(self):
        """Test adding a new suppression rule."""
        manager = SuppressionManager()
        
        rule = SuppressionRule(
            id="new-rule",
            pattern="SQL-.*",
            reason="SQL injection false positives in test files",
            created_at=datetime.now(),
            created_by="security_team"
        )
        
        manager.add_rule(rule)
        
        assert len(manager.rules) == 1
        assert manager.rules[0].id == "new-rule"
        assert len(manager.audit_log) == 1
        assert manager.audit_log[0]["action"] == "add_rule"
    
    def test_should_suppress_by_id_pattern(self, sample_vulnerability):
        """Test suppression by vulnerability ID pattern."""
        manager = SuppressionManager()
        
        rule = SuppressionRule(
            id="suppress-vuln",
            pattern="VULN-.*",
            reason="Suppress all VULN- prefixed vulnerabilities",
            created_at=datetime.now(),
            created_by="test"
        )
        manager.add_rule(rule)
        
        assert manager.should_suppress(sample_vulnerability)
        assert len(manager.audit_log) == 2  # add_rule + suppress_vulnerability
    
    def test_should_suppress_by_file_pattern(self, sample_vulnerability):
        """Test suppression by file path pattern."""
        manager = SuppressionManager()
        
        rule = SuppressionRule(
            id="suppress-auth",
            pattern="auth.py",
            reason="Suppress all auth.py vulnerabilities",
            created_at=datetime.now(),
            created_by="test"
        )
        manager.add_rule(rule)
        
        assert manager.should_suppress(sample_vulnerability)
    
    def test_should_suppress_by_type(self, sample_vulnerability):
        """Test suppression by vulnerability type."""
        manager = SuppressionManager()
        
        rule = SuppressionRule(
            id="suppress-secrets",
            pattern="hardcoded_secret",
            reason="Suppress hardcoded secrets",
            created_at=datetime.now(),
            created_by="test"
        )
        manager.add_rule(rule)
        
        assert manager.should_suppress(sample_vulnerability)
    
    def test_should_suppress_by_location(self, sample_vulnerability):
        """Test suppression by specific location."""
        manager = SuppressionManager()
        
        rule = SuppressionRule(
            id="suppress-location",
            pattern="/project/auth.py:25",
            reason="Known false positive at this location",
            created_at=datetime.now(),
            created_by="test"
        )
        manager.add_rule(rule)
        
        assert manager.should_suppress(sample_vulnerability)
    
    def test_expired_rule_not_applied(self, sample_vulnerability):
        """Test that expired rules are not applied."""
        manager = SuppressionManager()
        
        yesterday = datetime.now() - timedelta(days=1)
        rule = SuppressionRule(
            id="expired-rule",
            pattern="VULN-.*",
            reason="Temporary suppression",
            created_at=datetime.now() - timedelta(days=2),
            expires_at=yesterday,
            created_by="test"
        )
        manager.add_rule(rule)
        
        assert not manager.should_suppress(sample_vulnerability)
        assert not rule.active  # Should be deactivated
    
    def test_inactive_rule_not_applied(self, sample_vulnerability):
        """Test that inactive rules are not applied."""
        manager = SuppressionManager()
        
        rule = SuppressionRule(
            id="inactive-rule",
            pattern="VULN-.*",
            reason="Disabled suppression",
            created_at=datetime.now(),
            created_by="test",
            active=False
        )
        manager.add_rule(rule)
        
        assert not manager.should_suppress(sample_vulnerability)
    
    def test_get_suppression_reason(self, sample_vulnerability):
        """Test getting suppression reason."""
        manager = SuppressionManager()
        
        rule = SuppressionRule(
            id="suppress-with-reason",
            pattern="VULN-.*",
            reason="This is a test suppression reason",
            created_at=datetime.now(),
            created_by="test"
        )
        manager.add_rule(rule)
        
        assert manager.should_suppress(sample_vulnerability)
        reason = manager.get_suppression_reason(sample_vulnerability)
        assert reason == "This is a test suppression reason"
    
    def test_create_rule_from_vulnerability(self, sample_vulnerability):
        """Test creating a rule from a vulnerability."""
        manager = SuppressionManager()
        
        rule = manager.create_rule_from_vulnerability(
            sample_vulnerability,
            reason="False positive in test code",
            created_by="developer",
            expires_days=30
        )
        
        assert rule.id == "suppress-VULN-001"
        assert rule.pattern == "/project/auth.py:25"
        assert rule.reason == "False positive in test code"
        assert rule.created_by == "developer"
        assert rule.expires_at is not None
        assert rule.expires_at > datetime.now()
    
    def test_get_active_rules(self):
        """Test getting only active rules."""
        manager = SuppressionManager()
        
        # Add mix of active and inactive rules
        active_rule = SuppressionRule(
            id="active",
            pattern=".*",
            reason="Active",
            created_at=datetime.now(),
            created_by="test",
            active=True
        )
        
        inactive_rule = SuppressionRule(
            id="inactive",
            pattern=".*",
            reason="Inactive",
            created_at=datetime.now(),
            created_by="test",
            active=False
        )
        
        manager.add_rule(active_rule)
        manager.add_rule(inactive_rule)
        
        active_rules = manager.get_active_rules()
        assert len(active_rules) == 1
        assert active_rules[0].id == "active"
    
    def test_audit_trail(self):
        """Test audit trail functionality."""
        manager = SuppressionManager()
        
        # Add some actions
        rule = SuppressionRule(
            id="test-rule",
            pattern=".*",
            reason="Test",
            created_at=datetime.now(),
            created_by="test"
        )
        manager.add_rule(rule)
        
        vuln = Vulnerability(
            id="TEST-001",
            type=VulnerabilityType.INJECTION,
            severity=SeverityLevel.HIGH,
            title="Test",
            description="Test",
            location=Location(file_path=Path("/test.py"), line_start=1, line_end=1),
            remediation="Test",
            confidence=0.9
        )
        manager.should_suppress(vuln)
        
        # Check audit trail
        trail = manager.get_audit_trail()
        assert len(trail) >= 2
        assert any(entry["action"] == "add_rule" for entry in trail)
        assert any(entry["action"] == "suppress_vulnerability" for entry in trail)
    
    def test_audit_trail_date_filtering(self):
        """Test audit trail date filtering."""
        manager = SuppressionManager()
        
        # Add rule
        rule = SuppressionRule(
            id="test-rule",
            pattern=".*",
            reason="Test",
            created_at=datetime.now(),
            created_by="test"
        )
        manager.add_rule(rule)
        
        # Test filtering
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)
        
        # Should include today's entries
        trail = manager.get_audit_trail(start_date=yesterday, end_date=tomorrow)
        assert len(trail) >= 1
        
        # Should exclude today's entries
        trail = manager.get_audit_trail(end_date=yesterday)
        assert len(trail) == 0
    
    def test_save_rules(self):
        """Test saving rules to file."""
        manager = SuppressionManager()
        
        # Add rules
        rule1 = SuppressionRule(
            id="rule1",
            pattern="pattern1",
            reason="reason1",
            created_at=datetime.now(),
            created_by="user1"
        )
        rule2 = SuppressionRule(
            id="rule2",
            pattern="pattern2",
            reason="reason2",
            created_at=datetime.now(),
            created_by="user2"
        )
        
        manager.add_rule(rule1)
        manager.add_rule(rule2)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            manager.save_rules(temp_path)
            
            # Load and verify
            with open(temp_path, 'r') as f:
                data = json.load(f)
            
            assert len(data["rules"]) == 2
            assert data["rules"][0]["id"] == "rule1"
            assert data["rules"][1]["id"] == "rule2"
            assert len(data["audit_log"]) >= 2
        finally:
            temp_path.unlink()