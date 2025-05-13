import ast
import json
import yaml
import copy
import traceback
import html
import re
from contextlib import contextmanager

# Safe evaluation
class _SafeEval(ast.NodeVisitor):
    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def visit_Module(self, node):
        if len(node.body) != 1 or not isinstance(node.body[0], ast.Expr):
            raise ValueError("Only single expressions allowed")
        return self.visit(node.body[0].value)

    def visit_Expression(self, node):
        return self.visit(node.body)

    def visit_Constant(self, node):
        return node.value

    def visit_Num(self, node):
        return node.n

    def visit_Str(self, node):
        return node.s

    def visit_NameConstant(self, node):
        return node.value

    def visit_List(self, node):
        return [self.visit(e) for e in node.elts]

    def visit_Tuple(self, node):
        return tuple(self.visit(e) for e in node.elts)

    def visit_Set(self, node):
        return set(self.visit(e) for e in node.elts)

    def visit_Dict(self, node):
        return {self.visit(k): self.visit(v) for k, v in zip(node.keys, node.values)}

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        if isinstance(node.op, ast.UAdd):
            return +operand
        if isinstance(node.op, ast.USub):
            return -operand
        if isinstance(node.op, ast.Not):
            return not operand
        raise ValueError(f"Unsupported unary op {node.op}")

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = node.op
        if isinstance(op, ast.Add):
            return left + right
        if isinstance(op, ast.Sub):
            return left - right
        if isinstance(op, ast.Mult):
            return left * right
        if isinstance(op, ast.Div):
            return left / right
        if isinstance(op, ast.FloorDiv):
            return left // right
        if isinstance(op, ast.Mod):
            return left % right
        if isinstance(op, ast.Pow):
            return left ** right
        raise ValueError(f"Unsupported binary op {op}")

    def visit_BoolOp(self, node):
        if isinstance(node.op, ast.And):
            result = True
            for v in node.values:
                result = result and self.visit(v)
                if not result:
                    break
            return result
        if isinstance(node.op, ast.Or):
            result = False
            for v in node.values:
                result = result or self.visit(v)
                if result:
                    break
            return result
        raise ValueError(f"Unsupported bool op {node.op}")

    def visit_Compare(self, node):
        left = self.visit(node.left)
        for op, comp in zip(node.ops, node.comparators):
            right = self.visit(comp)
            if isinstance(op, ast.Eq):
                ok = left == right
            elif isinstance(op, ast.NotEq):
                ok = left != right
            elif isinstance(op, ast.Lt):
                ok = left < right
            elif isinstance(op, ast.LtE):
                ok = left <= right
            elif isinstance(op, ast.Gt):
                ok = left > right
            elif isinstance(op, ast.GtE):
                ok = left >= right
            else:
                raise ValueError(f"Unsupported compare op {op}")
            if not ok:
                return False
            left = right
        return True

    def visit_Name(self, node):
        if node.id in ('True', 'False', 'None'):
            return {'True': True, 'False': False, 'None': None}[node.id]
        raise ValueError(f"Name {node.id} is not allowed")

    def generic_visit(self, node):
        raise ValueError(f"Unsupported expression {node.__class__.__name__}")

def safe_eval(expr: str):
    tree = ast.parse(expr, mode='exec')
    return _SafeEval().visit(tree)

# Scoped context
@contextmanager
def scoped_context(ctx: dict):
    backup = copy.deepcopy(ctx)
    temp = copy.deepcopy(ctx)
    yield temp
    # do not write back to ctx

# Render stream
def render_stream(data, chunk_size=1):
    if isinstance(data, str):
        data = data.encode()
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i+chunk_size]
        yield chunk

# JSON/YAML
def to_json(value):
    return json.dumps(value)

def from_json(text):
    return json.loads(text)

def to_yaml(value):
    return yaml.safe_dump(value)

def from_yaml(text):
    return yaml.safe_load(text)

# Error reporting
def report_error(code: str, e: Exception):
    tb = traceback.format_exc()
    snippet = '\n'.join(f"{i+1}: {line}" for i, line in enumerate(code.splitlines()))
    return f"{tb}\nCode Snippet:\n{snippet}"

# Autoescape/raw
ESCAPE_ENABLED = True

@contextmanager
def autoescape(on=True):
    global ESCAPE_ENABLED
    old = ESCAPE_ENABLED
    ESCAPE_ENABLED = on
    try:
        yield
    finally:
        ESCAPE_ENABLED = old

@contextmanager
def raw():
    global ESCAPE_ENABLED
    old = ESCAPE_ENABLED
    ESCAPE_ENABLED = False
    try:
        yield
    finally:
        ESCAPE_ENABLED = old

def escape(text: str):
    if ESCAPE_ENABLED:
        return html.escape(text)
    return text

# Trim tags
def trim_tags(text: str):
    return re.sub(r'>\s+<', '><', text)

# Macros and delimiters
MACROS = {}
START_DELIM = "{{"
END_DELIM = "}}"

def define_macro(name: str, template: str):
    MACROS[name] = template

def set_delimiters(start: str, end: str):
    global START_DELIM, END_DELIM
    START_DELIM = start
    END_DELIM = end

def expand_macros(text: str):
    result = text
    for name, tpl in MACROS.items():
        token = f"{START_DELIM}{name}{END_DELIM}"
        result = result.replace(token, tpl)
    return result

# Arithmetic and tests
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
    return n % 2 == 1
