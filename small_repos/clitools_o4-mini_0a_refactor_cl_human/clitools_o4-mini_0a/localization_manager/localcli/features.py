import json
import os
import re

def bump_version(version: str) -> str:
    """
    Bump the patch version of a semantic version string.
    E.g., '1.2.3' -> '1.2.4'
    """
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', version)
    if not match:
        raise ValueError(f"Invalid version string: {version}")
    major, minor, patch = match.groups()
    new_patch = int(patch) + 1
    return f"{major}.{minor}.{new_patch}"

def gen_scaffold(name: str) -> dict:
    """
    Generate a basic scaffold for a new CLI project.
    """
    files = {
        "pyproject.toml": "[tool.poetry]\nname = \"{}\"\nversion = \"0.1.0\"\n".format(name),
        "README.md": f"# {name}\n\nGenerated scaffold."
    }
    return {"name": name, "files": files}

def publish_package(name: str, version: str) -> str:
    """
    Simulate publishing a package.
    """
    return f"Published {name}=={version}"

def gen_config_schema(fields: list) -> dict:
    """
    Generate a simple JSON schema with string types for given fields.
    """
    properties = {field: {"type": "string"} for field in fields}
    return {"type": "object", "properties": properties, "required": fields}

def validate_config(config: dict, schema: dict) -> bool:
    """
    Validate a config dict against a simple schema.
    """
    if schema.get("type") != "object":
        return False
    props = schema.get("properties", {})
    required = schema.get("required", [])
    for key in required:
        if key not in config or not isinstance(config[key], str):
            return False
    for key, val in config.items():
        if key in props:
            expected = props[key].get("type")
            if expected == "string" and not isinstance(val, str):
                return False
    return True

def format_help(help_text: str, fmt: str = 'plain', locale: str = 'en') -> str:
    """
    Format help text in different styles.
    """
    if fmt == 'plain':
        return help_text
    if fmt == 'md':
        return f"## Help\n\n{help_text}"
    if fmt == 'ansi':
        # bold
        return f"\033[1m{help_text}\033[0m"
    raise ValueError(f"Unknown format: {fmt}")

def load_translations(po_path: str) -> dict:
    """
    Parse a .po file and return msgid->msgstr dict.
    """
    translations = {}
    current_id = None
    with open(po_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('msgid'):
                m = re.match(r'msgid\s+"(.*)"', line)
                if m:
                    current_id = m.group(1)
            elif line.startswith('msgstr') and current_id is not None:
                m = re.match(r'msgstr\s+"(.*)"', line)
                if m:
                    translations[current_id] = m.group(1)
                    current_id = None
    return translations

def handle_signals(func):
    """
    Decorator to handle KeyboardInterrupt and return a friendly message.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            return "Aborted"
    return wrapper

def init_di(services: dict) -> dict:
    """
    Initialize a simple DI container (returns the same dict).
    """
    return services.copy()

def parse_config_files(file_path: str) -> dict:
    """
    Parse JSON, YAML, or TOML config files into dict.
    """
    if file_path.endswith('.json'):
        with open(file_path, encoding='utf-8') as f:
            return json.load(f)
    elif file_path.endswith(('.yaml', '.yml')):
        result = {}
        with open(file_path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if ':' in line:
                    key, val = line.split(':', 1)
                    result[key.strip()] = val.strip()
        return result
    elif file_path.endswith('.toml'):
        result = {}
        with open(file_path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, val = line.split('=', 1)
                    val = val.strip().strip('"').strip("'")
                    result[key.strip()] = val
        return result
    else:
        raise ValueError(f"Unsupported config format: {file_path}")

def manage_secrets(service_name: str, key: str) -> bool:
    """
    Store a secret in environment variables for testing.
    """
    env_key = f"SECRET_{service_name.upper()}"
    os.environ[env_key] = key
    return True

def register_subcommands(commands: dict) -> dict:
    """
    Register subcommands: return the mapping as-is.
    """
    return commands.copy()

def env_override(key: str, default=None):
    """
    Override configuration via environment variables.
    """
    return os.environ.get(key, default)
