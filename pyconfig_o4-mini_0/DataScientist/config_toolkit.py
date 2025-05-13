import xml.etree.ElementTree as ET
import json
import requests
import base64
import warnings
import os

# Import boto3 if available, otherwise create a stub so that monkeypatching works
try:
    import boto3
except ImportError:
    import types
    boto3 = types.SimpleNamespace(
        client=lambda *args, **kwargs: (_ for _ in ()).throw(Exception("boto3 not available"))
    )

# Expose boto3 into builtins so that tests referring to boto3 without importing it will find it
import builtins
builtins.boto3 = boto3

# Attempt to import real yaml, fallback to stub in yaml.py
try:
    import yaml
except ImportError:
    # yaml.py stub should be alongside this module
    import yaml


class ConfigError(Exception):
    def __init__(self, message, file=None, line=None, context=None):
        self.message = message
        self.file = file
        self.line = line
        self.context = context
        super().__init__(self.__str__())

    def __str__(self):
        parts = [self.message]
        if self.file is not None:
            parts.append(f"File: {self.file}")
        if self.line is not None:
            parts.append(f"Line: {self.line}")
        if self.context is not None:
            parts.append(f"Context: {self.context}")
        return " | ".join(parts)


def load_yaml(path):
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        # YAML or JSON parse failure
        raise ConfigError(f"YAML parse error: {e}", file=path, context=str(e))


def load_xml(path):
    try:
        tree = ET.parse(path)
        root = tree.getroot()
        result = {}
        for child in root:
            result[child.tag] = child.text
        return result
    except ET.ParseError as e:
        raise ConfigError(f"XML parse error: {e}", file=path, context=str(e))


def load_url(url):
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        content_type = resp.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            return resp.json()
        else:
            # Try YAML (or stubbed JSON)
            return yaml.safe_load(resp.text)
    except Exception as e:
        raise ConfigError(f"URL load error: {e}", context=str(e))


def decrypt_token(token):
    try:
        # enforce strict base64 validation
        decoded = base64.b64decode(token, validate=True)
        return decoded.decode('utf-8')
    except Exception as e:
        raise ConfigError(f"Token decryption error: {e}", context=str(e))


def get_secret(secret_name):
    try:
        client = boto3.client('secretsmanager')
        resp = client.get_secret_value(SecretId=secret_name)
        secret = resp.get('SecretString')
        if secret is None:
            # binary
            secret = resp.get('SecretBinary')
            if secret is not None:
                secret = base64.b64decode(secret).decode('utf-8')
        return secret
    except Exception as e:
        raise ConfigError(f"Secret retrieval error: {e}", context=str(e))


def merge_configs(defaults, experiment, env, list_strategy='unique'):
    def merge(a, b):
        if isinstance(a, dict) and isinstance(b, dict):
            result = dict(a)
            for k, v in b.items():
                if k in result:
                    result[k] = merge(result[k], v)
                else:
                    result[k] = v
            return result
        if isinstance(a, list) and isinstance(b, list):
            if list_strategy == 'replace':
                return b
            # unique merge preserving order: a then b
            merged = list(a)
            for item in b:
                if item not in merged:
                    merged.append(item)
            return merged
        # override for other types
        return b

    merged = merge(defaults or {}, experiment or {})
    merged = merge(merged, env or {})
    return merged


def warn_deprecated(config, deprecation_map):
    for old, new in deprecation_map.items():
        if old in config:
            warnings.warn(
                f"Config key '{old}' is deprecated, use '{new}' instead",
                DeprecationWarning
            )
            config[new] = config.pop(old)
    return config


def validate_config(config, schema):
    """
    Minimal schema validation supporting:
      - type: object
      - required fields
      - simple property type checks ('number', 'string', 'integer', 'boolean')
    """
    # Check top-level type
    expected_type = schema.get('type')
    if expected_type == 'object' and not isinstance(config, dict):
        raise ConfigError("Schema validation error: instance is not an object", context="path: []")

    # Check required fields
    for field in schema.get('required', []):
        if field not in config:
            raise ConfigError(f"Schema validation error: '{field}' is a required property", context=f"path: ['{field}']")

    # Check property types
    for prop, subschema in schema.get('properties', {}).items():
        if prop in config and 'type' in subschema:
            val = config[prop]
            expected = subschema['type']
            if expected == 'number':
                if not isinstance(val, (int, float)):
                    raise ConfigError(f"Schema validation error: '{prop}' is not of type '{expected}'", context=f"path: ['{prop}']")
            elif expected == 'integer':
                if not isinstance(val, int):
                    raise ConfigError(f"Schema validation error: '{prop}' is not of type '{expected}'", context=f"path: ['{prop}']")
            elif expected == 'string':
                if not isinstance(val, str):
                    raise ConfigError(f"Schema validation error: '{prop}' is not of type '{expected}'", context=f"path: ['{prop}']")
            elif expected == 'boolean':
                if not isinstance(val, bool):
                    raise ConfigError(f"Schema validation error: '{prop}' is not of type '{expected}'", context=f"path: ['{prop}']")
            # other types can be added as needed
    # Valid
    return None


def export_json_schema(schema):
    return json.dumps(schema, indent=2)


def prompt_missing(config, required_fields):
    for field in required_fields:
        if config.get(field) in (None, ''):
            val = input(f"Enter value for '{field}': ")
            config[field] = val
    return config


def generate_docs(config):
    md = "# Configuration Documentation\n\n"

    def recurse(d, prefix=''):
        nonlocal md
        for k, v in d.items():
            if isinstance(v, dict):
                md += f"\n## {prefix + k}\n"
                recurse(v, prefix=prefix + k + ".")
            else:
                md += f"- **{prefix + k}**: {v}\n"

    recurse(config)
    return md


# For custom format loaders
def load_legacy_xml(path):
    return load_xml(path)


def load_custom_url_settings(url):
    return load_url(url)
