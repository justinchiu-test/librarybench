import shlex
import json
import html
import re
import os
import ast
import time

SANDBOX_ENABLED = False

def escape(mode, text):
    if mode == 'shell':
        return shlex.quote(text)
    elif mode == 'json':
        return json.dumps(text)
    elif mode == 'html':
        return html.escape(text)
    else:
        raise ValueError('Unknown mode')

def minify(template):
    lines = template.splitlines()
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        cleaned.append(stripped)
    return ' '.join(cleaned)

def build_graph():
    graph = {}
    for root, _, files in os.walk('.'):
        for f in files:
            if f.endswith('.tpl'):
                path = os.path.join(root, f)
                deps = []
                with open(path, 'r') as fh:
                    for line in fh:
                        m = re.search(r"{%\s*include\s*['\"](.+?)['\"]\s*%}", line)
                        if m:
                            deps.append(m.group(1))
                        m2 = re.search(r"{%\s*import\s*['\"](.+?)['\"]\s*%}", line)
                        if m2:
                            deps.append(m2.group(1))
                if deps:
                    rel = os.path.relpath(path, '.')
                    graph[rel] = deps
    return graph

def render_expr(expr):
    node = ast.parse(expr, mode='eval')
    for n in ast.walk(node):
        if isinstance(n, ast.Name):
            if n.id not in ('True', 'False', 'None'):
                raise ValueError('Unsafe expression')
        elif isinstance(n, ast.Call):
            raise ValueError('Unsafe expression')
    code = compile(node, '<expr>', 'eval')
    return eval(code, {"__builtins__": None}, {})

def if_block(cond, then_, elifs, else_):
    if render_expr(cond):
        return then_
    for c, txt in elifs:
        if render_expr(c):
            return txt
    return else_

def render(template, context):
    return template.format(**context)

def stream_render(template, context):
    rendered = render(template, context)
    for line in rendered.splitlines(keepends=True):
        yield line

def assert_render(template, context, expected):
    out = render(template, context)
    assert out == expected, f"Rendering mismatch: got {out}, expected {expected}"

def profile_render(template, context):
    times = {}
    t0 = time.time()
    _ = template
    t1 = time.time()
    times['parsing'] = t1 - t0
    _ = precompile(template)
    t2 = time.time()
    times['compilation'] = t2 - t1
    _ = render(template, context)
    t3 = time.time()
    times['rendering'] = t3 - t2
    return times

def enable_sandbox():
    global SANDBOX_ENABLED
    SANDBOX_ENABLED = True

def precompile(template):
    def fn(context):
        return render(template, context)
    return fn
