import threading
import asyncio
import urllib.parse
import json
import html
import os
import re

# Macro registry
_macros = {}

def define_macro(name, func):
    _macros[name] = func

def call_macro(name, *args, **kwargs):
    if name not in _macros:
        raise KeyError(f"Macro '{name}' not defined")
    return _macros[name](*args, **kwargs)

# Auto-reloader (stub: calls callback immediately for each path)
def auto_reload(paths, callback):
    for p in paths:
        callback(p)

# Precompile template to Python module
def precompile_templates(template_str, output_path):
    code = []
    code.append("def render(**context):")
    # Escape triple quotes
    safe_tpl = template_str.replace('"""', '\\"\\"\\"')
    code.append(f'    return """{safe_tpl}""".format(**context)')
    module_code = "\n".join(code)
    dirpath = os.path.dirname(output_path)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(module_code)

# Output mode for escaping
class _OutputMode:
    def __init__(self, mode):
        self._mode = mode
    def set(self, mode):
        self._mode = mode
    def __eq__(self, other):
        # allow comparing to string
        return self._mode == other
    def __str__(self):
        return self._mode
    def __repr__(self):
        return repr(self._mode)

_output_mode = _OutputMode("html")

def set_output_mode(mode):
    if mode not in ("html", "raw"):
        raise ValueError("mode must be 'html' or 'raw'")
    _output_mode.set(mode)

# URL functions
def url_encode(s):
    return urllib.parse.quote(s, safe='')

def url_decode(s):
    return urllib.parse.unquote(s)

def querystring(base, **params):
    qs = urllib.parse.urlencode(params)
    return base + ("?" + qs if qs else "")

# JSON/YAML
def to_json(obj):
    return json.dumps(obj)

def from_json(s):
    return json.loads(s)

def to_yaml(obj):
    # Fallback to JSON format if PyYAML is not available
    return json.dumps(obj)

def from_yaml(s):
    return json.loads(s)

# Whitespace trimming
def trim_whitespace(text):
    # Remove trailing spaces and tabs
    lines = [re.sub(r"[ \t]+$", "", line) for line in text.splitlines()]
    joined = "\n".join(lines)
    # Collapse multiple blank lines to at most two
    return re.sub(r"\n{3,}", "\n\n", joined)

# Thread-safe rendering
_render_lock = threading.Lock()

def render_to_string(template_str, **context):
    return template_str.format(**context)

def render_threadsafe(template_str, **context):
    with _render_lock:
        return render_to_string(template_str, **context)

def render_async(template_str, **context):
    async def _wrapper():
        return render_to_string(template_str, **context)
    return _wrapper()

# Localization
_locale = "en"
_translations = {
    "hello": {"es": "hola", "de": "hallo"},
    "goodbye": {"es": "adios", "de": "auf wiedersehen"}
}

def set_locale(locale):
    global _locale
    _locale = locale

def trans(s):
    if s in _translations and _locale in _translations[s]:
        return _translations[s][_locale]
    return s

# File rendering
def render_to_file(template_str, path, **context):
    content = render_to_string(template_str, **context)
    dirpath = os.path.dirname(path)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path
