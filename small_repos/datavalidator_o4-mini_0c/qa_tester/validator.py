import re
import asyncio

class ValidationError:
    def __init__(self, path, message):
        self.path = path
        self.message = message

    def __eq__(self, other):
        return isinstance(other, ValidationError) and self.path == other.path and self.message == other.message

    def __repr__(self):
        return f"ValidationError(path='{self.path}', message='{self.message}')"

class Validator:
    def __init__(self, schema, strict=False, plugins=None, timeout=1.0):
        self.schema = schema
        self.strict = strict
        self.plugins = plugins or []
        self.timeout = timeout

    def validate(self, data, single_item=False, context=None):
        errors = []
        # Handle list vs object
        if isinstance(data, list):
            if single_item:
                for idx, item in enumerate(data):
                    errs = self._validate_object(item, self.schema, f"[{idx}]", context)
                    errors.extend(errs)
            else:
                errors.append(ValidationError("", "Expected object, got list"))
        elif isinstance(data, dict):
            errors.extend(self._validate_object(data, self.schema, "", context))
        else:
            errors.append(ValidationError("", f"Expected object, got {type(data).__name__}"))
        # Plugin validations
        for plugin in self.plugins:
            plugin_errors = plugin(data)
            for path, msg in plugin_errors:
                errors.append(ValidationError(path, msg))
        return errors

    def _validate_object(self, data, schema, path, context):
        errors = []
        if not isinstance(data, dict):
            errors.append(ValidationError(path, f"Expected object, got {type(data).__name__}"))
            return errors
        properties = schema.get("properties", {})
        # Strict mode: unexpected extras
        if self.strict:
            for key in data:
                if key not in properties:
                    errors.append(ValidationError(self._make_path(path, key), "Unexpected field"))
        # Validate each property
        for key, prop in properties.items():
            fpath = self._make_path(path, key)
            # Handle missing
            if key not in data:
                if "default" in prop:
                    default = prop["default"]
                    if isinstance(default, dict):
                        locale = context.get("locale") if context else None
                        data[key] = default.get(locale, default.get("default"))
                    else:
                        data[key] = default
                if prop.get("required"):
                    errors.append(ValidationError(fpath, "Missing required field"))
                continue
            val = data[key]
            # Nullability
            if val is None:
                if not prop.get("nullable", False):
                    errors.append(ValidationError(fpath, "Field is not nullable"))
                else:
                    continue
            # Type checks
            expected = prop.get("type")
            if expected:
                if expected == "string" and not isinstance(val, str):
                    errors.append(ValidationError(fpath, "Expected string"))
                    continue
                if expected == "integer" and not isinstance(val, int):
                    errors.append(ValidationError(fpath, "Expected integer"))
                    continue
                if expected == "number" and not isinstance(val, (int, float)):
                    errors.append(ValidationError(fpath, "Expected number"))
                    continue
                if expected == "boolean" and not isinstance(val, bool):
                    errors.append(ValidationError(fpath, "Expected boolean"))
                    continue
                if expected == "array" and not isinstance(val, list):
                    errors.append(ValidationError(fpath, "Expected array"))
                    continue
                if expected == "object" and not isinstance(val, dict):
                    errors.append(ValidationError(fpath, "Expected object"))
                    continue
            # Enum check
            if "enum" in prop:
                if val not in prop["enum"]:
                    errors.append(ValidationError(fpath, f"Value '{val}' not in enum {prop['enum']}"))
            # Range checks
            if isinstance(val, (int, float)):
                if "minimum" in prop and val < prop["minimum"]:
                    errors.append(ValidationError(fpath, f"Value {val} below minimum {prop['minimum']}"))
                if "maximum" in prop and val > prop["maximum"]:
                    errors.append(ValidationError(fpath, f"Value {val} above maximum {prop['maximum']}"))
            # Conditional validation
            if "conditional" in prop:
                cond = prop["conditional"]
                cond_if = cond.get("if", {})
                cond_then = cond.get("then", {})
                if all(data.get(k) == v for k, v in cond_if.items()):
                    # apply then rules
                    if "type" in cond_then:
                        ctype = cond_then["type"]
                        if ctype == "string" and not isinstance(val, str):
                            errors.append(ValidationError(fpath, "Conditional: Expected string"))
                    if "pattern" in cond_then:
                        pattern = cond_then["pattern"]
                        if not re.match(pattern, val or ""):
                            errors.append(ValidationError(fpath, "Conditional: Pattern mismatch"))
            # Async validation
            if "async" in prop:
                async_conf = prop["async"]
                func = async_conf["func"]
                t = async_conf.get("timeout", self.timeout)
                loop = asyncio.new_event_loop()
                try:
                    coro = func(val)
                    try:
                        res = loop.run_until_complete(asyncio.wait_for(coro, timeout=t))
                        if not res:
                            errors.append(ValidationError(fpath, "Async validation failed"))
                    except asyncio.TimeoutError:
                        errors.append(ValidationError(fpath, "Async validation timeout"))
                except Exception as e:
                    errors.append(ValidationError(fpath, f"Async validation error: {str(e)}"))
                finally:
                    loop.close()
        return errors

    def _make_path(self, base, key):
        return f"{base}.{key}" if base else key
