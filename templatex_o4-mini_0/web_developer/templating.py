import re
import html
import json
import shlex
import time
import os

class TemplateEngine:
    def __init__(self, template_dir='templates'):
        self.template_dir = template_dir
        self.filters = {}
        self.enable_sandbox = False
        self._cache = {}
        # register built-in filters
        self.add_filter('escape_html', self.escape_html)
        self.add_filter('escape_json', self.escape_json)
        self.add_filter('escape_shell', self.escape_shell)
        self.add_filter('default', self.default_filter)

    def enable_sandbox_mode(self):
        self.enable_sandbox = True

    def add_filter(self, name, func):
        self.filters[name] = func

    def cache_template(self, template_name):
        # just ensure it's compiled
        self._compile(template_name)

    def render(self, template_name, context=None, minify=False):
        context = context or {}
        output = ''.join(self.render_stream(template_name, context))
        if minify:
            output = self.minify_html(output)
        return output

    def render_stream(self, template_name, context=None):
        context = context or {}
        segments = self._compile(template_name)
        for seg in segments:
            if seg[0] == 'text':
                yield seg[1]
            elif seg[0] == 'expr':
                var_name, filters = seg[1], seg[2]
                value = self.dot_lookup(context, var_name)
                for fname, fargs in filters:
                    fn = self.filters.get(fname)
                    if not fn:
                        continue
                    # apply filter
                    if fargs:
                        value = fn(value, *fargs)
                    else:
                        value = fn(value)
                # convert to string
                yield '' if value is None else str(value)

    def profile_render(self, template_name, context=None, minify=False):
        context = context or {}
        start_parse = time.perf_counter()
        # parse & compile
        segments = self._compile(template_name)
        end_compile = time.perf_counter()
        # render
        parts = []
        start_render = time.perf_counter()
        for part in self.render_stream(template_name, context):
            parts.append(part)
        end_render = time.perf_counter()
        output = ''.join(parts)
        if minify:
            output = self.minify_html(output)
        return {
            'parse_compile_time': end_compile - start_parse,
            'render_time': end_render - start_render,
            'output': output
        }

    def escape_html(self, value):
        if value is None:
            return ''
        return html.escape(str(value), quote=True)

    def escape_json(self, value):
        return json.dumps(value)

    def escape_shell(self, value):
        return shlex.quote(str(value))

    def dot_lookup(self, context, path):
        parts = path.split('.')
        current = context
        for p in parts:
            try:
                if isinstance(current, dict):
                    current = current.get(p)
                else:
                    current = getattr(current, p, None)
            except Exception:
                return None
            if current is None:
                return None
        return current

    def default_filter(self, value, default_val):
        return value if value is not None else default_val

    def minify_html(self, output):
        # strip comments
        output = re.sub(r'<!--.*?-->', '', output, flags=re.DOTALL)
        # collapse whitespace
        output = re.sub(r'>\s+<', '><', output)
        output = re.sub(r'\s+', ' ', output)
        return output.strip()

    def _compile(self, template_name):
        if template_name in self._cache:
            return self._cache[template_name]
        path = os.path.join(self.template_dir, template_name)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        tokens = []
        pattern = re.compile(r'(\{\{.*?\}\}|\{%\s*include\s+\'(.*?)\'\s*%\})', re.DOTALL)
        pos = 0
        for m in pattern.finditer(content):
            start, end = m.start(), m.end()
            if start > pos:
                tokens.append(('text', content[pos:start]))
            token = m.group(1)
            include_name = m.group(2)
            if token.startswith('{%') and include_name:
                # include
                subtokens = self._compile(include_name)
                tokens.extend(subtokens)
            else:
                # expression
                expr = token[2:-2].strip()
                parts = [p.strip() for p in expr.split('|')]
                var = parts[0]
                filters = []
                for f in parts[1:]:
                    if '(' in f and f.endswith(')'):
                        fname, args = f[:-1].split('(', 1)
                        # strip quotes
                        arg = args.strip()
                        if (arg.startswith('"') and arg.endswith('"')) or (arg.startswith("'") and arg.endswith("'")):
                            arg = arg[1:-1]
                        filters.append((fname, [arg]))
                    else:
                        filters.append((f, []))
                tokens.append(('expr', var, filters))
            pos = end
        if pos < len(content):
            tokens.append(('text', content[pos:]))
        self._cache[template_name] = tokens
        return tokens
