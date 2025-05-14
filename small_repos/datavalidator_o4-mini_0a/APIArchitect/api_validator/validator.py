from api_validator.versioned_schemas import VersionedSchemas
from api_validator.error_code_support import ErrorCodeSupport
from api_validator.schema_inheritance import SchemaInheritance
from api_validator.performance_metrics import PerformanceMetrics
from api_validator.batch_validation_interface import BatchValidationInterface
from api_validator.default_values import DefaultValues
from api_validator.single_item_validation import SingleItemValidation
from api_validator.conditional_validation import ConditionalValidation
from api_validator.length_constraints import LengthConstraints
from api_validator.optional_fields import OptionalFields

class Validator(
    VersionedSchemas,
    ErrorCodeSupport,
    SchemaInheritance,
    PerformanceMetrics,
    BatchValidationInterface,
    DefaultValues,
    SingleItemValidation,
    ConditionalValidation,
    LengthConstraints,
    OptionalFields
):
    def __init__(self, schema, version=1, conditional_rules=None):
        super().__init__()
        self.register(version, schema)
        self.current_version = version
        self.conditional_rules = conditional_rules or []

    def validate_single(self, data, version=None):
        version = version or self.current_version
        schema = self.get(version)
        # migration placeholder
        data = self.migrate(data, version, self.current_version)
        # defaults
        self.apply_defaults(data, schema)
        # field validation
        result = self.validate_item(data, schema)
        # conditional
        cond_errors = self.apply_conditional(data, self.conditional_rules)
        if cond_errors:
            result['errors'].extend(cond_errors)
            result['valid'] = False
        return result

    @PerformanceMetrics.report
    def validate(self, data, batch=False, version=None):
        if batch:
            return self.validate_batch(data)
        return self.validate_single(data, version)
