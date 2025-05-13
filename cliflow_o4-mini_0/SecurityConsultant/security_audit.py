import os
import sys
import json
import configparser
import getpass
import importlib
import importlib.util
import concurrent.futures
from contextlib import redirect_stdout, redirect_stderr

# Attempt optional imports
try:
    import yaml
except ImportError:
    yaml = None

try:
    import toml
except ImportError:
    toml = None

# Renderer registry
_renderer_registry = {}
_current_renderer = None

def register_renderer(name, func):
    _renderer_registry[name] = func

def set_renderer(name):
    global _current_renderer
    if name not in _renderer_registry:
        raise ValueError(f"Renderer '{name}' not registered")
    _current_renderer = _renderer_registry[name]

def render(data):
    if _current_renderer is None:
        raise RuntimeError("No renderer set")
    return _current_renderer(data)

# Default renderers
def _color_renderer(data):
    return f"\033[94m{data}\033[0m"

def _plain_renderer(data):
    return str(data)

def _json_renderer(data):
    return json.dumps(data)

def _markdown_renderer(data):
    if isinstance(data, dict):
        lines = []
        for k, v in data.items():
            lines.append(f"- **{k}**: {v}")
        return "\n".join(lines)
    return f"- {data}"

register_renderer('color', _color_renderer)
register_renderer('plain', _plain_renderer)
register_renderer('json', _json_renderer)
register_renderer('markdown', _markdown_renderer)

# Pipe functions
def pipe(*funcs):
    def chained(*args, **kwargs):
        result = None
        for i, f in enumerate(funcs):
            if i == 0:
                result = f(*args, **kwargs)
            else:
                result = f(result)
        return result
    return chained

# Parallel execution
def parallelize(*tasks):
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(t) for t in tasks]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    return results

# Secure input
def secure_input(prompt, password=False):
    if password:
        return getpass.getpass(prompt)
    else:
        return input(prompt)

# Translation (mock)
def translate(text, lang):
    return f"[{lang}] {text}"

# Export workflow
def export_workflow(steps, fmt='md'):
    if fmt == 'md' or fmt == 'markdown':
        return "\n".join(f"- {step}" for step in steps)
    elif fmt == 'html':
        items = "".join(f"<li>{step}</li>" for step in steps)
        return f"<ol>{items}</ol>"
    else:
        raise ValueError("Unsupported format")

# Load configuration
def load_config(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == '.json':
        with open(path, 'r') as f:
            return json.load(f)
    elif ext in ('.yaml', '.yml'):
        if yaml is None:
            raise ImportError("PyYAML is not installed")
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    elif ext == '.toml':
        if toml is None:
            raise ImportError("toml library is not installed")
        with open(path, 'r') as f:
            return toml.load(f)
    elif ext in ('.ini', '.cfg'):
        parser = configparser.ConfigParser()
        parser.read(path)
        return {s: dict(parser.items(s)) for s in parser.sections()}
    else:
        raise ValueError("Unsupported config format")

# Environment injection
def env_inject():
    flags = []
    target = os.environ.get('SCAN_TARGET')
    token = os.environ.get('API_TOKEN')
    if target:
        flags.extend(['--scan-target', target])
    if token:
        flags.extend(['--api-token', token])
    return flags

# Plugin loading
def load_plugins(plugin_paths):
    modules = []
    for path in plugin_paths:
        if os.path.isfile(path) and path.endswith('.py'):
            name = os.path.splitext(os.path.basename(path))[0]
            spec = importlib.util.spec_from_file_location(name, path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            modules.append(mod)
        else:
            # assume module name
            mod = importlib.import_module(path)
            modules.append(mod)
    return modules

# IO redirection
class redirect_io:
    def __init__(self, stdout_path=None, stderr_path=None):
        self.stdout_path = stdout_path
        self.stderr_path = stderr_path
        self._stdout_file = None
        self._stderr_file = None

    def __enter__(self):
        if self.stdout_path:
            self._stdout_file = open(self.stdout_path, 'w')
            self._stdout_cm = redirect_stdout(self._stdout_file)
            self._stdout_cm.__enter__()
        if self.stderr_path:
            self._stderr_file = open(self.stderr_path, 'w')
            self._stderr_cm = redirect_stderr(self._stderr_file)
            self._stderr_cm.__enter__()
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.stdout_path:
            self._stdout_cm.__exit__(exc_type, exc, tb)
            self._stdout_file.close()
        if self.stderr_path:
            self._stderr_cm.__exit__(exc_type, exc, tb)
            self._stderr_file.close()
