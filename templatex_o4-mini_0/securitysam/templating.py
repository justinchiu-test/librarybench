import re
import os
import ast
import time
import json
import shlex
from collections import defaultdict

# Global sandbox flag and cache for precompiled templates
_SANDBOX = False
_PRECOMPILE_CACHE = {}

def enable_sandbox():
    """
    Enable strict sandbox mode: restricts eval of expressions to constants only.
    """
    global _SANDBOX
    _SANDBOX = True

def escape(mode, text):
    """
    Escape text for HTML, JSON, or shell contexts.
    """
    if mode == 'html':
        return (text.replace('&', '&amp;')
                    .replace('<', '&lt;')
                    .replace('>', '&gt;')
                    .replace('"', '&quot;')
                    .replace("'", '&#x27;'))
    elif mode == 'json':
        # json.dumps returns a JSON string literal including quotes
        return json.dumps(text)
    elif mode == 'shell':
        return shlex.quote(text)
    else:
        raise ValueError(f"Unknown escape mode: {mode}")

def minify(template):
    """
    Strip HTML comments and collapse whitespace.
    """
    no_comments = re.sub(r"<!--.*?-->", "", template, flags=re.DOTALL)
    collapsed = re.sub(r"\s+", " ", no_comments)
    return collapsed.strip()

def build_graph(template_dir="templates"):
    """
    Scan .tpl files under template_dir for include directives and build
    a dependency graph.
    """
    graph = defaultdict(list)
    pattern = re.compile(r"\{\%\s*include\s*['\"](.*?)['\"]\s*\%\}")
    for root, _, files in os.walk(template_dir):
        for fn in files:
            if fn.endswith('.tpl'):
                path = os.path.join(root, fn)
                rel = os.path.relpath(path, template_dir)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                includes = pattern.findall(content)
                graph[rel] = includes
    return dict(graph)

_SAFE_EXPR_NODES = (
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.Constant,
    ast.BoolOp, ast.Compare, ast.NameConstant, ast.Load,
    ast.operator, ast.unaryop, ast.boolop, ast.cmpop, ast.Name,
)

class _SafeVisitor(ast.NodeVisitor):
    def visit_Name(self, node):
        if _SANDBOX:
            # In sandbox, disallow any Name usage (no variables)
            raise ValueError(f"Unsafe expression: variable '{node.id}' not allowed")
        self.generic_visit(node)
    def generic_visit(self, node):
        if not isinstance(node, _SAFE_EXPR_NODES):
            raise ValueError(f"Unsafe expression node: {type(node).__name__}")
        super().generic_visit(node)

def render_expr(expr):
    """
    Safely evaluate simple Pythonic expressions: arithmetic and booleans.
    """
    try:
        tree = ast.parse(expr, mode='eval')
        _SafeVisitor().visit(tree)
        code = compile(tree, '<expr>', 'eval')
        # Restrict builtins and globals
        return eval(code, {'__builtins__': {}}, {})
    except Exception as e:
        raise ValueError(f"Error in render_expr: {e}")

def if_block(cond, then_, elifs=None, else_=None):
    """
    Build a template if-elif-else block string.
    """
    parts = [f"{{% if {cond} %}}", then_]
    if elifs:
        for c, t in elifs:
            parts.append(f"{{% elif {c} %}}")
            parts.append(t)
    if else_ is not None:
        parts.append("{% else %}")
        parts.append(else_)
    parts.append("{% endif %}")
    return "".join(parts)

def stream_render(template, context, chunk_size=10):
    """
    Stream-render a template with Python's str.format, yielding chunks.
    """
    rendered = template.format(**context)
    for i in range(0, len(rendered), chunk_size):
        yield rendered[i:i+chunk_size]

def assert_render(template, context, expected):
    """
    Assert that rendering template with context yields expected result.
    """
    result = template.format(**context)
    assert result == expected, f"Expected '{expected}', got '{result}'"

def profile_render(template, context):
    """
    Profile parse, compile, and render phases.
    """
    times = {}
    t0 = time.perf_counter()
    tree = ast.parse(template, mode='eval')
    times['parse'] = time.perf_counter() - t0

    t1 = time.perf_counter()
    code = compile(tree, '<template>', 'eval')
    times['compile'] = time.perf_counter() - t1

    t2 = time.perf_counter()
    # render via format in a safe context
    _ = eval(code, {"__builtins__": {}}, context)
    times['render'] = time.perf_counter() - t2
    return times

def precompile(template):
    """
    Precompile template string to AST and cache it.
    """
    if template in _PRECOMPILE_CACHE:
        return _PRECOMPILE_CACHE[template]
    tree = ast.parse(template, mode='eval')
    _PRECOMPILE_CACHE[template] = tree
    return tree
