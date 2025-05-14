import logging

class SchemaValidator:
    def __init__(self, schema, strict_mode=False, optional_fields=True, data_coercion=False,
                 aliases=None, custom_validators=None, plugins=None, logger=None):
        self.schema = schema
        self.strict_mode = strict_mode
        self.optional_fields = optional_fields
        self.data_coercion = data_coercion
        self.aliases = aliases or {}
        self.custom_validators = custom_validators or []
        self.plugins = plugins or []
        self.logger = logger or logging.getLogger(__name__)

    def validate(self, payload):
        errors = []
        for plugin in self.plugins:
            if hasattr(plugin, 'pre_validate'):
                plugin.pre_validate(payload)
        self._validate_schema(self.schema, payload, [], errors)
        for cv in self.custom_validators:
            cv_errors = cv(payload)
            errors.extend(cv_errors)
        for plugin in self.plugins:
            if hasattr(plugin, 'post_validate'):
                plugin.post_validate(payload, errors)
        return errors

    def _validate_schema(self, schema, data, path, errors):
        typ = schema.get('type')
        if typ == 'object':
            if not isinstance(data, dict):
                errors.append({
                    'path': '.'.join(path),
                    'message': f'Expected object at {".".join(path)}',
                    'expected': 'object',
                    'actual': type(data).__name__
                })
                return
            props = schema.get('properties', {})
            # strict mode: no extra fields
            if self.strict_mode:
                allowed = set(props.keys()) | set(self.aliases.keys())
                for key in data:
                    if key not in allowed:
                        errors.append({
                            'path': '.'.join(path + [key]),
                            'message': f'Unexpected field {key}',
                            'expected': 'no additional fields',
                            'actual': key
                        })
            # required fields (and optionally include optional fields if flagged)
            required = list(schema.get('required', []))
            if not self.optional_fields:
                required += schema.get('optional', [])
            for req in required:
                # consider field present if either the canonical name or any alias is in data
                if req not in data:
                    has_alias = False
                    for alias_key, orig in self.aliases.items():
                        if orig == req and alias_key in data:
                            has_alias = True
                            break
                    if not has_alias:
                        errors.append({
                            'path': '.'.join(path + [req]),
                            'message': f'Missing required field {req}',
                            'expected': 'present',
                            'actual': 'missing'
                        })
            # validate each property (using alias if provided)
            for prop, subschema in props.items():
                key = prop
                if prop not in data and prop in self.aliases.values():
                    # map alias to canonical property
                    for alias_key, orig in self.aliases.items():
                        if orig == prop and alias_key in data:
                            key = alias_key
                            break
                if key in data:
                    val = data[key]
                    if self.data_coercion:
                        val = self._coerce(val, subschema.get('type'))
                        data[key] = val
                    self._validate_schema(subschema, val, path + [key], errors)
        else:
            actual_type = type(data).__name__
            # type checks
            if typ == 'integer':
                if not isinstance(data, int):
                    errors.append({
                        'path': '.'.join(path),
                        'message': 'Expected integer',
                        'expected': 'integer',
                        'actual': actual_type
                    })
            elif typ == 'string':
                if not isinstance(data, str):
                    errors.append({
                        'path': '.'.join(path),
                        'message': 'Expected string',
                        'expected': 'string',
                        'actual': actual_type
                    })
            elif typ == 'boolean':
                if not isinstance(data, bool):
                    errors.append({
                        'path': '.'.join(path),
                        'message': 'Expected boolean',
                        'expected': 'boolean',
                        'actual': actual_type
                    })
            # string constraints
            if isinstance(data, str):
                if 'minLength' in schema and len(data) < schema['minLength']:
                    errors.append({
                        'path': '.'.join(path),
                        'message': 'String shorter than minLength',
                        'expected': f"minLength {schema['minLength']}",
                        'actual': f"length {len(data)}"
                    })
                if 'maxLength' in schema and len(data) > schema['maxLength']:
                    errors.append({
                        'path': '.'.join(path),
                        'message': 'String longer than maxLength',
                        'expected': f"maxLength {schema['maxLength']}",
                        'actual': f"length {len(data)}"
                    })
            # numeric constraints
            if isinstance(data, (int, float)):
                if 'minimum' in schema and data < schema['minimum']:
                    errors.append({
                        'path': '.'.join(path),
                        'message': 'Value less than minimum',
                        'expected': f"minimum {schema['minimum']}",
                        'actual': data
                    })
                if 'maximum' in schema and data > schema['maximum']:
                    errors.append({
                        'path': '.'.join(path),
                        'message': 'Value greater than maximum',
                        'expected': f"maximum {schema['maximum']}",
                        'actual': data
                    })

    def _coerce(self, value, expected_type):
        if expected_type == 'integer' and isinstance(value, str):
            if value.isdigit():
                try:
                    return int(value)
                except:
                    return value
        if expected_type == 'boolean' and isinstance(value, str):
            if value.lower() in ('true', 'false'):
                return value.lower() == 'true'
        return value
