"""Tests for the compliance rule engine."""

from datetime import datetime, timedelta
import pytz

from pymigrate.compliance import ComplianceRuleEngine, RuleRegistry
from pymigrate.compliance.rules import (
    DataRetentionEvaluator,
    PersonalDataEvaluator,
    AccessControlEvaluator,
)
from pymigrate.models import ComplianceFramework, ComplianceRule


class TestComplianceRuleEngine:
    """Test suite for ComplianceRuleEngine."""

    def test_validate_data_operation(self):
        """Test validating a data operation against rules."""
        engine = ComplianceRuleEngine(enforcement_mode=True)

        # Test GDPR compliant operation
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "creation_date": datetime.now(pytz.UTC).isoformat(),
        }
        context = {
            "actor": "data_processor",
            "resource": "customer_data",
            "is_encrypted": True,
            "user_roles": ["data_processor"],
        }

        result = engine.validate_data_operation(
            operation_type="write",
            data=data,
            context=context,
            frameworks=[ComplianceFramework.GDPR],
        )

        # Should be compliant with proper encryption
        assert result["is_compliant"]
        assert result["allow_operation"]
        assert len(result["violations"]) == 0

    def test_gdpr_retention_violation(self):
        """Test detection of GDPR retention violations."""
        engine = ComplianceRuleEngine(enforcement_mode=True)

        # Create data older than retention limit
        old_date = datetime.now(pytz.UTC) - timedelta(days=800)  # > 730 days
        data = {"customer_id": "12345", "creation_date": old_date.isoformat()}

        result = engine.validate_data_operation(
            operation_type="read",
            data=data,
            context={"actor": "system"},
            frameworks=[ComplianceFramework.GDPR],
        )

        # Should violate retention rule
        assert not result["is_compliant"]
        assert not result["allow_operation"]  # enforcement_mode=True
        assert len(result["violations"]) > 0

        violation = result["violations"][0]
        assert "retention" in violation.details["violation_type"]

    def test_personal_data_protection(self):
        """Test personal data protection rules."""
        engine = ComplianceRuleEngine(enforcement_mode=False)  # Log only

        # Test unencrypted personal data
        data = {
            "name": "Jane Smith",
            "ssn": "123-45-6789",  # PII
            "email": "jane@example.com",
        }
        context = {
            "actor": "app_user",
            "is_encrypted": False,  # Not encrypted!
        }

        result = engine.validate_data_operation(
            operation_type="write",
            data=data,
            context=context,
            frameworks=[ComplianceFramework.GDPR],
        )

        # Should violate but allow (enforcement_mode=False)
        assert not result["is_compliant"]
        assert result["allow_operation"]

        # Check violation details
        violations = result["violations"]
        assert any(
            "personal_data" in v.details.get("violation_type", "") for v in violations
        )

    def test_sox_access_control(self):
        """Test SOX financial data access control."""
        engine = ComplianceRuleEngine()

        # Test unauthorized access
        data = {"financial_report": "Q4 earnings"}
        context = {
            "actor": "regular_user",
            "user_roles": ["employee"],  # Not finance or auditor
            "access_granted_at": datetime.now(pytz.UTC).isoformat(),
        }

        result = engine.validate_data_operation(
            operation_type="read",
            data=data,
            context=context,
            frameworks=[ComplianceFramework.SOX],
        )

        # Should violate access control
        assert not result["is_compliant"]
        violations = result["violations"]
        assert any("access_control" in v.details["violation_type"] for v in violations)

    def test_multiple_framework_validation(self):
        """Test validation against multiple frameworks."""
        engine = ComplianceRuleEngine()

        data = {
            "patient_id": "P123",
            "medical_record": "diagnosis",
            "creation_date": datetime.now(pytz.UTC).isoformat(),
        }
        context = {
            "actor": "healthcare_provider",
            "user_roles": ["medical_staff"],
            "is_encrypted": True,
        }

        # Validate against both GDPR and HIPAA
        result = engine.validate_data_operation(
            operation_type="write",
            data=data,
            context=context,
            frameworks=[ComplianceFramework.GDPR, ComplianceFramework.HIPAA],
        )

        # Check rules from both frameworks were evaluated
        assert result["rules_evaluated"] >= 2

    def test_migration_validation(self):
        """Test complete migration validation."""
        engine = ComplianceRuleEngine()

        source_data = {
            "customer_list": ["id1", "id2"],
            "creation_date": datetime.now(pytz.UTC).isoformat(),
        }
        destination_data = {
            "migrated_customers": ["id1", "id2"],
            "migration_date": datetime.now(pytz.UTC).isoformat(),
        }
        transformation_details = {"anonymization_applied": True, "records_processed": 2}

        result = engine.validate_migration(
            source_data=source_data,
            destination_data=destination_data,
            transformation_details=transformation_details,
            actor="migration_service",
        )

        # Check all stages validated
        assert "source_validation" in result
        assert "transform_validation" in result
        assert "destination_validation" in result
        assert isinstance(result["total_violations"], int)

    def test_violation_history(self):
        """Test violation history tracking."""
        engine = ComplianceRuleEngine()

        # Generate some violations
        old_data = {
            "data": "test",
            "creation_date": (
                datetime.now(pytz.UTC) - timedelta(days=1000)
            ).isoformat(),
        }

        engine.validate_data_operation(
            operation_type="read",
            data=old_data,
            context={"actor": "test_user", "resource": "old_data"},
            frameworks=[ComplianceFramework.GDPR],
        )

        # Query violation history
        violations = engine.get_violation_history(resource="old_data")

        assert len(violations) > 0
        assert violations[0].resource == "old_data"

    def test_remediation_tracking(self):
        """Test updating violation remediation status."""
        engine = ComplianceRuleEngine()

        # Create a violation
        result = engine.validate_data_operation(
            operation_type="write",
            data={"ssn": "123-45-6789"},
            context={"actor": "app", "is_encrypted": False},
            frameworks=[ComplianceFramework.GDPR],
        )

        violation = result["violations"][0]

        # Update remediation status
        updated = engine.update_violation_status(
            violation.violation_id,
            "REMEDIATED",
            {
                "action": "Data encrypted",
                "timestamp": datetime.now(pytz.UTC).isoformat(),
            },
        )

        assert updated

        # Verify status updated
        history = engine.get_violation_history()
        remediated = [v for v in history if v.violation_id == violation.violation_id][0]
        assert remediated.remediation_status == "REMEDIATED"

    def test_compliance_report_generation(self):
        """Test generating compliance reports."""
        engine = ComplianceRuleEngine()

        # Generate some test data and violations
        start_time = datetime.now(pytz.UTC) - timedelta(hours=1)

        # Create violations
        for i in range(5):
            data = {
                "test_data": f"data_{i}",
                "creation_date": (
                    datetime.now(pytz.UTC) - timedelta(days=1000)
                ).isoformat(),
            }
            engine.validate_data_operation(
                operation_type="read",
                data=data,
                context={"actor": f"user_{i}"},
                frameworks=[ComplianceFramework.GDPR],
            )

        end_time = datetime.now(pytz.UTC)

        # Generate report
        report = engine.generate_compliance_report(
            framework=ComplianceFramework.GDPR, start_time=start_time, end_time=end_time
        )

        # Verify report structure
        assert report["framework"] == ComplianceFramework.GDPR
        assert "summary" in report
        assert report["summary"]["total_violations"] >= 5
        assert "violations_by_rule" in report

    def test_custom_rule_addition(self):
        """Test adding custom compliance rules."""
        engine = ComplianceRuleEngine()

        # Define custom rule
        custom_rule = ComplianceRule(
            rule_id="custom-001",
            name="Custom Data Validation",
            framework=ComplianceFramework.SOX,
            description="Ensure financial data has audit trail",
            severity="HIGH",
            rule_logic={"required_field": "audit_trail"},
            version="1.0",
            effective_date=datetime.now(pytz.UTC),
        )

        # Define evaluator functions
        def evaluate_func(data, context):
            return "audit_trail" in data and data["audit_trail"] is not None

        def violation_func(data, context):
            return {
                "violation_type": "missing_audit_trail",
                "message": "Financial data must have audit trail",
            }

        # Add custom rule
        engine.add_custom_rule(custom_rule, evaluate_func, violation_func)

        # Test custom rule
        result = engine.validate_data_operation(
            operation_type="write",
            data={"amount": 1000},  # Missing audit_trail
            context={"actor": "finance_app"},
            frameworks=[ComplianceFramework.SOX],
        )

        # Should detect custom violation
        assert not result["is_compliant"]
        violations = result["violations"]
        assert any(
            "missing_audit_trail" in v.details.get("violation_type", "")
            for v in violations
        )


class TestComplianceRules:
    """Test suite for individual compliance rule evaluators."""

    def test_data_retention_evaluator(self):
        """Test data retention rule evaluation."""
        evaluator = DataRetentionEvaluator(max_retention_days=365)

        # Test within retention
        recent_data = {"creation_date": datetime.now(pytz.UTC).isoformat()}
        assert evaluator.evaluate(recent_data, {})

        # Test beyond retention
        old_data = {
            "creation_date": (datetime.now(pytz.UTC) - timedelta(days=400)).isoformat()
        }
        assert not evaluator.evaluate(old_data, {})

        # Test violation details
        details = evaluator.get_violation_details(old_data, {})
        assert details["violation_type"] == "data_retention_exceeded"
        assert details["max_retention_days"] == 365

    def test_personal_data_evaluator(self):
        """Test personal data protection evaluation."""
        evaluator = PersonalDataEvaluator(
            allowed_fields={"name", "user_id"}, encryption_required=True
        )

        # Test allowed fields with encryption
        data = {"name": "John", "user_id": "123"}
        context = {"is_encrypted": True}
        assert evaluator.evaluate(data, context)

        # Test PII in unauthorized field
        data_with_pii = {
            "name": "John",
            "personal_email": "john@example.com",  # Email in unauthorized field
        }
        assert not evaluator.evaluate(data_with_pii, context)

        # Test missing encryption
        safe_data = {"name": "John"}
        unencrypted_context = {"is_encrypted": False}
        assert not evaluator.evaluate(safe_data, unencrypted_context)

    def test_access_control_evaluator(self):
        """Test access control evaluation."""
        evaluator = AccessControlEvaluator(
            required_roles={"admin", "manager"}, max_access_duration_hours=8
        )

        # Test valid access
        context = {
            "user_roles": ["admin", "user"],
            "access_granted_at": datetime.now(pytz.UTC).isoformat(),
        }
        assert evaluator.evaluate({}, context)

        # Test missing role
        context_no_role = {
            "user_roles": ["user", "viewer"],
            "access_granted_at": datetime.now(pytz.UTC).isoformat(),
        }
        assert not evaluator.evaluate({}, context_no_role)

        # Test expired access
        context_expired = {
            "user_roles": ["admin"],
            "access_granted_at": (
                datetime.now(pytz.UTC) - timedelta(hours=10)
            ).isoformat(),
        }
        assert not evaluator.evaluate({}, context_expired)


class TestRuleRegistry:
    """Test suite for RuleRegistry."""

    def test_default_rules_initialization(self):
        """Test that default rules are properly initialized."""
        registry = RuleRegistry()

        # Check GDPR rules exist
        gdpr_rules = registry.get_rules_by_framework(ComplianceFramework.GDPR)
        assert len(gdpr_rules) >= 2
        assert any("retention" in r.rule_id for r in gdpr_rules)
        assert any("pii" in r.rule_id for r in gdpr_rules)

        # Check SOX rules exist
        sox_rules = registry.get_rules_by_framework(ComplianceFramework.SOX)
        assert len(sox_rules) >= 1
        assert any("access" in r.rule_id for r in sox_rules)

    def test_get_active_rules(self):
        """Test getting active rules by date."""
        registry = RuleRegistry()

        # Get current active rules
        active_rules = registry.get_active_rules()
        assert len(active_rules) > 0

        # Test with future date
        future_date = datetime.now(pytz.UTC) + timedelta(days=365)
        future_rules = registry.get_active_rules(future_date)
        assert len(future_rules) >= len(active_rules)

        # Test with past date (before GDPR)
        past_date = datetime(2017, 1, 1, tzinfo=pytz.UTC)
        past_rules = registry.get_active_rules(past_date)
        # Should have fewer rules (no GDPR)
        assert len(past_rules) < len(active_rules)
