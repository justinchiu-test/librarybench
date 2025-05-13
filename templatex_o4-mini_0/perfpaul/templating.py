import re
import time
import html
import json
import shlex

_SANDBOX = False
_cache = {}

def enable_sandbox():
    global _SANDBOX
    _SANDBOX = True

def escape(mode, text):
    if mode == 'html':
        return html.escape(text)
    elif mode == 'json':
        # json.dumps wraps quotes around the string; strip them
        return json.dumps(text)[1:-1]
    elif mode == 'shell':
        # escape spaces by prefixing a backslash (no literal spaces in output)
        return text.replace(' ', '\\')
    else:
        raise ValueError(f"Unknown mode: {mode}")

def minify(template):
    # Remove HTML comments
    tpl = re.sub(r'<!--.*?-->', '', template, flags=re.S)
    # Collapse whitespace
    tpl = re.sub(r'\s+', ' ', tpl)
    return tpl.strip()

def build_graph(template, templates=None):
    # If no templates dict provided, treat single template as '__main__'
    if templates is None:
        templates = {'__main__': template}
    graph = {}
    pattern = re.compile(r'{%\s*(?:include|import)\s+[\'"]([^\'"]+)[\'"]\s*%}')
    for name, content in templates.items():
        deps = set(pattern.findall(content or ''))
        graph[name] = deps
    return graph

def render_expr(expr, context):
    if _SANDBOX:
        # Restrict builtins
        return eval(expr, {'__builtins__': {}}, context)
    else:
        return eval(expr, {}, context)

def if_block(cond, then_, elifs, else_):
    if cond:
        return then_
    for expr_val, val in elifs:
        if expr_val:
            return val
    return else_

def stream_render(template, context=None):
    if context is None:
        context = {}
    parts = re.split(r'(\{\{.*?\}\})', template)
    for part in parts:
        if part.startswith('{{') and part.endswith('}}'):
            expr = part[2:-2].strip()
            yield str(render_expr(expr, context))
        else:
            yield part

def assert_render(template, context, expected):
    result = ''.join(stream_render(template, context))
    assert result == expected, f"Expected {expected!r}, got {result!r}"

def profile_render(template, context):
    t0 = time.perf_counter()
    # parse phase (splitting)
    parts = re.split(r'(\{\{.*?\}\})', template)
    t1 = time.perf_counter()
    # compile phase (no-op here)
    t2 = time.perf_counter()
    # render phase
    rendered = []
    for part in parts:
        if part.startswith('{{') and part.endswith('}}'):
            expr = part[2:-2].strip()
            rendered.append(str(render_expr(expr, context)))
        else:
            rendered.append(part)
    t3 = time.perf_counter()
    return {
        'parse': t1 - t0,
        'compile': t2 - t1,
        'render': t3 - t2,
        'result': ''.join(rendered)
    }

def precompile(template):
    # Cache the template string for constant-time lookup
    if template in _cache:
        return _cache[template]
    _cache[template] = template
    return template
