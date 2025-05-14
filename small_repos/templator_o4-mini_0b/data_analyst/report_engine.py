import ast
import json
import html
import re as _re
from contextlib import contextmanager

# Try to import YAML; if unavailable, fall back to JSON-based YAML
try:
    import yaml
    _has_yaml = True
except ImportError:
    _has_yaml = False

# Safe string for raw insertion
class SafeString(str):
    pass

def raw(s):
    return SafeString(s)

def autoescape(s):
    if isinstance(s, SafeString):
        return s
    return SafeString(html.escape(str(s)))

def trim_tags(text):
    return _re.sub(r'>\s+<', '><', str(text))

def safe_eval(expr_str):
    try:
        node = ast.parse(expr_str, mode='eval')
    except Exception as e:
        raise ValueError(f"Invalid expression: {e}")
    for n in ast.walk(node):
        if not isinstance(n, (
            ast.Expression, ast.Constant, ast.Tuple, ast.List,
            ast.Dict, ast.Set, ast.UnaryOp, ast.USub,
            ast.UAdd, ast.Load
        )):
            raise ValueError(f"Disallowed expression: {type(n).__name__}")
    return eval(compile(node, '<safe_eval>', 'eval'), {}, {})

def render_stream(data, chunk_size=1024):
    if isinstance(data, str):
        for i in range(0, len(data), chunk_size):
            yield data[i:i+chunk_size]
    elif hasattr(data, '__iter__'):
        lst = list(data)
        for i in range(0, len(lst), chunk_size):
            yield lst[i:i+chunk_size]
    else:
        raise TypeError("Data must be string or iterable")

@contextmanager
def scoped_context(ctx):
    temp = ctx.copy()
    yield temp

def to_json(obj, **kwargs):
    return json.dumps(obj, **kwargs)

def from_json(s):
    return json.loads(s)

if _has_yaml:
    def to_yaml(obj, **kwargs):
        return yaml.safe_dump(obj, **kwargs)

    def from_yaml(s):
        return yaml.safe_load(s)
else:
    # Fallback to JSON for YAML functionality if PyYAML is not installed
    def to_yaml(obj, **kwargs):
        return json.dumps(obj, **kwargs)

    def from_yaml(s):
        return json.loads(s)

def report_error(exc, context=""):
    name = exc.__class__.__name__
    msg = str(exc)
    return f"Error: {name}: {msg} Context: {context}"

# Macro registry and delimiters
macros = {}
delimiters = ("{{", "}}")

def define_macro(name):
    def decorator(fn):
        macros[name] = fn
        return fn
    return decorator

def set_delimiters(start, end):
    global delimiters
    delimiters = (start, end)

@define_macro('bar_chart')
def bar_chart(data, **options):
    start, end = delimiters
    content = f"{start} bar_chart data={data} options={options} {end}"
    return SafeString(content)

@define_macro('line_chart')
def line_chart(data, **options):
    start, end = delimiters
    content = f"{start} line_chart data={data} options={options} {end}"
    return SafeString(content)

def add(a, b):
    return a + b

def sub(a, b):
    return a - b

def mul(a, b):
    return a * b

def div(a, b):
    return a / b

def is_even(n):
    return n % 2 == 0

def is_odd(n):
    return n % 2 != 0
