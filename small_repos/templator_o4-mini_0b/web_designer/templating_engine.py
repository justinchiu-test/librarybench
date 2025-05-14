import ast
import json
import html
import traceback

# Try to import yaml; if unavailable, fall back to JSON for YAML functionality
try:
    import yaml
except ImportError:
    yaml = None

def safe_eval(expr):
    try:
        return ast.literal_eval(expr)
    except Exception as e:
        raise ValueError(f"unsafe or invalid expression: {expr}") from e

def render_stream(template, context=None):
    if context is None:
        context = {}
    for line in template.splitlines(keepends=True):
        yield line.format(**context)

class scoped_context:
    def __init__(self, context):
        self._original = context
        self._stack = []

    def __enter__(self):
        # push a copy of the current context onto the stack
        self._stack.append(self._original.copy())
        return self._original

    def __exit__(self, exc_type, exc_value, tb):
        # restore the original context from the stack
        self._original.clear()
        self._original.update(self._stack.pop())

def to_json(obj):
    return json.dumps(obj)

def from_json(s):
    return json.loads(s)

def to_yaml(obj):
    # if PyYAML is available, use it; otherwise, fall back to JSON
    if yaml is not None:
        return yaml.safe_dump(obj)
    return json.dumps(obj)

def from_yaml(s):
    # if PyYAML is available, use it; otherwise, fall back to JSON
    if yaml is not None:
        return yaml.safe_load(s)
    return json.loads(s)

def report_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            tb = traceback.format_exc()
            raise RuntimeError(f"Error in {func.__name__}:\n{tb}")
    return wrapper

def autoescape(s):
    if isinstance(s, RawString):
        return s.text
    return html.escape(str(s))

class RawString:
    def __init__(self, text):
        self.text = text

def raw(s):
    return RawString(str(s))

def trim_tags(s):
    return s.strip()

_macros = {}

def define_macro(name):
    def decorator(func):
        _macros[name] = func
        return func
    return decorator

_delims = {
    'var_start': '{{',
    'var_end': '}}',
    'block_start': '{%',
    'block_end': '%}'
}

def set_delimiters(var_start, var_end, block_start, block_end):
    _delims['var_start'] = var_start
    _delims['var_end'] = var_end
    _delims['block_start'] = block_start
    _delims['block_end'] = block_end

def add(x):
    return lambda y: x + y

def sub(x):
    return lambda y: x - y

def mul(x):
    return lambda y: x * y

def div(x):
    return lambda y: x / y

def is_even(n):
    return n % 2 == 0

def is_odd(n):
    return n % 2 == 1
