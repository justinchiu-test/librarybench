import os
import sys
import json
import getpass
import threading
import configparser
import builtins
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import importlib.util

# Optional imports
try:
    import yaml
except ImportError:
    yaml = None

try:
    import toml
except ImportError:
    toml = None

# Expose yaml and toml to builtins so pytest.skipif in tests can see them
builtins.yaml = yaml
builtins.toml = toml

_renderer = 'plain'
_translations = {
    'es': {'hello': 'hola', 'help': 'ayuda'},
    'fr': {'hello': 'bonjour', 'help': 'aide'}
}

def set_renderer(renderer):
    global _renderer
    allowed = {'color', 'plain', 'json', 'markdown'}
    if renderer not in allowed:
        raise ValueError(f"Renderer '{renderer}' not supported")
    _renderer = renderer

def get_renderer():
    return _renderer

def pipe(*funcs):
    def _piped(arg):
        res = arg
        for f in funcs:
            res = f(res)
        return res
    return _piped

def parallelize(funcs):
    results = []
    # ensure at least one worker
    max_workers = len(funcs) or 1
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(f) for f in funcs]
        for future in futures:
            results.append(future.result())
    return results

def secure_input(prompt=''):
    secret = getpass.getpass(prompt)
    # Attempt to wipe secret from memory by converting to bytearray
    try:
        b = bytearray(secret, 'utf-8')
        for i in range(len(b)):
            b[i] = 0
    except Exception:
        pass
    return secret

def translate(key, locale):
    return _translations.get(locale, {}).get(key, key)

def export_workflow(steps, format='markdown'):
    if format == 'markdown':
        lines = []
        for step in steps:
            name = step.get('name', '')
            desc = step.get('description', '')
            lines.append(f"- {name}: {desc}")
        return "\n".join(lines)
    elif format == 'html':
        parts = []
        for step in steps:
            name = step.get('name', '')
            desc = step.get('description', '')
            parts.append(f"<li>{name}: {desc}</li>")
        return "<ul>" + "".join(parts) + "</ul>"
    else:
        raise ValueError(f"Format '{format}' not supported")

def load_config(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == '.json':
        with open(path, 'r') as f:
            return json.load(f)
    elif ext in ('.yaml', '.yml'):
        if yaml is None:
            raise ImportError("PyYAML is required for YAML support")
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    elif ext == '.toml':
        if toml is None:
            raise ImportError("toml is required for TOML support")
        return toml.load(path)
    elif ext == '.ini':
        parser = configparser.ConfigParser()
        parser.read(path)
        data = {}
        for section in parser.sections():
            data[section] = dict(parser.items(section))
        return data
    else:
        raise ValueError(f"Unsupported config format: {ext}")

def env_inject(args, mapping):
    # args can be dict or namespace
    is_namespace = not isinstance(args, dict)
    for env_var, flag in mapping.items():
        val = os.environ.get(env_var)
        if val is not None:
            if is_namespace:
                if not hasattr(args, flag) or getattr(args, flag) is None:
                    setattr(args, flag, val)
            else:
                if args.get(flag) is None:
                    args[flag] = val
    return args

def load_plugins(plugin_dir):
    plugins = {}
    if not os.path.isdir(plugin_dir):
        return plugins
    for fname in os.listdir(plugin_dir):
        if fname.endswith('.py') and fname != '__init__.py':
            path = os.path.join(plugin_dir, fname)
            name = os.path.splitext(fname)[0]
            spec = importlib.util.spec_from_file_location(name, path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                plugins[name] = module
    return plugins

@contextmanager
def redirect_io(file_path):
    old_out, old_err = sys.stdout, sys.stderr
    with open(file_path, 'a+') as f:
        sys.stdout = f
        sys.stderr = f
        try:
            yield
        finally:
            sys.stdout.flush()
            sys.stderr.flush()
            sys.stdout, sys.stderr = old_out, old_err
