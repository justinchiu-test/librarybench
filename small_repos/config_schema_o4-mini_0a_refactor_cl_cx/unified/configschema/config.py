"""
Core ConfigManager class for managing configuration data.
"""
import os
import copy
from .env import expand_env_vars
from .error import ValidationError
from .schema import infer_schema

class ConfigManager:
    """
    Configuration manager supporting nested get/set, type validation,
    JSON schema export, prompting, and reload.
    """
    def __init__(self, source, file=None, prompt=False):
        # If source is a file path, load configuration
        if isinstance(source, str):
            self.file = source
            self.prompt = prompt
            # disable type checking on direct string instantiation
            self._type_check_on_set = False
            from .loader import load_json, load_ini, load_yaml, yaml
            ext = os.path.splitext(source)[1].lower()
            if ext == '.json':
                data = load_json(source)
            elif ext == '.ini':
                data = load_ini(source)
            elif ext in ('.yaml', '.yml'):
                if yaml is None:
                    raise RuntimeError("YAML support not available")
                data = load_yaml(source)
            else:
                raise RuntimeError(f"Unsupported config format: {source}")
            # Expand environment variables
            data = expand_env_vars(data)
            self._config = data
            # Record initial types
            self._types = {}
            self._record_types(self._config)
            return
        # source is a dict
        self._config = copy.deepcopy(source)
        self.file = file
        self.prompt = prompt
        # enable type checking on set
        self._type_check_on_set = True
        # Record initial types for existing keys
        self._types = {}
        self._record_types(self._config)

    def _record_types(self, obj, prefix=''):
        if isinstance(obj, dict):
            for k, v in obj.items():
                key_path = f"{prefix}.{k}" if prefix else k
                if isinstance(v, dict):
                    self._record_types(v, key_path)
                else:
                    self._types[key_path] = type(v)

    def __eq__(self, other):
        if isinstance(other, ConfigManager):
            return self._config == other._config
        if isinstance(other, dict):
            return self._config == other
        return False

    def __getitem__(self, key):
        return self._config[key]

    def __contains__(self, key):
        return key in self._config

    def get(self, key, default=None, prompt_missing=False):
        """
        Get a configuration value by dot-notated key.
        If missing and prompt_missing or self.prompt, will prompt the user.
        """
        parts = key.split('.')
        curr = self._config
        for part in parts:
            if isinstance(curr, dict) and part in curr:
                curr = curr[part]
            else:
                # Missing key
                if prompt_missing or self.prompt:
                    return self._prompt_and_set(key)
                if default is not None:
                    return default
                raise KeyError(key)
        # Key found
        if (prompt_missing or self.prompt) and (curr is None or curr == ''):
            return self._prompt_and_set(key)
        return curr

    def _prompt_and_set(self, key):
        val = input(f"{key}: ")
        expected_type = self._types.get(key, str)
        try:
            if expected_type == list:
                new_val = val.split(',') if val else []
            else:
                new_val = expected_type(val)
        except Exception:
            new_val = val
        self.set(key, new_val)
        return new_val

    def set(self, key, value):
        """Set a configuration value by dot-notated key, with type validation."""
        parts = key.split('.')
        curr = self._config
        for part in parts[:-1]:
            if part not in curr or not isinstance(curr[part], dict):
                curr[part] = {}
            curr = curr[part]
        last = parts[-1]
        if last in curr:
            expected = self._types.get(key)
            if self._type_check_on_set and expected and not isinstance(value, expected):
                # type validation on set if enabled
                raise ValidationError(
                    file=self.file,
                    key=key,
                    message=f"expected {expected.__name__}",
                    expected=expected.__name__,
                    actual=type(value).__name__
                )
        curr[last] = value
        # update type mapping only if type checking on set is enabled
        if self._type_check_on_set:
            self._types[key] = type(value)

    def serialize(self):
        """Return a deep copy of the configuration dictionary."""
        return copy.deepcopy(self._config)

    def reload(self):
        """Reload configuration from associated file path."""
        if not self.file:
            raise RuntimeError("No file associated with ConfigManager")
        from .loader import load_json, load_ini, load_yaml, yaml
        ext = os.path.splitext(self.file)[1].lower()
        if ext == '.json':
            data = load_json(self.file)
        elif ext == '.ini':
            data = load_ini(self.file)
        elif ext in ('.yaml', '.yml'):
            if yaml is None:
                raise RuntimeError("YAML support not available")
            data = load_yaml(self.file)
        else:
            raise RuntimeError(f"Unsupported config format: {self.file}")
        data = expand_env_vars(data)
        self._config = data
        self._types = {}
        self._record_types(self._config)
    
    def validate_types(self, schema=None):
        """
        Validate configuration values.
        - If schema is None: validate against initial types mapping.
        - If schema is a JSON schema dict: validate using jsonschema.
        - If schema is a mapping of keys to type names: use custom validators.
        """
        # Validate against initial types
        if schema is None:
            # Validate against initial types mapping
            # Map Python types to JSON schema type names
            type_map = {
                int: "integer",
                float: "number",
                str: "string",
                bool: "boolean",
                list: "array",
                type(None): "null",
            }
            for key, expected in self._types.items():
                try:
                    val = self.get(key)
                except KeyError:
                    continue
                if not isinstance(val, expected):
                    exp = type_map.get(expected, expected.__name__)
                    msg = f"expected {exp}"
                    raise ValidationError(
                        file=self.file,
                        key=key,
                        message=msg,
                        expected=exp,
                        actual=type(val).__name__
                    )
            return True
        # JSON schema validation
        if isinstance(schema, dict) and schema.get("type") == "object" and "properties" in schema:
            try:
                import jsonschema
                jsonschema.validate(self._config, schema)
            except Exception as e:
                raise ValidationError(file=self.file, message=f"expected {str(e)}")
            return True
        # Custom type name validators
        if isinstance(schema, dict):
            for key, type_name in schema.items():
                val = self.get(key)
                if type_name == "ip":
                    import ipaddress
                    try:
                        ipaddress.ip_address(val)
                    except Exception:
                        raise ValidationError(file=self.file, key=key, message="IP address")
                elif type_name == "port":
                    if not isinstance(val, int) or not (0 <= val <= 65535):
                        raise ValidationError(file=self.file, key=key, message="port")
                elif type_name == "bool":
                    if not isinstance(val, bool):
                        raise ValidationError(file=self.file, key=key, message="bool")
                elif type_name == "token":
                    if not isinstance(val, str):
                        raise ValidationError(file=self.file, key=key, message="token")
            return True
        raise ValueError("Invalid schema for validate_types")

    def prompt_missing(self, keys=None):
        """Prompt for missing configuration values."""
        targets = []
        if keys is None:
            # find None or empty values
            def _find(obj, prefix=''):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        path = f"{prefix}.{k}" if prefix else k
                        if v is None or v == '':
                            targets.append(path)
                        elif isinstance(v, dict):
                            _find(v, path)
                # lists not prompted
            _find(self._config)
        else:
            targets = list(keys)
        for key in targets:
            self._prompt_and_set(key)
    
    def expand_env_vars(self):
        """Expand environment variables in the configuration in place."""
        from .env import expand_env_vars as _expand_env_vars
        self._config = _expand_env_vars(self._config)

    def export_json_schema(self):
        """Export the configuration as a JSON schema dict, including defaults."""
        schema = infer_schema(self._config)
        # Attach default values
        def _attach(sch, obj):
            if sch.get('type') == 'object' and isinstance(obj, dict):
                for k, v in obj.items():
                    prop = sch.get('properties', {}).get(k)
                    if prop is not None:
                        prop['default'] = v
                        _attach(prop, v)
            elif sch.get('type') == 'array' and isinstance(obj, list) and sch.get('items'):
                _attach(sch['items'], obj[0])
        _attach(schema, self._config)
        return schema