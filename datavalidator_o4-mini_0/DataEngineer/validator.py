import time
import copy

class ErrorCodeSupport:
    default_error_codes = {
        'required': 'ERR_REQUIRED',
        'type': 'ERR_TYPE_MISMATCH',
        'length_min': 'ERR_LENGTH_MIN',
        'length_max': 'ERR_LENGTH_MAX',
        'conditional': 'ERR_CONDITIONAL',
    }

    def get_error_code(self, rule):
        return self.default_error_codes.get(rule, 'ERR_UNKNOWN')

class Field(ErrorCodeSupport):
    def __init__(self, type_, default=None, optional=False, min_length=None, max_length=None, condition=None, error_codes=None):
        self.type_ = type_
        self.default = default
        self.optional = optional
        self.min_length = min_length
        self.max_length = max_length
        self.condition = condition
        self.error_codes = error_codes or {}
        self.name = None

    def validate(self, record, value_provided):
        errors = []
        # Conditional skip
        if self.condition and not self.condition(record):
            return errors
        # Missing value
        if not value_provided:
            if self.optional:
                return errors
            else:
                errors.append({
                    'field': self.name,
                    'message': 'Field is required',
                    'code': self.error_codes.get('required', self.get_error_code('required'))
                })
                return errors
        value = record.get(self.name)
        # Type check
        if self.type_ and value is not None and not isinstance(value, self.type_):
            errors.append({
                'field': self.name,
                'message': f'Expected type {self.type_.__name__}',
                'code': self.error_codes.get('type', self.get_error_code('type'))
            })
            return errors
        # Length constraints
        if isinstance(value, (str, list, dict)):
            if self.min_length is not None and len(value) < self.min_length:
                errors.append({
                    'field': self.name,
                    'message': f'Length should be >= {self.min_length}',
                    'code': self.error_codes.get('length_min', self.get_error_code('length_min'))
                })
            if self.max_length is not None and len(value) > self.max_length:
                errors.append({
                    'field': self.name,
                    'message': f'Length should be <= {self.max_length}',
                    'code': self.error_codes.get('length_max', self.get_error_code('length_max'))
                })
        return errors

class Schema:
    def __init__(self, fields=None, bases=None):
        self.fields = {}
        if bases:
            for base in bases:
                self.fields.update(base.fields)
        if fields:
            for name, field in fields.items():
                field.name = name
                self.fields[name] = field

class VersionedSchemas:
    def __init__(self):
        self.schemas = {}
        self.migrations = {}

    def register(self, name, version, schema):
        self.schemas.setdefault(name, {})[version] = schema

    def add_migration(self, name, from_version, to_version, func):
        self.migrations.setdefault(name, {})[(from_version, to_version)] = func

    def migrate(self, name, record):
        if 'version' not in record:
            return record
        rec = record
        current = rec['version']
        versions = sorted(self.schemas.get(name, {}).keys())
        for v in versions:
            if v > current:
                func = self.migrations.get(name, {}).get((current, v))
                if func:
                    rec = func(rec)
                rec['version'] = v
                current = v
        return rec

class PerformanceMetrics:
    def __init__(self):
        self.records = []

    def record(self, count, duration):
        self.records.append({'count': count, 'duration': duration})

    def summary(self):
        total_count = sum(r['count'] for r in self.records)
        total_time = sum(r['duration'] for r in self.records)
        return {'total_records': total_count, 'total_time': total_time}

class Validator:
    def __init__(self, schema, version_name=None, versioned_schemas=None, capture_performance=False):
        self.schema = schema
        self.version_name = version_name
        self.versioned_schemas = versioned_schemas
        self.capture_performance = capture_performance
        self.metrics = PerformanceMetrics() if capture_performance else None

    def validate_single(self, record):
        rec = copy.deepcopy(record)
        # Version migration
        if self.versioned_schemas and self.version_name:
            rec = self.versioned_schemas.migrate(self.version_name, rec)
        errors = []
        # Field validation
        for name, field in self.schema.fields.items():
            provided = name in rec
            # apply default and consider as provided
            if not provided and field.default is not None:
                rec[name] = field.default
                provided = True
            field_errors = field.validate(rec, provided)
            for err in field_errors:
                errors.append(err)
        return {'valid': not errors, 'record': rec, 'errors': errors}

    def validate_batch(self, records):
        results = []
        start = time.perf_counter()
        for rec in records:
            results.append(self.validate_single(rec))
        end = time.perf_counter()
        if self.capture_performance:
            self.metrics.record(len(records), end - start)
        passed = sum(1 for r in results if r['valid'])
        failed = len(results) - passed
        errors = [r['errors'] for r in results]
        summary = {'total': len(results), 'passed': passed, 'failed': failed, 'errors': errors}
        if self.capture_performance:
            summary['metrics'] = self.metrics.summary()
        return summary
