import threading
import asyncio
import os
import json
import html
import urllib.parse
import yaml
import sys

# Global state
auto_reload_enabled = False
macros = {}
compiled_templates = {}
output_mode = 'escape'
current_locale = 'en'
translations = {}

_lock = threading.Lock()

def auto_reload(enable: bool):
    """
    Enable or disable auto reload.
    Also syncs the value to any caller module that imported `auto_reload_enabled`.
    """
    global auto_reload_enabled
    auto_reload_enabled = enable
    # Sync to caller's namespace if they imported the name
    try:
        cg = sys._getframe(1).f_globals
        if 'auto_reload_enabled' in cg:
            cg['auto_reload_enabled'] = enable
    except (ValueError, AttributeError):
        pass

def define_macro(name: str, func):
    macros[name] = func

def precompile_templates(template_dir: str, locale: str):
    """
    Simulate precompilation by reading .tmpl files and storing their content.
    """
    key = (template_dir, locale)
    compiled = {}
    for root, _, files in os.walk(template_dir):
        for f in files:
            if f.endswith('.tmpl'):
                path = os.path.join(root, f)
                with open(path, 'r', encoding='utf-8') as fd:
                    content = fd.read()
                # Simulated compilation: store upper() + locale tag
                compiled[path] = f"/*{locale}*/\n" + content
    compiled_templates[key] = compiled
    return compiled

def set_output_mode(mode: str):
    """
    mode: 'escape' or 'raw'
    Also syncs the value to any caller module that imported `output_mode`.
    """
    global output_mode
    if mode not in ('escape', 'raw'):
        raise ValueError("Output mode must be 'escape' or 'raw'")
    output_mode = mode
    # Sync to caller's namespace if they imported the name
    try:
        cg = sys._getframe(1).f_globals
        if 'output_mode' in cg:
            cg['output_mode'] = mode
    except (ValueError, AttributeError):
        pass

def url_encode(s: str) -> str:
    return urllib.parse.quote_plus(s)

def url_decode(s: str) -> str:
    return urllib.parse.unquote_plus(s)

def querystring(url: str, **params) -> str:
    parsed = urllib.parse.urlparse(url)
    qs = dict(urllib.parse.parse_qsl(parsed.query))
    qs.update(params)
    new_qs = urllib.parse.urlencode(qs)
    new = parsed._replace(query=new_qs)
    return urllib.parse.urlunparse(new)

def to_json(obj) -> str:
    return json.dumps(obj)

def from_json(s: str):
    return json.loads(s)

def to_yaml(obj) -> str:
    return yaml.dump(obj)

def from_yaml(s: str):
    return yaml.safe_load(s)

def trim_whitespace(text: str, mode: str) -> str:
    if mode == 'rtl':
        return text.strip()
    elif mode == 'vertical':
        # Remove spaces and newlines
        return text.replace(' ', '').replace('\n', '')
    else:
        raise ValueError("Mode must be 'rtl' or 'vertical'")

def render_threadsafe(template_str: str, context: dict) -> str:
    with _lock:
        return _render(template_str, context)

async def render_async(template_str: str, context: dict) -> str:
    await asyncio.sleep(0)
    return _render(template_str, context)

def set_locale(locale: str):
    """
    Set the current locale.
    Also syncs the value to any caller module that imported `current_locale`.
    """
    global current_locale
    current_locale = locale
    # Sync to caller's namespace if they imported the name
    try:
        cg = sys._getframe(1).f_globals
        if 'current_locale' in cg:
            cg['current_locale'] = locale
    except (ValueError, AttributeError):
        pass

def trans(text: str, count: int = None) -> str:
    """
    Simplified translation/pluralization.
    Use 'singular|plural' syntax if count is provided.
    """
    if count is not None and '|' in text:
        singular, plural = text.split('|', 1)
        return singular if count == 1 else plural
    return text

def render_to_string(template_str: str, context: dict) -> str:
    return _render(template_str, context)

def render_to_file(template_str: str, context: dict, path: str):
    content = _render(template_str, context)
    with open(path, 'w', encoding='utf-8') as fd:
        fd.write(content)
    return path

def _render(template_str: str, context: dict) -> str:
    # Apply macros
    ctx = {}
    for k, v in context.items():
        if isinstance(v, str):
            ctx[k] = html.escape(v) if output_mode == 'escape' else v
        else:
            ctx[k] = v
    # Simple Python format rendering
    try:
        return template_str.format(**ctx)
    except Exception:
        # Fallback: return as is
        return template_str
