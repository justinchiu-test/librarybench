import ast
import json
import yaml
from contextlib import contextmanager

class TemplateError(Exception):
    pass

def safe_eval(expr, context=None):
    node = ast.parse(expr, mode='eval')
    def _eval(n):
        if isinstance(n, ast.Expression):
            return _eval(n.body)
        if isinstance(n, ast.Constant):
            if isinstance(n.value, (int, float, str, bool, type(None))):
                return n.value
            raise ValueError(f"Unsupported constant: {n.value}")
        if isinstance(n, ast.Num):
            return n.n
        if isinstance(n, ast.Str):
            return n.s
        if isinstance(n, ast.BinOp):
            left = _eval(n.left)
            right = _eval(n.right)
            if isinstance(n.op, ast.Add):
                return left + right
            if isinstance(n.op, ast.Sub):
                return left - right
            if isinstance(n.op, ast.Mult):
                return left * right
            if isinstance(n.op, ast.Div):
                return left / right
            if isinstance(n.op, ast.Mod):
                return left % right
            if isinstance(n.op, ast.Pow):
                return left ** right
            raise ValueError(f"Unsupported operator: {n.op}")
        if isinstance(n, ast.UnaryOp):
            operand = _eval(n.operand)
            if isinstance(n.op, ast.UAdd):
                return +operand
            if isinstance(n.op, ast.USub):
                return -operand
            raise ValueError(f"Unsupported unary operator: {n.op}")
        raise ValueError(f"Unsupported expression: {n}")
    # ensure tree only contains allowed nodes
    for n in ast.walk(node):
        if not isinstance(n, (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Num, ast.Str,
                              ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow, ast.UAdd, ast.USub)):
            raise ValueError(f"Unsafe expression: {n}")
    return _eval(node)

@contextmanager
def scoped_context(context, **overrides):
    old = context.copy()
    context.update(overrides)
    try:
        yield context
    finally:
        context.clear()
        context.update(old)

delimiters = ('{{', '}}')

def set_delimiters(left, right):
    global delimiters
    delimiters = (left, right)

def render_stream(template, context):
    left, right = delimiters
    temp = template.replace(left, '{').replace(right, '}')
    rendered = temp.format(**context)
    for line in rendered.splitlines(keepends=True):
        yield line

def to_json(obj):
    return json.dumps(obj)

def from_json(s):
    return json.loads(s)

def to_yaml(obj):
    return yaml.safe_dump(obj)

def from_yaml(s):
    return yaml.safe_load(s)

def report_error(exc, file_name, line_no):
    msg = f"{file_name}:{line_no}: {str(exc)}"
    raise TemplateError(msg)

def autoescape(s):
    return (s.replace('&','&amp;')
             .replace('<','&lt;')
             .replace('>','&gt;')
             .replace('"','&quot;')
             .replace("'",'&#39;'))

def raw(s):
    return s

def trim_tags(s):
    return s.strip()

_macros = {}

def define_macro(name):
    def decorator(func):
        _macros[name] = func
        return func
    return decorator

def call_macro(name, *args, **kwargs):
    func = _macros.get(name)
    if not func:
        raise TemplateError(f"Macro '{name}' not defined")
    return func(*args, **kwargs)

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
