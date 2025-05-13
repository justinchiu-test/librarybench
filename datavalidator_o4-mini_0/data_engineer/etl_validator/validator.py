import asyncio
from datetime import datetime
from .external import default_external_validator

class ValidationResult:
    def __init__(self, success, record, errors=None, warnings=None):
        self.success = success
        self.record = record
        self.errors = errors or []
        self.warnings = warnings or []

    def __repr__(self):
        return f"<ValidationResult success={self.success} errors={self.errors} warnings={self.warnings}>"

class Validator:
    def __init__(self, schema, plugin_manager=None, external_validator=None, strict=None):
        self.schema = schema
        self.plugin_manager = plugin_manager
        self.external_validator = external_validator or default_external_validator
        self.strict = strict if strict is not None else self.schema.strict

    def validate(self, record):
        # Synchronous wrapper
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(self.validate_async(record))

    async def validate_async(self, record):
        rec = dict(record)  # copy to avoid mutation
        errors = []
        warnings = []

        # Strict mode: no extra fields
        allowed = set(self.schema.fields.keys())
        extra = set(rec.keys()) - allowed
        if self.strict and extra:
            for f in extra:
                errors.append({'field': f, 'code': 'EXTRA_FIELD', 'message': f'Unexpected field {f}'})
            return ValidationResult(False, rec, errors, warnings)

        # Apply default values
        for fname, props in self.schema.fields.items():
            if fname not in rec and 'default' in props:
                default = props['default']
                if default == 'now':
                    rec[fname] = datetime.utcnow().isoformat()
                else:
                    rec[fname] = default

        # Apply plugins
        if self.plugin_manager:
            rec = self.plugin_manager.apply(rec)

        # Field validations
        for fname, props in self.schema.fields.items():
            cond = props.get('condition')
            # Determine if we should skip or enforce conditional requirement
            if cond:
                other = cond.get('field')
                eq = cond.get('equals')
                if rec.get(other) != eq:
                    # Condition not met => skip all validation for this field
                    continue
                # Condition met => treat as required even if props['required'] is False
                is_required = True
            else:
                is_required = props.get('required', False)

            val = rec.get(fname)

            # Required check (including conditional requirement)
            if is_required and val is None:
                errors.append({'field': fname, 'code': 'REQUIRED', 'message': f'{fname} is required'})
                continue
            if val is None:
                # nothing to do for non-present, non-required
                continue

            # Type check
            ftype = props.get('type')
            if ftype == 'number':
                if not isinstance(val, (int, float)):
                    errors.append({'field': fname, 'code': 'TYPE', 'message': f'{fname} must be a number'})
                    continue
            elif ftype == 'string':
                if not isinstance(val, str):
                    errors.append({'field': fname, 'code': 'TYPE', 'message': f'{fname} must be a string'})
                    continue

            # Enum constraints
            if 'values' in props:
                if val not in props['values']:
                    errors.append({'field': fname, 'code': 'ENUM', 'message': f'{fname} must be one of {props["values"]}'})

            # Range checks
            minv = props.get('min')
            maxv = props.get('max')
            if isinstance(val, (int, float)):
                if minv is not None and val < minv:
                    errors.append({'field': fname, 'code': 'RANGE', 'message': f'{fname} must be >= {minv}'})
                if maxv is not None and val > maxv:
                    errors.append({'field': fname, 'code': 'RANGE', 'message': f'{fname} must be <= {maxv}'})

            # Async external validation
            if props.get('async'):
                ok = await self.external_validator(fname, val)
                if not ok:
                    errors.append({'field': fname, 'code': 'EXTERNAL', 'message': f'{fname} failed external validation'})

            # Optional fields flagged
            if not props.get('required', False) and fname in rec:
                warnings.append({'field': fname, 'code': 'OPTIONAL', 'message': f'{fname} is optional and present'})

        success = len(errors) == 0
        return ValidationResult(success, rec, errors, warnings)
