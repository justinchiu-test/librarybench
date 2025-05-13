import os
import hashlib
import shlex
import time
import re

from jinja2.exceptions import TemplateNotFound

class SimpleTemplate:
    """
    Minimal template that supports:
      - {{ expr }} with pipe-style filters
      - {% for var in iterable %} ... {% endfor %}
    """
    _tag_re = re.compile(r'(\{\{.*?\}\}|\{%.*?%\})', re.DOTALL)

    def __init__(self, engine, text):
        self.engine = engine
        self.text = text
        self.tokens = self._parse(text)

    def _parse(self, text):
        parts = self._tag_re.split(text)
        tokens = []
        for part in parts:
            if not part:
                continue
            if part.startswith('{{') and part.endswith('}}'):
                expr = part[2:-2].strip()
                tokens.append(('expr', expr))
            elif part.startswith('{%') and part.endswith('%}'):
                content = part[2:-2].strip()
                if content.startswith('for '):
                    # expect: for <var> in <iterable>
                    words = content.split()
                    if len(words) >= 4 and words[0] == 'for' and words[2] == 'in':
                        var = words[1]
                        iterable = ' '.join(words[3:])
                        tokens.append(('for', var, iterable))
                elif content == 'endfor':
                    tokens.append(('endfor',))
                # ignore other statements
            else:
                tokens.append(('text', part))
        return tokens

    def _eval_expr(self, expr, ctx):
        # split off filters
        parts = [p.strip() for p in expr.split('|')]
        base = parts[0]
        # prepare a merged namespace of globals then context
        merged = {}
        merged.update(self.engine.globals)
        merged.update(ctx)
        # sandbox builtins
        try:
            val = eval(base, {"__builtins__": {}}, merged)
        except Exception:
            val = ''
        # apply each filter in sequence
        for filt in parts[1:]:
            if '(' in filt and filt.endswith(')'):
                fname, argstr = filt.split('(', 1)
                fname = fname.strip()
                argstr = argstr[:-1]  # drop trailing ')'
                # very simplistic: single argument only
                try:
                    arg_val = eval(argstr, {"__builtins__": {}}, merged)
                except Exception:
                    arg_val = None
                args = [arg_val]
            else:
                fname = filt
                args = []
            func = self.engine.filters.get(fname)
            if func:
                try:
                    val = func(val, *args)
                except Exception:
                    # swallow filter errors
                    pass
        return val

    def _render_tokens(self, tokens, ctx):
        out = []
        i = 0
        n = len(tokens)
        while i < n:
            tok = tokens[i]
            kind = tok[0]
            if kind == 'text':
                out.append(tok[1])
            elif kind == 'expr':
                v = self._eval_expr(tok[1], ctx)
                out.append(str(v))
            elif kind == 'for':
                _, var, iterable_expr = tok
                # find matching endfor
                depth = 1
                j = i + 1
                inner = []
                while j < n:
                    t2 = tokens[j]
                    if t2[0] == 'for':
                        depth += 1
                    elif t2[0] == 'endfor':
                        depth -= 1
                        if depth == 0:
                            break
                    if depth >= 1:
                        inner.append(t2)
                    j += 1
                # evaluate iterable
                merged = {}
                merged.update(self.engine.globals)
                merged.update(ctx)
                try:
                    iterable = eval(iterable_expr, {"__builtins__": {}}, merged)
                except Exception:
                    iterable = []
                # iterate
                for item in iterable:
                    new_ctx = ctx.copy()
                    new_ctx[var] = item
                    out.extend(self._render_tokens(inner, new_ctx))
                i = j  # skip to endfor
            # endfor or unrecognized statements are no-ops
            i += 1
        return out

    def render(self, **ctx):
        return ''.join(self._render_tokens(self.tokens, ctx))

    def generate(self, **ctx):
        for piece in self._render_tokens(self.tokens, ctx):
            yield piece


class TemplateEngine:
    def __init__(self, searchpath='.'):
        self.searchpath = searchpath
        # make sure cache dir exists
        self.cache_dir = os.path.join(self.searchpath, '.template_cache')
        os.makedirs(self.cache_dir, exist_ok=True)
        # filters and globals
        self.filters = {}
        self.globals = {}
        # register built-in filters
        self.filters['default'] = self.default_filter
        self.filters['escape_shell'] = self.escape_shell
        # register globals
        self.globals['dot_lookup'] = self.dot_lookup
        self.globals['minify'] = self.minify
        # include needs to know the current context at render time
        self._current_ctx = {}
        self.globals['include'] = self._make_include()
        # allow built-in range in templates (for loops, etc.)
        self.globals['range'] = range
        # for compatibility with tests that do engine.env.from_string(...)
        self.env = self

    def _make_include(self):
        def _include(name):
            tpl = self.cache_template(name)
            # render with the current outer context
            return tpl.render(**self._current_ctx)
        return _include

    def from_string(self, text):
        return SimpleTemplate(self, text)

    def cache_template(self, path):
        full = os.path.join(self.searchpath, path)
        if not os.path.isfile(full):
            raise TemplateNotFound(path)
        text = open(full, 'r', encoding='utf-8').read()
        # compute a hash key (to mimic original intent)
        key = hashlib.sha256(text.encode('utf-8')).hexdigest()
        # touch a cache filename (we do not actually pickle)
        cf = os.path.join(self.cache_dir, key + '.tpl')
        # ensure directory exists
        try:
            with open(cf, 'a'):
                pass
        except Exception:
            pass
        # return a fresh SimpleTemplate each time
        return SimpleTemplate(self, text)

    def render(self, path, ctx):
        self._current_ctx = ctx.copy()
        tpl = self.cache_template(path)
        return tpl.render(**ctx)

    def render_stream(self, path, ctx):
        self._current_ctx = ctx.copy()
        tpl = self.cache_template(path)
        return tpl.generate(**ctx)

    def escape_shell(self, value):
        return shlex.quote(str(value))

    def dot_lookup(self, ctx, key):
        parts = key.split('.')
        cur = ctx
        for p in parts:
            if isinstance(cur, dict) and p in cur:
                cur = cur[p]
            else:
                raise KeyError(f'Key "{p}" not found in context')
        return cur

    def minify(self, output):
        lines = output.splitlines()
        new = []
        for L in lines:
            s = L.strip()
            if not s or s.startswith('#'):
                continue
            new.append(s)
        return '\n'.join(new)

    def default_filter(self, value, default):
        if value is None or (isinstance(value, str) and value == ''):
            return default
        return value

    def add_filter(self, name, func):
        self.filters[name] = func

    def profile_render(self, path, ctx):
        start = time.time()
        rendered = self.render(path, ctx)
        elapsed = time.time() - start
        return {'rendered': rendered, 'time': elapsed}


# Singleton instance
engine = TemplateEngine()
