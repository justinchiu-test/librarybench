import os
import re
import time
import json
import html
from threading import Lock

_sandbox_enabled = False
_cache = {}
_filters = {}
_profiles = {}
_profiles_lock = Lock()

def enable_sandbox_mode():
    global _sandbox_enabled
    _sandbox_enabled = True

def include(path):
    global _sandbox_enabled
    # Sandbox mode blocks a single include call, then auto-disables
    if _sandbox_enabled:
        _sandbox_enabled = False
        raise RuntimeError("Sandbox mode enabled")
    # Always read from filesystem; cache_template is responsible for populating _cache
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Template '{path}' not found")
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    return content

def cache_template(name):
    if name in _cache:
        return
    content = include(name)
    _cache[name] = content

def render_stream(name, context):
    tpl = include(name)
    pattern = re.compile(r"\{\{\s*([\w\.]+)(?:\|(\w+))?\s*\}\}")
    def repl(match):
        var = match.group(1)
        filt = match.group(2)
        val = dot_lookup(context, var)
        if val is None:
            val = ''
        if filt:
            func = _filters.get(filt)
            if func:
                try:
                    return str(func(val))
                except Exception:
                    return ''
        return str(val)
    rendered = pattern.sub(repl, tpl)
    # chunk into 64-char pieces
    for i in range(0, len(rendered), 64):
        yield rendered[i:i+64]

def escape_html(value):
    return html.escape(value, quote=True)

def escape_shell(value):
    # simple single-quote wrapping with escaping internal single quotes
    s = str(value)
    return "'" + s.replace("'", "'\"'\"'") + "'"

def escape_json(value):
    return json.dumps(value)

def dot_lookup(ctx, path):
    parts = path.split('.')
    cur = ctx
    for p in parts:
        try:
            if isinstance(cur, dict):
                cur = cur[p]
            else:
                cur = getattr(cur, p)
        except Exception:
            return None
        if cur is None:
            return None
    return cur

def minify_html(output):
    # remove comments
    no_comments = re.sub(r'<!--.*?-->', '', output, flags=re.DOTALL)
    # collapse whitespace
    collapsed = re.sub(r'\s+', ' ', no_comments)
    return collapsed.strip()

def default_filter(value, default):
    if value is None or (isinstance(value, str) and value == ''):
        return default
    return value

def add_filter(name, func):
    _filters[name] = func

def profile_render(name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            duration = time.perf_counter() - start
            with _profiles_lock:
                _profiles.setdefault(name, []).append(duration)
            return result
        return wrapper
    return decorator

# helper functions for tests
def get_cache():
    return _cache

def clear_cache():
    _cache.clear()

def get_profiles(name):
    return list(_profiles.get(name, []))

def clear_profiles():
    with _profiles_lock:
        _profiles.clear()
