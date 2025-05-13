import threading
import asyncio
import json
# Attempt to import PyYAML; if unavailable, fall back to JSON
try:
    import yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False
import urllib.parse
import re

_macros = {}
_output_mode = 'escape'
_locale = 'en'

class ReloadMonitor:
    def __init__(self, path, callback):
        self.path = path
        self.callback = callback

    def start(self):
        pass

    def stop(self):
        pass

def auto_reload(path, callback):
    return ReloadMonitor(path, callback)

def define_macro(name, func):
    _macros[name] = func

def precompile_templates(templates):
    compiled = {}
    for name, tpl in templates.items():
        compiled[name] = f"Compiled:{tpl}"
    return compiled

def set_output_mode(mode):
    global _output_mode
    if mode not in ('escape', 'raw'):
        raise ValueError(f"Invalid mode: {mode}")
    _output_mode = mode

def url_encode(params):
    if isinstance(params, str):
        return urllib.parse.quote_plus(params)
    items = []
    for k, v in params.items():
        items.append(f"{urllib.parse.quote_plus(str(k))}={urllib.parse.quote_plus(str(v))}")
    return "&".join(items)

def url_decode(s):
    if isinstance(s, dict):
        return s
    parsed = urllib.parse.parse_qs(s, keep_blank_values=True)
    # parse_qs decodes '+' to space and percent-escapes
    return {k: v[0] for k, v in parsed.items()}

def querystring(base, params):
    qs = url_encode(params)
    sep = '&' if '?' in base else '?'
    return f"{base}{sep}{qs}"

def to_json(obj):
    return json.dumps(obj)

def from_json(s):
    return json.loads(s)

def to_yaml(obj):
    """
    If PyYAML is available, produce a YAML string,
    otherwise fall back to JSON.
    """
    if _HAS_YAML:
        return yaml.safe_dump(obj)
    else:
        return json.dumps(obj)

def from_yaml(s):
    """
    If PyYAML is available, parse YAML,
    otherwise parse JSON.
    """
    if _HAS_YAML:
        return yaml.safe_load(s)
    else:
        return json.loads(s)

def trim_whitespace(s):
    # collapse whitespace between tags and trim ends
    s = re.sub(r'>\s+<', '><', s)
    return s.strip()

def render_threadsafe(func):
    lock = threading.Lock()
    def wrapper(*args, **kwargs):
        with lock:
            return func(*args, **kwargs)
    wrapper._lock = lock
    return wrapper

def render_async(func):
    async def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def set_locale(locale):
    global _locale
    _locale = locale

def trans(text):
    return f"{{% trans %}}{text}{{% endtrans %}}"

def render_to_string(template, context=None):
    if context is None:
        context = {}
    # Expand macro calls without args: {{ name() }}
    def macro_sub(match):
        name = match.group(1)
        if name in _macros:
            return str(_macros[name]())
        return match.group(0)
    s = re.sub(r'\{\{\s*(\w+)\(\)\s*\}\}', macro_sub, template)
    # Expand variables: {{ var }}
    def var_sub(match):
        var = match.group(1)
        return str(context.get(var, ''))
    s = re.sub(r'\{\{\s*(\w+)\s*\}\}', var_sub, s)
    return s

def render_to_file(template, filepath, context=None):
    content = render_to_string(template, context)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return filepath
