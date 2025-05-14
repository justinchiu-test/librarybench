import yaml
import asyncio

# Ensure a default event loop is set for the main thread so run_until_complete works
# Use get_running_loop to detect absence of a loop without triggering deprecation warnings
try:
    asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

class ValidationError(Exception):
    pass

class PluginInterface:
    def validate(self, data, errors):
        raise NotImplementedError()

class FormValidator:
    def __init__(self, strict_mode=False, username_check_func=None, browser_locale="en-US"):
        # Ensure there's an event loop available for sync contexts (run_until_complete)
        try:
            asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        self.strict_mode = strict_mode
        # Default username check returns True
        self.username_check_func = username_check_func or (lambda u: asyncio.sleep(0, result=True))
        self.browser_locale = browser_locale
        self.plugins = []
        # Schema definitions per field
        self.schema = {
            "username": {"required": True, "type": str},
            "password": {"required": True, "type": str, "min_length": 8, "max_length": 64},
            "age": {"required": True, "type": int, "min": 13, "max": 120},
            "gender": {"required": True, "type": str, "enum": ["male", "female", "other"]},
            "plan_type": {"required": True, "type": str, "enum": ["free", "basic", "premium"]},
            "newsletter_opt_in": {"required": True, "type": bool, "enum": [True, False]},
            "user_type": {"required": True, "type": str, "enum": ["individual", "business"]},
            "company_name": {"required": False, "type": str},
            "country": {"required": False, "type": str, "default": "US"},
            "language": {"required": False, "type": str, "default": None},
            "profile_picture": {"required": False, "type": str, "tooltip": "Upload your profile picture"},
            "bio": {"required": False, "type": str, "tooltip": "Tell us about yourself"},
        }

    def register_plugin(self, plugin):
        if not isinstance(plugin, PluginInterface):
            raise ValidationError("Invalid plugin")
        self.plugins.append(plugin)

    async def validate(self, data):
        errors = {}
        validated = {}

        # Unknown fields handling
        for key in data:
            if key not in self.schema:
                if self.strict_mode:
                    errors.setdefault(key, []).append("Unknown field")

        # Apply defaults and initial data
        for field, rules in self.schema.items():
            raw = data.get(field)
            # treat None or empty string as missing
            if field not in data or raw is None or (isinstance(raw, str) and raw == ""):
                if "default" in rules:
                    if rules["default"] is None and field == "language":
                        validated[field] = self.browser_locale
                    else:
                        validated[field] = rules["default"]
                else:
                    validated[field] = raw
            else:
                validated[field] = raw

        # Include any additional data fields so plugins can see them, without overwriting defaults
        for key, value in data.items():
            if key not in self.schema:
                validated[key] = value

        # Field-level validation
        for field, rules in self.schema.items():
            value = validated.get(field)
            # Conditional requirement
            if field == "company_name" and validated.get("user_type") == "business":
                if not value:
                    errors.setdefault(field, []).append("company_name is required for business users")
            # Required check
            if rules.get("required") and (value is None or (value == "" and rules.get("type") != bool)):
                errors.setdefault(field, []).append("Field is required")
            # Type check
            if value is not None and "type" in rules:
                expected = rules["type"]
                if not isinstance(value, expected):
                    errors.setdefault(field, []).append(f"Expected type {expected.__name__}")
                    continue
            # Enum constraint
            if value is not None and "enum" in rules:
                if value not in rules["enum"]:
                    errors.setdefault(field, []).append(f"Value must be one of {rules['enum']}")
            # Range checks for numbers
            if isinstance(value, (int, float)):
                if "min" in rules and value < rules["min"]:
                    errors.setdefault(field, []).append(f"Value must be >= {rules['min']}")
                if "max" in rules and value > rules["max"]:
                    errors.setdefault(field, []).append(f"Value must be <= {rules['max']}")
            # String length checks
            if isinstance(value, str):
                if "min_length" in rules and len(value) < rules["min_length"]:
                    errors.setdefault(field, []).append(f"Length must be >= {rules['min_length']}")
                if "max_length" in rules and len(value) > rules["max_length"]:
                    errors.setdefault(field, []).append(f"Length must be <= {rules['max_length']}")

        # Async username uniqueness
        username = validated.get("username")
        if username:
            unique = await self.username_check_func(username)
            if not unique:
                errors.setdefault("username", []).append("Username is already taken")

        # Plugins validation
        for plugin in self.plugins:
            plugin.validate(validated, errors)

        return {"data": validated, "errors": errors}

    def export_schema(self):
        export_dict = {}
        for field, rules in self.schema.items():
            export_dict[field] = {}
            for k, v in rules.items():
                if callable(v):
                    continue
                export_dict[field][k] = v
        return yaml.safe_dump(export_dict)

    def import_schema(self, yaml_str):
        loaded = yaml.safe_load(yaml_str)
        new_schema = {}
        for field, rules in loaded.items():
            new_schema[field] = rules
        self.schema = new_schema
