"""
Features module for Localization Manager CLI.
Includes version bump, scaffold, publish, config schema and validation, help formatting,
translation loading, signal handling, DI, config parsing, secrets, subcommand registry, and env override.
"""
import os
import json
import configparser

# Version bump
def bump_version(ver):
    parts = ver.split('.')
    if not all(p.isdigit() for p in parts) or len(parts) != 3:
        raise ValueError(f"Invalid version: {ver}")
    major, minor, patch = map(int, parts)
    patch += 1
    return f"{major}.{minor}.{patch}"

# Scaffold generation
def gen_scaffold(name):
    files = {
        'pyproject.toml': f"[project]\nname = \"{name}\"\n",
        'README.md': f"# {name}\n"
    }
    return {'name': name, 'files': files}

# Publish package
def publish_package(pkg, version):
    return f"Published {pkg} version {version}"

# Config schema and validation
def gen_config_schema(fields):
    props = {f: {'type': 'string'} for f in fields}
    return {'type': 'object', 'properties': props, 'required': fields}

def validate_config(cfg, schema):
    if schema.get('type') != 'object':
        return False
    for key in schema.get('required', []):
        if key not in cfg:
            return False
    for key, prop in schema.get('properties', {}).items():
        if key in cfg:
            if prop.get('type') == 'string' and not isinstance(cfg[key], str):
                return False
    return True

# Help formatting
def format_help(text, fmt='plain'):
    if fmt == 'plain':
        return text
    if fmt == 'md':
        return f"## Help\n\n{text}"
    if fmt == 'ansi':
        return f"\033[1m{text}\033[0m"
    raise ValueError(f"Unknown format: {fmt}")

# Load translations from .po files
def load_translations(path):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    result = {}
    key = None
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('msgid '):
                key = line.split('msgid ', 1)[1].strip().strip('"')
            elif line.startswith('msgstr '):
                val = line.split('msgstr ', 1)[1].strip().strip('"')
                if key is not None:
                    result[key] = val
                    key = None
    return result

# Signal handling decorator
def handle_signals(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            return "Aborted"
    return wrapper

# Dependency injection (identity)
def init_di(deps):
    return dict(deps)

# Parse config files
def parse_config_files(paths):
    if isinstance(paths, str):
        paths = [paths]
    result = {}
    for p in paths:
        low = p.lower()
        if low.endswith('.json'):
            with open(p, 'r') as f:
                data = json.load(f)
            result.update(data)
        elif low.endswith('.ini'):
            cp = configparser.ConfigParser()
            cp.read(p)
            for sec in cp.sections():
                result[sec] = dict(cp[sec])
        elif low.endswith(('.yaml', '.yml')):
            with open(p, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if ':' in line:
                        k, v = line.split(':', 1)
                        val = v.strip()
                        result[k.strip()] = int(val) if val.isdigit() else val
        elif low.endswith('.toml'):
            with open(p, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#') or line.startswith('['):
                        continue
                    if '=' in line:
                        k, v = line.split('=', 1)
                        key = k.strip()
                        val = v.strip().strip("'\"")
                        if val.isdigit():
                            result[key] = int(val)
                        else:
                            result[key] = val
    return result

# Secrets management
def manage_secrets(service, key):
    os.environ[f"SECRET_{service.upper()}"] = key
    return True

# Subcommand registry
def register_subcommands(cmds):
    return dict(cmds)

# Environment override for single value
def env_override(key, default=None):
    return os.getenv(key, default)