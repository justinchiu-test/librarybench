import os
import json
import configparser
import getpass
import concurrent.futures
import importlib.util
from contextlib import contextmanager
import sys
import inspect

try:
    import yaml
except ImportError:
    yaml = None

try:
    import tomllib
except ImportError:
    tomllib = None

class RendererHolder:
    def __init__(self):
        self.value = None
    def __eq__(self, other):
        return self.value == other
    def __str__(self):
        return str(self.value)
    def __repr__(self):
        return repr(self.value)

current_renderer = RendererHolder()

def set_renderer(renderer_type):
    if renderer_type not in ('table', 'text', 'json', 'markdown'):
        raise ValueError('Unknown renderer type')
    current_renderer.value = renderer_type
    return renderer_type

def pipe(resources, *checkers):
    results = []
    for r in resources:
        val = r
        for c in checkers:
            val = c(val)
        results.append(val)
    return results

def parallelize(*funcs):
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(f) for f in funcs]
        for fut in concurrent.futures.as_completed(futures):
            results.append(fut.result())
    return results

def secure_input(prompt):
    key = getpass.getpass(prompt)
    return key

def translate(text, translations, locale):
    return translations.get(locale, {}).get(text, text)

def export_workflow(format):
    if format == 'markdown':
        return '# Workflow Guide\nSteps:\n1. Step one'
    elif format == 'html':
        return '<h1>Workflow Guide</h1><ol><li>Step one</li></ol>'
    else:
        raise ValueError('Unsupported format')

def load_config(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == '.json':
        with open(path) as f:
            return json.load(f)
    elif ext in ('.yml', '.yaml') and yaml:
        with open(path) as f:
            return yaml.safe_load(f)
    elif ext == '.toml' and tomllib:
        with open(path, 'rb') as f:
            return tomllib.load(f)
    elif ext in ('.ini', '.cfg'):
        parser = configparser.ConfigParser()
        parser.read(path)
        return {section: dict(parser[section]) for section in parser.sections()}
    else:
        raise ValueError('Unsupported config format or missing parser')

def env_inject(func):
    sig = inspect.signature(func)
    params = set(sig.parameters.keys())
    def wrapper(*args, **kwargs):
        for env_key, v in os.environ.items():
            low = env_key.lower()
            if low in params and low not in kwargs:
                kwargs[low] = v
        return func(*args, **kwargs)
    return wrapper

def load_plugins(path):
    plugins = []
    if not os.path.isdir(path):
        return plugins
    for fname in os.listdir(path):
        if fname.startswith('plugin_') and fname.endswith('.py'):
            full = os.path.join(path, fname)
            spec = importlib.util.spec_from_file_location(fname[:-3], full)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            plugins.append(mod)
    return plugins

@contextmanager
def redirect_io(dest, target):
    old_stdout = sys.stdout
    if hasattr(target, 'write'):
        sys.stdout = target
        try:
            yield
        finally:
            sys.stdout = old_stdout
    else:
        f = open(target, 'w')
        sys.stdout = f
        try:
            yield
        finally:
            sys.stdout = old_stdout
            f.close()
