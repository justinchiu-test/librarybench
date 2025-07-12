"""Tests for parameter injection system."""

import pytest
from datetime import datetime, date, timedelta
from unittest.mock import Mock, patch

from src.parameter_injector import (
    ParameterInjector,
    ParameterType,
    ParameterDefinition,
    DateRange,
    ParameterValidator,
)


class TestParameterDefinition:
    """Test parameter definition configuration."""

    def test_valid_definition(self):
        """Test creating valid parameter definition."""
        param = ParameterDefinition(
            name="report_date",
            type=ParameterType.DATE,
            description="Report generation date",
            required=True,
            format="%Y-%m-%d",
        )
        assert param.name == "report_date"
        assert param.type == ParameterType.DATE
        assert param.required == True

    def test_invalid_name(self):
        """Test parameter name validation."""
        with pytest.raises(ValueError):
            ParameterDefinition(
                name="123invalid",  # Can't start with number
                type=ParameterType.STRING,
            )

        with pytest.raises(ValueError):
            ParameterDefinition(
                name="invalid-name",  # Can't have hyphen
                type=ParameterType.STRING,
            )

    def test_choices_with_date_range(self):
        """Test that choices are not allowed for date_range type."""
        with pytest.raises(ValueError):
            ParameterDefinition(
                name="date_range",
                type=ParameterType.DATE_RANGE,
                choices=["option1", "option2"],
            )

    def test_default_values(self):
        """Test default parameter values."""
        param = ParameterDefinition(
            name="status", type=ParameterType.STRING, default="active"
        )
        assert param.default == "active"
        assert param.required == True  # Default


class TestDateRange:
    """Test date range functionality."""

    def test_valid_date_range(self):
        """Test creating valid date range."""
        start = date(2024, 1, 1)
        end = date(2024, 1, 31)
        date_range = DateRange(start=start, end=end)

        assert date_range.start == start
        assert date_range.end == end

    def test_invalid_date_range(self):
        """Test that end date must be after start date."""
        with pytest.raises(ValueError):
            DateRange(start=date(2024, 1, 31), end=date(2024, 1, 1))

    def test_to_sql_conditions(self):
        """Test SQL condition generation."""
        date_range = DateRange(start=date(2024, 1, 1), end=date(2024, 1, 31))

        sql = date_range.to_sql_conditions("order_date")
        assert sql == "order_date >= '2024-01-01' AND order_date <= '2024-01-31'"


class TestParameterValidator:
    """Test parameter validation functionality."""

    @pytest.fixture
    def validator(self):
        """Create a test validator."""
        return ParameterValidator()

    def test_validate_required_parameter(self, validator):
        """Test validation of required parameters."""
        definition = ParameterDefinition(
            name="user_id", type=ParameterType.INTEGER, required=True
        )

        # Missing required parameter
        with pytest.raises(ValueError, match="required"):
            validator.validate(None, definition)

        # Valid required parameter
        result = validator.validate(123, definition)
        assert result == 123

    def test_validate_with_default(self, validator):
        """Test validation with default values."""
        definition = ParameterDefinition(
            name="limit", type=ParameterType.INTEGER, required=False, default=100
        )

        # Use default when None
        result = validator.validate(None, definition)
        assert result == 100

    def test_type_conversion_string(self, validator):
        """Test string type conversion."""
        definition = ParameterDefinition(name="name", type=ParameterType.STRING)

        assert validator.validate(123, definition) == "123"
        assert validator.validate("test", definition) == "test"

    def test_type_conversion_numeric(self, validator):
        """Test numeric type conversion."""
        # Integer
        int_def = ParameterDefinition(name="count", type=ParameterType.INTEGER)
        assert validator.validate("123", int_def) == 123
        assert validator.validate(123.7, int_def) == 123

        # Float
        float_def = ParameterDefinition(name="price", type=ParameterType.FLOAT)
        assert validator.validate("123.45", float_def) == 123.45
        assert validator.validate(100, float_def) == 100.0

    def test_type_conversion_boolean(self, validator):
        """Test boolean type conversion."""
        definition = ParameterDefinition(name="active", type=ParameterType.BOOLEAN)

        # String conversions
        assert validator.validate("true", definition) == True
        assert validator.validate("false", definition) == False
        assert validator.validate("yes", definition) == True
        assert validator.validate("no", definition) == False
        assert validator.validate("1", definition) == True
        assert validator.validate("0", definition) == False

        # Direct boolean
        assert validator.validate(True, definition) == True
        assert validator.validate(False, definition) == False

    def test_type_conversion_date(self, validator):
        """Test date type conversion."""
        definition = ParameterDefinition(
            name="report_date", type=ParameterType.DATE, format="%Y-%m-%d"
        )

        # From string
        result = validator.validate("2024-01-15", definition)
        assert result == date(2024, 1, 15)

        # From datetime
        dt = datetime(2024, 1, 15, 10, 30)
        result = validator.validate(dt, definition)
        assert result == date(2024, 1, 15)

        # Direct date
        d = date(2024, 1, 15)
        result = validator.validate(d, definition)
        assert result == d

    def test_type_conversion_list(self, validator):
        """Test list type conversion."""
        definition = ParameterDefinition(name="tags", type=ParameterType.LIST)

        # From comma-separated string
        result = validator.validate("tag1, tag2, tag3", definition)
        assert result == ["tag1", "tag2", "tag3"]

        # Direct list
        result = validator.validate(["a", "b", "c"], definition)
        assert result == ["a", "b", "c"]

        # Single value to list
        result = validator.validate("single", definition)
        assert result == ["single"]

    def test_type_conversion_date_range(self, validator):
        """Test date range type conversion."""
        definition = ParameterDefinition(name="period", type=ParameterType.DATE_RANGE)

        # From dict
        result = validator.validate(
            {"start": "2024-01-01", "end": "2024-01-31"}, definition
        )
        assert isinstance(result, DateRange)
        assert result.start == date(2024, 1, 1)
        assert result.end == date(2024, 1, 31)

        # From comma-separated string
        result = validator.validate("2024-01-01, 2024-01-31", definition)
        assert isinstance(result, DateRange)
        assert result.start == date(2024, 1, 1)

        # Direct DateRange
        dr = DateRange(start=date(2024, 1, 1), end=date(2024, 1, 31))
        result = validator.validate(dr, definition)
        assert result == dr

    def test_validate_choices(self, validator):
        """Test choice validation."""
        definition = ParameterDefinition(
            name="status",
            type=ParameterType.STRING,
            choices=["active", "inactive", "pending"],
        )

        # Valid choice
        result = validator.validate("active", definition)
        assert result == "active"

        # Invalid choice
        with pytest.raises(ValueError, match="must be one of"):
            validator.validate("invalid", definition)

    def test_custom_validators(self, validator):
        """Test custom validation rules."""
        definition = ParameterDefinition(
            name="age",
            type=ParameterType.INTEGER,
            validators=[{"type": "min", "value": 0}, {"type": "max", "value": 150}],
        )

        # Valid value
        result = validator.validate(25, definition)
        assert result == 25

        # Too small
        with pytest.raises(ValueError, match=">= 0"):
            validator.validate(-5, definition)

        # Too large
        with pytest.raises(ValueError, match="<= 150"):
            validator.validate(200, definition)

    def test_string_validators(self, validator):
        """Test string validation rules."""
        definition = ParameterDefinition(
            name="username",
            type=ParameterType.STRING,
            validators=[
                {"type": "min_length", "value": 3},
                {"type": "max_length", "value": 20},
                {"type": "regex", "value": "^[a-zA-Z0-9_]+$"},
            ],
        )

        # Valid
        result = validator.validate("test_user", definition)
        assert result == "test_user"

        # Too short
        with pytest.raises(ValueError, match="Length must be >= 3"):
            validator.validate("ab", definition)

        # Invalid characters
        with pytest.raises(ValueError, match="must match pattern"):
            validator.validate("test-user", definition)


class TestParameterInjector:
    """Test parameter injection functionality."""

    @pytest.fixture
    def injector(self):
        """Create a test parameter injector."""
        return ParameterInjector()

    def test_register_parameter(self, injector):
        """Test parameter registration."""
        param = ParameterDefinition(name="user_id", type=ParameterType.INTEGER)

        injector.register_parameter(param)

        assert "user_id" in injector._definitions
        assert injector._definitions["user_id"] == param

    def test_inject_parameters_basic(self, injector):
        """Test basic parameter injection."""
        template = (
            "SELECT * FROM users WHERE id = {{user_id}} AND status = '{{status}}'"
        )
        parameters = {"user_id": 123, "status": "active"}

        result = injector.inject_parameters(template, parameters, validate=False)

        expected = "SELECT * FROM users WHERE id = 123 AND status = 'active'"
        assert result == expected

    def test_inject_parameters_with_validation(self, injector):
        """Test parameter injection with validation."""
        # Register parameters
        injector.register_parameter(
            ParameterDefinition(name="user_id", type=ParameterType.INTEGER)
        )
        injector.register_parameter(
            ParameterDefinition(
                name="status", type=ParameterType.STRING, choices=["active", "inactive"]
            )
        )

        template = "WHERE id = {{user_id}} AND status = '{{status}}'"
        parameters = {
            "user_id": "123",  # Will be converted to int
            "status": "active",
        }

        result = injector.inject_parameters(template, parameters, validate=True)

        assert "WHERE id = 123" in result
        assert "status = 'active'" in result

    def test_special_parameters(self, injector):
        """Test special parameter injection."""
        # Test that special parameters work
        template = "SELECT * FROM orders WHERE date = '{{today}}'"

        result = injector.inject_parameters(template, {}, validate=False)

        # Check that today was replaced with a date
        assert "{{today}}" not in result
        assert "WHERE date = '" in result
        # The actual date will vary, so just check format
        import re

        assert re.search(r"WHERE date = '\d{4}-\d{2}-\d{2}'", result)

    def test_inject_sql_parameters_basic(self, injector):
        """Test SQL parameter injection."""
        query = "SELECT * FROM users WHERE id = :user_id AND active = :is_active"
        parameters = {"user_id": 123, "is_active": True}

        processed_query, sql_params = injector.inject_sql_parameters(
            query, parameters, validate=False
        )

        assert sql_params == parameters

    def test_inject_sql_parameters_with_date_range(self, injector):
        """Test SQL injection with date range."""
        query = "SELECT * FROM orders WHERE :order_date = :date_range"
        parameters = {
            "date_range": DateRange(start=date(2024, 1, 1), end=date(2024, 1, 31))
        }

        processed_query, sql_params = injector.inject_sql_parameters(
            query, parameters, validate=False
        )

        # Date range should be expanded in query
        assert (
            "order_date >= '2024-01-01' AND order_date <= '2024-01-31'"
            in processed_query
        )
        assert "date_range" not in sql_params

    def test_inject_list_parameter(self, injector):
        """Test list parameter injection."""
        template = "SELECT * FROM users WHERE status IN :statuses"
        parameters = {"statuses": ["active", "pending", "verified"]}

        result = injector.inject_parameters(template, parameters, validate=False)

        assert (
            result
            == "SELECT * FROM users WHERE status IN ('active','pending','verified')"
        )

    def test_create_parameter_set(self, injector):
        """Test parameter set creation for batch processing."""
        base_params = {"report_type": "sales", "format": "pdf"}

        variations = [{"month": "2024-01"}, {"month": "2024-02"}, {"month": "2024-03"}]

        result = injector.create_parameter_set(base_params, variations)

        assert len(result) == 3
        assert all(p["report_type"] == "sales" for p in result)
        assert result[0]["month"] == "2024-01"
        assert result[1]["month"] == "2024-02"

    def test_get_parameter_documentation(self, injector):
        """Test parameter documentation generation."""
        # Register some parameters
        injector.register_parameter(
            ParameterDefinition(
                name="user_id",
                type=ParameterType.INTEGER,
                description="User identifier",
                required=True,
            )
        )
        injector.register_parameter(
            ParameterDefinition(
                name="status",
                type=ParameterType.STRING,
                choices=["active", "inactive"],
                default="active",
            )
        )

        docs = injector.get_parameter_documentation()

        # Should include registered params and special params
        assert len(docs) > 2  # At least our 2 + special params

        # Check registered param
        user_doc = next(d for d in docs if d["name"] == "user_id")
        assert user_doc["type"] == "integer"
        assert user_doc["description"] == "User identifier"
        assert user_doc["required"] == True

        # Check special param
        today_doc = next(d for d in docs if d["name"] == "today")
        assert today_doc["type"] == "special"

    def test_get_last_month_range(self, injector):
        """Test last month range calculation."""
        # We can't easily mock date.today() inside the method,
        # so just verify the method returns a valid DateRange
        date_range = injector._get_last_month_range()

        assert isinstance(date_range, DateRange)
        assert date_range.start < date_range.end
        # Last month should have start day 1
        assert date_range.start.day == 1

    def test_get_current_month_range(self, injector):
        """Test current month range calculation."""
        # We can't easily mock date.today() inside the method,
        # so just verify the method returns a valid DateRange
        date_range = injector._get_current_month_range()

        assert isinstance(date_range, DateRange)
        assert date_range.start <= date_range.end
        # Current month should have start day 1
        assert date_range.start.day == 1
        # Should be in the same month
        assert date_range.start.month == date_range.end.month
