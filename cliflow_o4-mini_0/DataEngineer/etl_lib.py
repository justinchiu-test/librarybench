import os
import json
import configparser
import gettext
import inspect
import importlib.util
import concurrent.futures
import contextlib
import io
import getpass
import functools

try:
    import yaml
except ImportError:
    yaml = None

try:
    import toml
except ImportError:
    toml = None

# Renderer
renderer = 'plain'
def set_renderer(r):
    global renderer
    renderer = r

# Pipe
def pipe(f, g):
    def wrapped(*args, **kwargs):
        return g(f(*args, **kwargs))
    return wrapped

# Parallelize
def parallelize(func):
    @functools.wraps(func)
    def wrapper(*args, tasks=None, **kwargs):
        if tasks is None:
            return func(*args, **kwargs)
        results = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(t) for t in tasks]
            for fut in concurrent.futures.as_completed(futures):
                results.append(fut.result())
        return results
    return wrapper

# Secure Input
class secure_input:
    def __init__(self, prompt):
        self.prompt = prompt
        self.secret = None
    def __enter__(self):
        self.secret = getpass.getpass(self.prompt)
        return self.secret
    def __exit__(self, exc_type, exc, tb):
        self.secret = None
        return False

# Translate
_translations = {
    'en': {'hello': 'hello', 'bye': 'goodbye'},
    'es': {'hello': 'hola', 'bye': 'adiós'}
}
def translate(message, locale='en'):
    return _translations.get(locale, {}).get(message, message)

# Export Workflow
def export_workflow(functions, format='markdown'):
    if format == 'markdown':
        lines = ["# Workflow"]
        for fn in functions:
            lines.append(f"## {fn.__name__}")
            doc = fn.__doc__ or ""
            lines.append(doc)
        return "\n".join(lines)
    elif format == 'html':
        parts = ["<h1>Workflow</h1>"]
        for fn in functions:
            parts.append(f"<h2>{fn.__name__}</h2>")
            doc = fn.__doc__ or ""
            parts.append(f"<p>{doc}</p>")
        return "\n".join(parts)
    else:
        raise ValueError("Unknown format")

# Load Config
def load_config(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == '.json':
        with open(path, 'r') as f:
            return json.load(f)
    elif ext in ('.yml', '.yaml'):
        if yaml is None:
            raise ImportError("PyYAML not installed")
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    elif ext == '.toml':
        if toml is None:
            raise ImportError("toml not installed")
        with open(path, 'r') as f:
            return toml.load(f)
    elif ext in ('.ini', '.cfg'):
        config = configparser.ConfigParser()
        config.read(path)
        result = {s: dict(config[s]) for s in config.sections()}
        return result
    else:
        raise ValueError("Unsupported config format")

# Env Inject
def env_inject(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        sig = inspect.signature(func)
        for name, param in sig.parameters.items():
            if name not in kwargs and param.default is inspect._empty:
                env_val = os.environ.get(name.upper())
                if env_val is not None:
                    kwargs[name] = env_val
        return func(*args, **kwargs)
    return wrapper

# Load Plugins
def load_plugins(path):
    modules = []
    if not os.path.isdir(path):
        return modules
    for fname in os.listdir(path):
        if fname.endswith('.py') and not fname.startswith('_'):
            full = os.path.join(path, fname)
            spec = importlib.util.spec_from_file_location(fname[:-3], full)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            modules.append(module)
    return modules

# Redirect IO
@contextlib.contextmanager
def redirect_io(stdout=None, stderr=None):
    new_out = stdout if stdout is not None else io.StringIO()
    new_err = stderr if stderr is not None else io.StringIO()
    with contextlib.redirect_stdout(new_out), contextlib.redirect_stderr(new_err):
        yield new_out, new_err
