import logging
from collections import defaultdict

logger = logging.getLogger("validation")
logger.addHandler(logging.NullHandler())

class FieldError:
    def __init__(self, path, message):
        self.path = path
        self.message = message

    def to_dict(self):
        return {"path": self.path, "message": self.message}

    def __str__(self):
        return f"{self.path}: {self.message}"

class ValidationError(Exception):
    def __init__(self, errors):
        self.errors = errors
        messages = "; ".join(str(e) for e in errors)
        super().__init__(messages)

class Field:
    def __init__(self, name, type_, required=True, default=None, alias=None, validators=None):
        self.name = name
        self.type_ = type_
        self.required = required
        self.default = default
        self.alias = alias
        self.validators = validators or []

class Schema:
    def __init__(self, fields):
        self.fields = {f.name: f for f in fields}
        self.alias_map = {f.alias: f.name for f in fields if f.alias}

class Validator:
    def __init__(self, schema, strict=True, plugins=None):
        self.schema = schema
        self.strict = strict
        self.plugins = plugins or []

    def validate(self, data):
        logger.info("Starting validation")
        errors = []
        cleaned = {}
        # handle aliases
        data_map = {}
        for k, v in data.items():
            if k in self.schema.alias_map:
                data_map[self.schema.alias_map[k]] = v
                logger.debug(f"Alias mapping: {k} -> {self.schema.alias_map[k]}")
            else:
                data_map[k] = v
        # strict mode: detect extra
        if self.strict:
            for k in data_map:
                if k not in self.schema.fields:
                    msg = f"Unexpected field '{k}'"
                    errors.append(FieldError(k, msg))
                    logger.warning(msg)
        # validate each field
        for name, field in self.schema.fields.items():
            if name in data_map:
                raw = data_map[name]
            else:
                if field.required and field.default is None:
                    msg = "Missing required field"
                    errors.append(FieldError(name, msg))
                    logger.warning(f"{name}: {msg}")
                    continue
                raw = field.default
                logger.debug(f"Using default for {name}: {raw}")
            # type coercion
            try:
                val = self._coerce(raw, field.type_)
                logger.debug(f"Coerced field {name}: {raw} -> {val}")
            except Exception as e:
                msg = f"Type error: {e}"
                errors.append(FieldError(name, msg))
                logger.warning(f"{name}: {msg}")
                continue
            # custom validators
            for fn in field.validators:
                ok, msg = fn(val)
                if not ok:
                    errors.append(FieldError(name, msg))
                    logger.warning(f"{name}: {msg}")
            cleaned[name] = val
        # plugins
        for plugin in self.plugins:
            try:
                plugin(cleaned, errors)
            except Exception as e:
                logger.error(f"Plugin error: {e}")
                errors.append(FieldError("", f"Plugin error: {e}"))
        if errors:
            logger.error("Validation failed with errors")
            raise ValidationError(errors)
        logger.info("Validation succeeded")
        # permissive: include extra fields
        if not self.strict:
            for k, v in data_map.items():
                if k not in cleaned:
                    cleaned[k] = v
        return cleaned

    def _coerce(self, value, expected_type):
        if value is None:
            return None
        if expected_type is int:
            if isinstance(value, int):
                return value
            if isinstance(value, str) and value.isdigit():
                return int(value)
            return int(value)
        if expected_type is float:
            return float(value)
        if expected_type is bool:
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                v = value.lower()
                if v in ("true", "1"):
                    return True
                if v in ("false", "0"):
                    return False
            return bool(value)
        if expected_type is str:
            return str(value)
        # custom complex types pass through
        if isinstance(value, expected_type):
            return value
        raise TypeError(f"Cannot coerce {value!r} to {expected_type}")

