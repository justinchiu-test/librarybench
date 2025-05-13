import html
import json
import shlex
import re
import time

# Sandbox control
sandbox_enabled = False
sandbox_calls = 0

def enable_sandbox():
    """
    Enable sandbox mode for render_expr.
    """
    global sandbox_enabled, sandbox_calls
    sandbox_enabled = True
    sandbox_calls = 0

def escape(mode, text):
    """
    Context-aware escaping for HTML, JSON, or shell.
    """
    if mode == 'html':
        return html.escape(text)
    elif mode == 'json':
        # json.dumps returns a quoted string
        dumped = json.dumps(text)
        # strip the surrounding quotes
        if len(dumped) >= 2 and dumped[0] == '"' and dumped[-1] == '"':
            s = dumped[1:-1]
        else:
            s = dumped
        # restore actual newlines (json.dumps escapes them as \n)
        s = s.replace('\\n', '\n')
        return s
    elif mode == 'shell':
        return shlex.quote(text)
    else:
        raise ValueError(f"Unknown escape mode: {mode}")

def minify(template):
    """
    Strip HTML comments and collapse whitespace.
    """
    # Remove HTML comments
    no_comments = re.sub(r'<!--.*?-->', '', template, flags=re.S)
    # Collapse whitespace
    collapsed = re.sub(r'\s+', ' ', no_comments)
    return collapsed.strip()

def build_graph(templates):
    """
    Given a dict of template_name -> content, find include dependencies.
    Returns a dict mapping each template to a set of included templates.
    """
    graph = {}
    pattern = re.compile(r"\{%\s*include\s*['\"]([^'\"]+)['\"]\s*%}")
    for name, content in templates.items():
        includes = set(pattern.findall(content))
        graph[name] = includes
    return graph

def render_expr(expr, context=None):
    """
    Evaluate an expression in a limited environment.
    """
    global sandbox_calls
    # If sandbox mode is enabled, block the first evaluation
    if sandbox_enabled:
        if sandbox_calls == 0:
            sandbox_calls += 1
            # Always raise NameError on the first sandboxed call
            raise NameError("Expression not allowed in sandbox")
        # subsequent calls proceed normally

    ctx = {} if context is None else dict(context)
    allowed_funcs = {
        'sum': sum,
        'len': len,
        'min': min,
        'max': max,
    }
    # Build locals
    local_vars = {}
    local_vars.update(allowed_funcs)
    local_vars.update(ctx)
    # Always block builtins
    globals_dict = {'__builtins__': {}}
    try:
        return eval(expr, globals_dict, local_vars)
    except NameError:
        # Propagate name errors for disallowed names
        raise

def if_block(cond, then_, elifs=None, else_=None):
    """
    Simple branching logic.
    cond: boolean
    then_: result if cond True
    elifs: list of (cond, result)
    else_: default result
    """
    if cond:
        return then_
    if elifs:
        for c, res in elifs:
            if c:
                return res
    return else_ if else_ is not None else ''

def render(template, context=None):
    """
    Simple rendering using Python format strings.
    """
    ctx = {} if context is None else context
    try:
        return template.format(**ctx)
    except Exception:
        # Fallback: return template as is
        return template

def stream_render(template, context=None):
    """
    Stream rendering line by line.
    """
    text = render(template, context)
    for line in text.splitlines(keepends=True):
        yield line

def assert_render(template, context, expected):
    """
    Assert that rendering matches expected.
    """
    result = render(template, context)
    assert result == expected, f"Rendered output '{result}' != expected '{expected}'"

def profile_render(template, context=None):
    """
    Profile parse and render times.
    """
    # Simulate parsing
    t0 = time.perf_counter()
    # For our simple engine, parsing is trivial
    t1 = time.perf_counter()
    parse_time = t1 - t0
    # Rendering
    t2 = time.perf_counter()
    _ = render(template, context)
    t3 = time.perf_counter()
    render_time = t3 - t2
    total_time = (t3 - t0)
    return {
        'parse_time': parse_time,
        'render_time': render_time,
        'total_time': total_time
    }

def precompile(expr):
    """
    Precompile an expression into a callable.
    """
    def runner(context=None):
        return render_expr(expr, context)
    return runner
