import json
import warnings
import os
import re
import base64
from urllib import request

class ConfigError(Exception):
    """Base exception for config errors."""

class SecretManager:
    """Integrate with secret backends (stub implementations)."""

    def fetch_secret(self, provider, secret_id):
        # Stub implementation: just return a formatted string
        return f"fetched-{provider}-{secret_id}"

    def rotate_secret(self, provider, secret_id):
        # Stub implementation: pretend to rotate and return new secret
        return f"rotated-{provider}-{secret_id}"

class JSONSchemaSupport:
    """Provide JSON Schema export and runtime validation."""

    def export_schema(self, schema):
        # Return JSON string of the schema
        return json.dumps(schema, indent=2)

    def validate_schema(self, config, schema):
        # Minimal validation: check required keys
        missing = []
        for key in schema.get("required", []):
            if key not in config:
                missing.append(key)
        if missing:
            raise ConfigError(f"Missing required keys: {missing}")
        # Type checks
        for key, prop in schema.get("properties", {}).items():
            if key in config and "type" in prop:
                expected = prop["type"]
                val = config[key]
                if expected == "object" and not isinstance(val, dict):
                    raise ConfigError(f"Key '{key}' expected object")
                if expected == "array" and not isinstance(val, list):
                    raise ConfigError(f"Key '{key}' expected array")
                if expected == "string" and not isinstance(val, str):
                    raise ConfigError(f"Key '{key}' expected string")
                if expected == "number" and not isinstance(val, (int, float)):
                    raise ConfigError(f"Key '{key}' expected number")
        return True

class DeprecationWarnings:
    """Warn users about deprecated flags or config keys."""

    def warn(self, used_keys, deprecated_map):
        for key in used_keys:
            if key in deprecated_map:
                warnings.warn(
                    f"{key} is deprecated, use {deprecated_map[key]} instead",
                    DeprecationWarning
                )

class ConfigMerger:
    """Merge default flags, config files, and environment variables."""

    def merge(self, *dicts, env_precedence=False):
        result = {}
        for d in dicts:
            if not isinstance(d, dict):
                continue
            for k, v in d.items():
                result[k] = v
        if env_precedence:
            for k, v in os.environ.items():
                result[k] = v
        return result

class InteractiveCLI:
    """Prompt user for missing inputs."""

    def prompt_missing(self, config, required_keys):
        for key in required_keys:
            if key not in config or config[key] in (None, ""):
                val = input(f"Enter value for {key}: ")
                config[key] = val
        return config

class ListMergeStrategies:
    """Support append, replace, and unique merge for lists."""

    def merge(self, lists, strategy="append"):
        if strategy == "replace":
            return lists[-1] if lists else []
        if strategy == "unique":
            seen = set()
            out = []
            for lst in lists:
                for item in lst:
                    if item not in seen:
                        seen.add(item)
                        out.append(item)
            return out
        # default append
        out = []
        for lst in lists:
            out.extend(lst)
        return out

class DocumentationGen:
    """Generate Markdown and HTML docs from schema."""

    def generate(self, schema, format="markdown"):
        props = schema.get("properties", {})
        lines = []
        for key, prop in props.items():
            desc = prop.get("description", "")
            typ = prop.get("type", "")
            line = f"- **{key}** ({typ}): {desc}"
            lines.append(line)
        if format == "html":
            items = "".join(f"<li><strong>{k}</strong> ({v.get('type','')}): {v.get('description','')}</li>"
                            for k, v in props.items())
            return f"<ul>{items}</ul>"
        # default markdown
        return "\n".join(lines)

class CustomFormatLoaders:
    """Register and use custom file-format loaders."""

    def __init__(self):
        self.loaders = {}

    def register(self, fmt, func):
        self.loaders[fmt.lower()] = func

    def load(self, path_or_url):
        if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
            data = request.urlopen(path_or_url).read().decode()
            return json.loads(data)
        ext = os.path.splitext(path_or_url)[1].lstrip(".").lower()
        if ext in self.loaders:
            with open(path_or_url, "r") as f:
                return self.loaders[ext](f.read())
        # fallback JSON
        with open(path_or_url, "r") as f:
            return json.load(f)

class SecretDecryption:
    """Detect and decrypt encrypted secrets."""

    ENC_PATTERN = re.compile(r"ENC\(([^)]+)\)")

    def decrypt(self, value):
        if not isinstance(value, str):
            return value
        m = self.ENC_PATTERN.match(value)
        if m:
            inner = m.group(1)
            try:
                decoded = base64.b64decode(inner).decode("utf-8")
                return decoded
            except Exception:
                raise ConfigError("Failed to base64-decode secret")
        # try base64 auto
        try:
            decoded = base64.b64decode(value).decode("utf-8")
            # only return if printable
            if all(32 <= ord(c) <= 126 for c in decoded):
                return decoded
        except Exception:
            pass
        return value

class ErrorReporting:
    """Surface rich error messages."""

    def report(self, file, line, context, message):
        return f"{file}:{line}: error: {message}\n{context}\n{' '*(len(context)//2)}^"

# Expose all in one namespace
__all__ = [
    "ConfigError",
    "SecretManager",
    "JSONSchemaSupport",
    "DeprecationWarnings",
    "ConfigMerger",
    "InteractiveCLI",
    "ListMergeStrategies",
    "DocumentationGen",
    "CustomFormatLoaders",
    "SecretDecryption",
    "ErrorReporting",
]
