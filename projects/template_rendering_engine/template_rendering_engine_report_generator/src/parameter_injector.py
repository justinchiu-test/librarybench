"""Parameter injection system for runtime report customization."""

from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, date, timedelta
from enum import Enum
import re
from pydantic import BaseModel, Field, field_validator, ValidationInfo


class ParameterType(str, Enum):
    """Types of parameters that can be injected."""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    LIST = "list"
    DICT = "dict"
    DATE_RANGE = "date_range"


class ParameterDefinition(BaseModel):
    """Definition of a parameter that can be injected."""

    name: str
    type: ParameterType
    description: Optional[str] = None
    default: Optional[Any] = None
    required: bool = Field(default=True)
    validators: Optional[List[Dict[str, Any]]] = None
    choices: Optional[List[Any]] = None
    format: Optional[str] = None  # For date/datetime formatting

    @field_validator("name")
    def validate_name(cls, v):
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", v):
            raise ValueError("Parameter name must be a valid identifier")
        return v

    @field_validator("choices")
    def validate_choices(cls, v, info: ValidationInfo):
        if v and info.data.get("type") == ParameterType.DATE_RANGE:
            raise ValueError("Choices not supported for date_range type")
        return v


class DateRange(BaseModel):
    """Represents a date range for filtering."""

    start: date
    end: date

    @field_validator("end")
    def validate_end(cls, v, info: ValidationInfo):
        if "start" in info.data and v < info.data["start"]:
            raise ValueError("End date must be after start date")
        return v

    def to_sql_conditions(self, column: str) -> str:
        """Convert to SQL WHERE conditions."""
        return f"{column} >= '{self.start}' AND {column} <= '{self.end}'"


class ParameterValidator:
    """Validates parameter values against their definitions."""

    def validate(self, value: Any, definition: ParameterDefinition) -> Any:
        """Validate and convert a parameter value."""
        # Check required
        if definition.required and value is None:
            raise ValueError(f"Parameter '{definition.name}' is required")

        # Use default if value is None
        if value is None:
            return definition.default

        # Type conversion and validation
        converted_value = self._convert_type(value, definition)

        # Check choices
        if definition.choices and converted_value not in definition.choices:
            raise ValueError(
                f"Parameter '{definition.name}' must be one of {definition.choices}"
            )

        # Run custom validators
        if definition.validators:
            for validator in definition.validators:
                converted_value = self._run_validator(converted_value, validator)

        return converted_value

    def _convert_type(self, value: Any, definition: ParameterDefinition) -> Any:
        """Convert value to the specified type."""
        param_type = definition.type

        try:
            if param_type == ParameterType.STRING:
                return str(value)
            elif param_type == ParameterType.INTEGER:
                return int(value)
            elif param_type == ParameterType.FLOAT:
                return float(value)
            elif param_type == ParameterType.BOOLEAN:
                if isinstance(value, str):
                    return value.lower() in ["true", "yes", "1", "on"]
                return bool(value)
            elif param_type == ParameterType.DATE:
                if isinstance(value, datetime):
                    return value.date()
                elif isinstance(value, date):
                    return value
                else:
                    return datetime.strptime(
                        str(value), definition.format or "%Y-%m-%d"
                    ).date()
            elif param_type == ParameterType.DATETIME:
                if isinstance(value, datetime):
                    return value
                else:
                    return datetime.strptime(
                        str(value), definition.format or "%Y-%m-%d %H:%M:%S"
                    )
            elif param_type == ParameterType.LIST:
                if isinstance(value, list):
                    return value
                elif isinstance(value, str):
                    return [v.strip() for v in value.split(",")]
                else:
                    return [value]
            elif param_type == ParameterType.DICT:
                if isinstance(value, dict):
                    return value
                else:
                    raise ValueError("Dict parameters must be provided as dictionaries")
            elif param_type == ParameterType.DATE_RANGE:
                if isinstance(value, DateRange):
                    return value
                elif isinstance(value, dict):
                    return DateRange(**value)
                elif isinstance(value, str) and "," in value:
                    parts = value.split(",")
                    if len(parts) == 2:
                        start = datetime.strptime(parts[0].strip(), "%Y-%m-%d").date()
                        end = datetime.strptime(parts[1].strip(), "%Y-%m-%d").date()
                        return DateRange(start=start, end=end)
                raise ValueError(
                    "Date range must be provided as DateRange object, dict, or 'start,end' string"
                )
        except Exception as e:
            raise ValueError(
                f"Failed to convert parameter '{definition.name}' to {param_type}: {str(e)}"
            )

    def _run_validator(self, value: Any, validator: Dict[str, Any]) -> Any:
        """Run a custom validator on the value."""
        validator_type = validator.get("type")

        if validator_type == "min":
            min_val = validator.get("value")
            if value < min_val:
                raise ValueError(f"Value must be >= {min_val}")
        elif validator_type == "max":
            max_val = validator.get("value")
            if value > max_val:
                raise ValueError(f"Value must be <= {max_val}")
        elif validator_type == "min_length":
            min_len = validator.get("value")
            if len(value) < min_len:
                raise ValueError(f"Length must be >= {min_len}")
        elif validator_type == "max_length":
            max_len = validator.get("value")
            if len(value) > max_len:
                raise ValueError(f"Length must be <= {max_len}")
        elif validator_type == "regex":
            pattern = validator.get("value")
            if not re.match(pattern, str(value)):
                raise ValueError(f"Value must match pattern: {pattern}")

        return value


class ParameterInjector:
    """Handles parameter injection into templates and queries."""

    def __init__(self):
        """Initialize the parameter injector."""
        self._definitions: Dict[str, ParameterDefinition] = {}
        self._validator = ParameterValidator()
        self._special_params: Dict[str, Callable] = {
            "today": lambda: date.today(),
            "now": lambda: datetime.now(),
            "yesterday": lambda: date.today() - timedelta(days=1),
            "last_week": lambda: DateRange(
                start=date.today() - timedelta(days=7), end=date.today()
            ),
            "last_month": lambda: self._get_last_month_range(),
            "current_month": lambda: self._get_current_month_range(),
            "current_year": lambda: DateRange(
                start=date(date.today().year, 1, 1), end=date.today()
            ),
        }

    def register_parameter(self, definition: ParameterDefinition):
        """Register a parameter definition."""
        self._definitions[definition.name] = definition

    def inject_parameters(
        self,
        template: str,
        parameters: Dict[str, Any],
        validate: bool = True,
    ) -> str:
        """Inject parameters into a template string."""
        # Validate parameters if requested
        if validate:
            validated_params = {}
            for name, value in parameters.items():
                if name in self._definitions:
                    validated_params[name] = self._validator.validate(
                        value, self._definitions[name]
                    )
                else:
                    validated_params[name] = value
        else:
            validated_params = parameters.copy()

        # Add special parameters
        for name, func in self._special_params.items():
            if name not in validated_params:
                validated_params[name] = func()

        # Replace placeholders in template
        result = template

        # Handle {{ parameter }} style
        pattern = r"\{\{\s*(\w+)\s*\}\}"
        matches = re.findall(pattern, result)
        for match in matches:
            if match in validated_params:
                value = validated_params[match]
                if isinstance(value, (date, datetime)):
                    value = str(value)
                elif isinstance(value, DateRange):
                    value = f"{value.start} to {value.end}"
                result = result.replace(f"{{{{{match}}}}}", str(value))

        # Handle :parameter style for SQL
        pattern = r":(\w+)"
        matches = re.findall(pattern, result)
        for match in matches:
            if match in validated_params:
                value = validated_params[match]
                if isinstance(value, str):
                    value = f"'{value}'"
                elif isinstance(value, (date, datetime)):
                    value = f"'{value}'"
                elif isinstance(value, list):
                    value = (
                        "("
                        + ",".join(
                            f"'{v}'" if isinstance(v, str) else str(v) for v in value
                        )
                        + ")"
                    )
                elif isinstance(value, DateRange):
                    # Don't replace, will be handled separately
                    continue
                result = result.replace(f":{match}", str(value))

        return result

    def inject_sql_parameters(
        self,
        query: str,
        parameters: Dict[str, Any],
        validate: bool = True,
    ) -> tuple[str, Dict[str, Any]]:
        """Inject parameters into SQL query, returning query and parameter dict."""
        # Validate parameters
        if validate:
            validated_params = {}
            for name, value in parameters.items():
                if name in self._definitions:
                    validated_params[name] = self._validator.validate(
                        value, self._definitions[name]
                    )
                else:
                    validated_params[name] = value
        else:
            validated_params = parameters.copy()

        # Handle date ranges specially
        processed_query = query
        sql_params = {}

        for name, value in validated_params.items():
            if isinstance(value, DateRange):
                # Replace :param with date range conditions
                pattern = f":(\\w+)\\s*=\\s*:{name}"
                replacement = value.to_sql_conditions("\\1")
                processed_query = re.sub(pattern, replacement, processed_query)
            else:
                sql_params[name] = value

        return processed_query, sql_params

    def create_parameter_set(
        self,
        base_params: Dict[str, Any],
        variations: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Create multiple parameter sets for batch report generation."""
        parameter_sets = []

        for variation in variations:
            params = base_params.copy()
            params.update(variation)
            parameter_sets.append(params)

        return parameter_sets

    def _get_last_month_range(self) -> DateRange:
        """Get the date range for last month."""
        today = date.today()
        first_day_this_month = date(today.year, today.month, 1)
        last_day_last_month = first_day_this_month - timedelta(days=1)
        first_day_last_month = date(
            last_day_last_month.year, last_day_last_month.month, 1
        )

        return DateRange(start=first_day_last_month, end=last_day_last_month)

    def _get_current_month_range(self) -> DateRange:
        """Get the date range for current month."""
        today = date.today()
        first_day = date(today.year, today.month, 1)

        # Calculate last day of month
        if today.month == 12:
            last_day = date(today.year, 12, 31)
        else:
            last_day = date(today.year, today.month + 1, 1) - timedelta(days=1)

        return DateRange(start=first_day, end=last_day)

    def get_parameter_documentation(self) -> List[Dict[str, Any]]:
        """Get documentation for all registered parameters."""
        docs = []

        # Add registered parameters
        for param in self._definitions.values():
            doc = {
                "name": param.name,
                "type": param.type.value,
                "description": param.description,
                "required": param.required,
                "default": param.default,
                "choices": param.choices,
            }
            docs.append(doc)

        # Add special parameters
        for name, func in self._special_params.items():
            doc = {
                "name": name,
                "type": "special",
                "description": f"Special parameter that returns {name}",
                "required": False,
                "default": None,
                "choices": None,
            }
            docs.append(doc)

        return docs
