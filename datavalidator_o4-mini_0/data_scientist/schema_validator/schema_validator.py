import logging
import random
import string

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

class ValidationError(Exception):
    pass

class Field:
    def __init__(self, name, type_, optional=False, aliases=None, default=None, validators=None):
        self.name = name
        self.type = type_
        self.optional = optional
        self.aliases = aliases or []
        self.default = default
        self.validators = validators or []

class Plugin:
    def process(self, field_name, value):
        return value

class SchemaValidator:
    def __init__(self, schema_fields, strict_mode=False):
        """
        schema_fields: list of Field instances
        """
        self.strict_mode = strict_mode
        self.fields = {f.name: f for f in schema_fields}
        # build alias mapping
        self._alias_map = {}
        for fname, field in self.fields.items():
            for alias in [fname] + field.aliases:
                self._alias_map[alias] = fname
        self.plugins = []
        self.logger = logger

    def register_plugin(self, plugin):
        self.plugins.append(plugin)

    def _coerce(self, value, target_type):
        if value is None:
            return None
        if isinstance(value, target_type):
            return value
        if target_type is bool:
            if isinstance(value, str):
                val = value.strip().lower()
                if val in ('true', '1', 'yes'):
                    return True
                if val in ('false', '0', 'no'):
                    return False
                raise ValueError(f"Cannot coerce '{value}' to bool")
            return bool(value)
        if target_type is int:
            return int(value)
        if target_type is float:
            return float(value)
        if target_type is str:
            return str(value)
        # unsupported type
        return target_type(value)

    def validate(self, data):
        """
        data: dict of input values
        returns: (sanitized_data_dict, list_of_error_messages)
        """
        errors = []
        sanitized = {}
        # remap aliases
        remapped = {}
        for key, val in data.items():
            if key in self._alias_map:
                canonical = self._alias_map[key]
                remapped[canonical] = val
            else:
                self.logger.debug(f"Ignoring unknown field '{key}'")

        for fname, field in self.fields.items():
            if fname in remapped:
                raw = remapped[fname]
                try:
                    coerced = self._coerce(raw, field.type)
                    self.logger.debug(f"Coerced field '{fname}': {raw} -> {coerced}")
                except Exception as e:
                    msg = f"Field '{fname}': coercion error: {e}"
                    errors.append(msg)
                    if self.strict_mode:
                        raise ValidationError(msg)
                    coerced = None
                # custom validators
                for validator in field.validators:
                    try:
                        validator(coerced)
                    except Exception as e:
                        msg = f"Field '{fname}': validation error: {e}"
                        errors.append(msg)
                        if self.strict_mode:
                            raise ValidationError(msg)
                # plugins
                for plugin in self.plugins:
                    try:
                        new_val = plugin.process(fname, coerced)
                        self.logger.debug(f"Plugin {plugin.__class__.__name__} processed '{fname}': {coerced} -> {new_val}")
                        coerced = new_val
                    except Exception as e:
                        msg = f"Field '{fname}': plugin error: {e}"
                        errors.append(msg)
                        if self.strict_mode:
                            raise ValidationError(msg)
                sanitized[fname] = coerced
            else:
                if field.optional:
                    sanitized[fname] = field.default
                    self.logger.debug(f"Field '{fname}' missing, default={field.default}")
                else:
                    msg = f"Field '{fname}' missing and required"
                    errors.append(msg)
                    # assign None for missing required fields in non-strict mode
                    sanitized[fname] = None
                    if self.strict_mode:
                        raise ValidationError(msg)
        return sanitized, errors

    def to_json_schema(self):
        properties = {}
        required = []
        for fname, field in self.fields.items():
            t = field.type
            js_type = None
            if t is int:
                js_type = "integer"
            elif t is float:
                js_type = "number"
            elif t is bool:
                js_type = "boolean"
            elif t is str:
                js_type = "string"
            else:
                js_type = "object"
            properties[fname] = {"type": js_type}
            if field.aliases:
                properties[fname]["aliases"] = field.aliases
        for fname, field in self.fields.items():
            if not field.optional:
                required.append(fname)
        schema = {"type": "object", "properties": properties}
        if required:
            schema["required"] = required
        return schema

    def sample(self, n=1):
        """
        Generate n synthetic records according to schema
        """
        records = []
        for _ in range(n):
            rec = {}
            for fname, field in self.fields.items():
                if field.optional and random.random() < 0.2:
                    rec[fname] = field.default
                    continue
                t = field.type
                if t is int:
                    rec[fname] = random.randint(0, 100)
                elif t is float:
                    rec[fname] = random.random() * 100
                elif t is bool:
                    rec[fname] = random.choice([True, False])
                elif t is str:
                    rec[fname] = ''.join(random.choices(string.ascii_letters, k=8))
                else:
                    rec[fname] = None
            records.append(rec)
        return records
