import os
import re
import threading
import time
import textwrap
from datetime import datetime, timedelta

# Try to pick up the standard library tomllib (Python 3.11+), else fall back to PyPI toml
try:
    import tomllib as toml
except ImportError:
    try:
        import toml
    except ImportError:
        toml = None

# YAML will use PyYAML if available; otherwise we provide a minimal fallback
def _fallback_safe_load_all(stream):
    """
    A minimal YAML loader for simple mapping-only documents.
    Splits on '---' and parses nested dicts by indentation.
    """
    content = stream.read()
    # Remove common leading indentation
    content = textwrap.dedent(content)
    parts = content.split('---')
    docs = []
    for part in parts:
        lines = part.splitlines()
        doc = {}
        # Stack of (indent_level, container_dict)
        stack = [(0, doc)]
        for raw_line in lines:
            # Skip empty lines or comment lines
            if not raw_line.strip() or raw_line.lstrip().startswith('#'):
                continue
            indent = len(raw_line) - len(raw_line.lstrip(' '))
            line = raw_line.lstrip(' ')
            if ':' not in line:
                continue
            key, val = line.split(':', 1)
            key = key.strip()
            val = val.strip()
            # Pop stack until parent with lower indent
            while stack and indent <= stack[-1][0] and len(stack) > 1:
                stack.pop()
            parent = stack[-1][1]
            if val == '':
                # Nested dict
                child = {}
                parent[key] = child
                stack.append((indent, child))
            else:
                # Try integer conversion
                if re.fullmatch(r'-?\d+', val):
                    value = int(val)
                else:
                    # Strip quotes if present
                    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                        value = val[1:-1]
                    else:
                        value = val
                parent[key] = value
        if doc:
            docs.append(doc)
    return docs

try:
    import yaml
    # use the real safe_load_all
    _yaml_loader = yaml.safe_load_all
except ImportError:
    yaml = True  # non-None to signal load_yaml should run
    _yaml_loader = _fallback_safe_load_all

_config = {}
_coercers = {}
_hooks = {'pre': [], 'post': [], 'export': []}
_profile = os.environ.get('PYTHON_ENV', 'dev')
VAR_PATTERN = re.compile(r'\$\{([^}]+)\}')

def _merge_dicts(a, b):
    for k, v in b.items():
        if k in a and isinstance(a[k], dict) and isinstance(v, dict):
            _merge_dicts(a[k], v)
        else:
            a[k] = v

def resolve_variables(obj):
    if isinstance(obj, dict):
        return {k: resolve_variables(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [resolve_variables(i) for i in obj]
    if isinstance(obj, str):
        def repl(match):
            key = match.group(1)
            if key in os.environ:
                return os.environ[key]
            val = get(key, '')
            return str(val)
        return VAR_PATTERN.sub(repl, obj)
    return obj

def load_toml(path):
    if toml is None:
        raise RuntimeError("toml library not available")
    for h in _hooks['pre']:
        h()
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    data = toml.loads(content)
    _merge_dicts(_config, data)
    for h in _hooks['post']:
        h(_config)
    return _config

def load_yaml(path):
    """
    Load YAML documents from `path`. Merge first document if dict,
    store remaining docs in 'yaml_docs' list.
    Uses PyYAML if installed, otherwise a simple fallback loader.
    """
    if yaml is None:
        # Should not happen; we ensure yaml is truthy (real or fallback) above
        raise RuntimeError("yaml library not available")
    for h in _hooks['pre']:
        h()
    with open(path, 'r', encoding='utf-8') as f:
        docs = list(_yaml_loader(f))
    if not docs:
        for h in _hooks['post']:
            h(_config)
        return _config

    first, rest = docs[0], []
    if isinstance(first, dict):
        _merge_dicts(_config, first)
        rest = docs[1:]
    else:
        rest = docs

    if rest:
        _config.setdefault('yaml_docs', []).extend(rest)

    for h in _hooks['post']:
        h(_config)
    return _config

def register_coercer(type_name, func):
    _coercers[type_name] = func

def register_hook(hook_type, func):
    if hook_type not in _hooks:
        raise ValueError(f"Unknown hook type: {hook_type}")
    _hooks[hook_type].append(func)

def merge_lists(path, lst, position='append'):
    parts = path.split('.')
    curr = _config
    for p in parts[:-1]:
        curr = curr.setdefault(p, {})
    key = parts[-1]
    existing = curr.get(key, [])
    if not isinstance(existing, list):
        existing = [existing]
    if position == 'prepend':
        curr[key] = lst + existing
    else:
        curr[key] = existing + lst
    return curr[key]

def set_profile(profile=None):
    global _profile
    if profile is None:
        profile = os.environ.get('PYTHON_ENV', 'dev')
    _profile = profile
    os.environ['PYTHON_ENV'] = profile
    return profile

def get(path, default=None):
    parts = path.split('.')
    curr = _config
    for p in parts:
        if isinstance(curr, dict) and p in curr:
            curr = curr[p]
        else:
            return default
    return curr

def with_defaults(defaults):
    def merge(d, defd):
        for k, v in defd.items():
            if k not in d:
                d[k] = v
            else:
                if isinstance(v, dict) and isinstance(d[k], dict):
                    merge(d[k], v)
    merge(_config, defaults)
    return _config

def export_config():
    for h in _hooks['export']:
        h(_config)
    return _config

def watch_and_reload(path, callback, interval=0.1):
    def _watch():
        try:
            last_mtime = os.path.getmtime(path)
        except Exception:
            return
        try:
            callback()
        except Exception:
            pass
        while True:
            try:
                mtime = os.path.getmtime(path)
                if mtime != last_mtime:
                    last_mtime = mtime
                    callback()
                time.sleep(interval)
            except Exception:
                break
    t = threading.Thread(target=_watch, daemon=True)
    t.start()
    return t
