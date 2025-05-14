import logging

class Plugin:
    def __init__(self):
        self.strict_mode = False
        self.errors = []
        self.logger = logging.getLogger('plugin_ext')
        self.aliases = {}
        self.metadata = {'x-plugin-metadata': {'info': 'plugin_ext'}}
        self.validators = [self.gdpr_validator]

    def register(self, host):
        # Respect host strict/permissive setting
        self.strict_mode = getattr(host, 'strict_mode', False)
        # Hook into host extension points
        if hasattr(host, 'register_hook'):
            host.register_hook('coerce', self.coerce)
            host.register_hook('override_optional_fields', self.override_optional_fields)
        if hasattr(host, 'register_error_reporter'):
            host.register_error_reporter(self.report_error)
        if hasattr(host, 'schema_augmenter'):
            host.schema_augmenter(self.augment_schema)
        if hasattr(host, 'data_generator'):
            host.data_generator(self.generate_test_data)
        # Logging integration
        setattr(host, 'logging_namespace', 'plugin_ext')
        # Validator registration
        if hasattr(host, 'validators') and isinstance(host.validators, list):
            host.validators.extend(self.validators)
        # Field aliases
        setattr(host, 'field_aliases', self.aliases)

    def override_optional_fields(self, schema):
        # Inspect schema optionality and override behavior
        required = schema.get('required', [])
        props = schema.get('properties', {})
        for field, definition in props.items():
            if field not in required:
                definition['nullable'] = True
        return schema

    def coerce(self, data, schema):
        # Custom type transformations
        result = {}
        props = schema.get('properties', {})
        for key, value in data.items():
            field_def = props.get(key, {})
            t = field_def.get('type')
            if t == 'integer':
                try:
                    result[key] = int(value)
                except:
                    result[key] = value
            elif t == 'number':
                try:
                    result[key] = float(value)
                except:
                    result[key] = value
            else:
                result[key] = value
        return result

    def apply_aliases(self, data):
        # Recognize field aliases
        result = {}
        for key, value in data.items():
            actual = self.aliases.get(key, key)
            result[actual] = value
        return result

    def report_error(self, error):
        # Contribute error objects to aggregated report
        self.errors.append(error)

    def generate_test_data(self, schema):
        # Schema-based test data generator
        props = schema.get('properties', {})
        sample = {}
        for key, definition in props.items():
            t = definition.get('type')
            if t == 'string':
                sample[key] = 'test'
            elif t == 'integer':
                sample[key] = 42
            elif t == 'number':
                sample[key] = 3.14
            else:
                sample[key] = None
        return sample

    def augment_schema(self, schema):
        # Augment schema exports with plugin-specific metadata
        schema.update(self.metadata)
        return schema

    def gdpr_validator(self, data, path=''):
        # Simple GDPR compliance check: no emails allowed
        errors = []
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}{key}"
                if isinstance(value, str) and '@' in value:
                    errors.append({
                        'code': 'GDPR001',
                        'message': 'Email not allowed',
                        'path': current_path
                    })
                elif isinstance(value, dict):
                    errors.extend(self.gdpr_validator(value, current_path + '.'))
        return errors
