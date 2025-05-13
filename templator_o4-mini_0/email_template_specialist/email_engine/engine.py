import os
import threading
import asyncio
import urllib.parse
import json
import re
import ast
import html

# Minimal loader for filesystem templates
class FileSystemLoader:
    def __init__(self, searchpath):
        self.searchpath = searchpath

    def load(self, name):
        path = os.path.join(self.searchpath, name)
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

# Minimal template and environment implementation
class Environment:
    def __init__(self, loader, autoescape):
        self.loader = loader
        # autoescape flag applies only to file-based templates
        self.autoescape = bool(autoescape)
        self.auto_reload = True
        self.filters = {}
        self.globals = {}

    def from_string(self, template_str):
        return Template(template_str, self, is_file=False)

    def get_template(self, name):
        content = self.loader.load(name)
        return Template(content, self, is_file=True)

    def compile_templates(self, target, zip=False):
        # emulate compilation by emitting a .py file per template
        base = self.loader.searchpath
        for fn in os.listdir(base):
            src_path = os.path.join(base, fn)
            if os.path.isfile(src_path):
                out_name = fn + '.py'
                out_path = os.path.join(target, out_name)
                with open(out_path, 'w', encoding='utf-8') as f:
                    f.write('# compiled template stub\n')

class Template:
    _expr = re.compile(r'\{\{\s*(.*?)\s*\}\}')

    def __init__(self, src, env, is_file=False):
        self.src = src
        self.env = env
        self.is_file = is_file
        # module stub for macros
        self.module = type('Module', (), {})()

    def render(self, **context):
        def _repl(match):
            expr = match.group(1)
            val = self._eval(expr, context)
            text = '' if val is None else str(val)
            # only escape for file-based templates when autoescape is True
            if self.is_file and self.env.autoescape:
                text = html.escape(text)
            return text
        return self._expr.sub(_repl, self.src)

    def _eval(self, expr, context):
        parts = [p.strip() for p in expr.split('|')]
        first = parts[0]
        # function call?
        m = re.match(r'^(\w+)\s*\(\s*(.*)\s*\)$', first)
        if m:
            name, args_str = m.group(1), m.group(2)
            kwargs = {}
            if args_str:
                # simple split on commas
                for part in args_str.split(','):
                    key, val = part.split('=', 1)
                    key = key.strip()
                    raw = val.strip()
                    try:
                        parsed = ast.literal_eval(raw)
                    except Exception:
                        # fallback to context lookup
                        parsed = context.get(raw)
                    kwargs[key] = parsed
            func = self.env.globals.get(name)
            base = func(**kwargs) if callable(func) else ''
        else:
            # literal?
            try:
                base = ast.literal_eval(first)
            except Exception:
                # variable, global, or bracket lookup
                # support simple bracket lookup like var["key"] or var['key']
                br = re.match(r'^(\w+)\[(?:\'([^\']*)\'|"([^"]*)")\]$', first)
                if br:
                    var = br.group(1)
                    key = br.group(2) if br.group(2) is not None else br.group(3)
                    try:
                        base = context.get(var, {})[key]
                    except Exception:
                        base = ''
                elif first in context:
                    base = context[first]
                elif first in self.env.globals:
                    base = self.env.globals[first]
                else:
                    base = ''
        # apply filters
        for fname in parts[1:]:
            fn = self.env.filters.get(fname)
            if callable(fn):
                # most filters take a single argument
                base = fn(base)
        return base

class EmailTemplateEngine:
    def __init__(self, template_dir='templates'):
        self.template_dir = template_dir
        self._lock = threading.Lock()
        # loader and env
        loader = FileSystemLoader(self.template_dir)
        # default autoescape off for string templates; file templates check this flag
        self.env = Environment(loader, autoescape=False)
        self.locale = 'en'
        # register filters
        self.env.filters.update({
            'url_encode': self.url_encode,
            'url_decode': self.url_decode,
            'querystring': self.querystring,
            'to_json': self.to_json,
            'from_json': self.from_json,
            'to_yaml': self.to_yaml,
            'from_yaml': self.from_yaml,
            'trim_whitespace': self.trim_whitespace,
        })
        # register globals
        self.env.globals.update({
            'trans': self.trans,
        })

    def auto_reload(self, flag=True):
        self.env.auto_reload = bool(flag)

    def define_macro(self, name, template_str):
        # define a macro that renders the given template_str with kwargs context
        def macro_fn(**kwargs):
            tmpl = Template(template_str, self.env, is_file=False)
            # inside macro, provide a 'kwargs' variable
            return tmpl.render(kwargs=kwargs)
        self.env.globals[name] = macro_fn

    def precompile_templates(self, target):
        os.makedirs(target, exist_ok=True)
        # emit individual .py files
        self.env.compile_templates(target, zip=False)

    def set_output_mode(self, mode):
        if mode == 'html':
            # enable escaping for file templates
            self.env.autoescape = True
        else:
            # raw
            self.env.autoescape = False

    def url_encode(self, s):
        return urllib.parse.quote_plus(s)

    def url_decode(self, s):
        return urllib.parse.unquote_plus(s)

    def querystring(self, obj=None, **params):
        if isinstance(obj, dict) and not params:
            return urllib.parse.urlencode(obj)
        return urllib.parse.urlencode(params)

    def to_json(self, obj):
        return json.dumps(obj)

    def from_json(self, s):
        return json.loads(s)

    def to_yaml(self, obj):
        import yaml
        return yaml.dump(obj)

    def from_yaml(self, s):
        import yaml
        return yaml.safe_load(s)

    def trim_whitespace(self, s):
        text = s.strip()
        return re.sub(r'\n\s*\n', '\n', text)

    def render_threadsafe(self, template_name, context):
        with self._lock:
            tmpl = self.env.get_template(template_name)
            return tmpl.render(**context)

    async def render_async(self, template_name, context):
        # use the running loop to dispatch to an executor
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, self.render_threadsafe, template_name, context
        )

    def set_locale(self, locale):
        self.locale = locale

    def trans(self, text):
        return f"[{self.locale}]{text}"

    def render_to_string(self, template_name, context):
        return self.render_threadsafe(template_name, context)

    def render_to_file(self, template_name, context, path):
        content = self.render_to_string(template_name, context)
        dirpath = os.path.dirname(path)
        if dirpath:
            os.makedirs(dirpath, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return path
