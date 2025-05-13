import html
import json
import shlex
import re
import ast
import time

# Global state
_sandbox_enabled = False
_precompile_cache = {}

def escape(mode, text):
    if mode == 'html':
        return html.escape(text)
    elif mode == 'json':
        return json.dumps(text)
    elif mode == 'shell':
        return shlex.quote(text)
    else:
        raise ValueError(f"Unknown escape mode: {mode}")

def minify(template):
    # Remove HTML comments
    no_comments = re.sub(r'<!--.*?-->', '', template, flags=re.DOTALL)
    # Collapse whitespace
    collapsed = re.sub(r'\s+', ' ', no_comments)
    return collapsed.strip()

def build_graph():
    # Placeholder: no templates to analyze
    return {}

def render_expr(expr):
    # Parse expression
    try:
        tree = ast.parse(expr, mode='eval')
    except SyntaxError as e:
        raise ValueError("Invalid expression") from e
    # Allowed node types
    allowed_nodes = (
        ast.Expression, ast.BoolOp, ast.BinOp, ast.UnaryOp,
        ast.Compare, ast.Call, ast.Name, ast.Load, ast.Constant,
        ast.And, ast.Or, ast.Add, ast.Sub, ast.Mult, ast.Div,
        ast.Mod, ast.Pow, ast.Lt, ast.Gt, ast.LtE, ast.GtE,
        ast.Eq, ast.NotEq, ast.Not, ast.USub, ast.UAdd,
        ast.List, ast.Tuple, ast.Dict, ast.ListComp, ast.comprehension
    )
    for node in ast.walk(tree):
        if not isinstance(node, allowed_nodes):
            raise ValueError(f"Disallowed expression: {type(node).__name__}")
    # Safe eval
    return eval(compile(tree, filename="<expr>", mode="eval"), {}, {})

def if_block(cond, then_, elifs, else_):
    if cond:
        return then_
    for c, val in elifs:
        if c:
            return val
    return else_

def _render(template, context):
    # Handle expressions {{ expr }}
    def _replace_expr(match):
        expr = match.group(1).strip()
        try:
            return str(eval(expr, {}, context))
        except Exception:
            # Fallback to safe render_expr for literals
            return str(render_expr(expr))
    rendered = re.sub(r'{{\s*(.*?)\s*}}', _replace_expr, template)
    # Note: {% if %} blocks not fully supported here
    return rendered

def stream_render(template, context=None):
    if context is None:
        context = {}
    output = _render(template, context)
    # Simple streaming: yield whole output once
    yield output

def assert_render(template, context, expected):
    result = _render(template, context)
    assert result == expected, f"Render output '{result}' != expected '{expected}'"

def profile_render(template, context):
    # Timing parsing (dummy), compilation (dummy), rendering
    t0 = time.time()
    # parsing placeholder
    _ = template.split()
    t1 = time.time()
    # compilation placeholder
    _ = compile("pass", "<string>", "exec")
    t2 = time.time()
    # rendering
    _ = _render(template, context)
    t3 = time.time()
    return {
        'parsing': t1 - t0,
        'compilation': t2 - t1,
        'rendering': t3 - t2
    }

def enable_sandbox():
    global _sandbox_enabled
    _sandbox_enabled = True

def precompile(template):
    if template in _precompile_cache:
        return _precompile_cache[template]
    # For simplicity, store the template itself
    _precompile_cache[template] = template
    return template
