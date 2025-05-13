import time
import re
import json
import html
import ast
from markupsafe import Markup

class Template:
    def __init__(self, engine, snippet):
        self.engine = engine
        self.snippet = snippet

    def render(self, **ctx):
        # Render fully by joining streamed chunks
        return ''.join(self.generate(**ctx))

    def generate(self, **ctx):
        # Streamed rendering
        return self.engine._generate(self.snippet, ctx or {})

class SafeTemplateEngine:
    def __init__(self):
        self._cache = {}
        self._custom_filters = {}
        self.sandbox = False
        # Setup environment
        self._create_env()

    def _create_env(self):
        # env is self; filters stored in env.filters
        self.env = self
        # Build filters dict: custom plus default
        self.env.filters = dict(self._custom_filters)
        self.env.filters['default'] = self.default_filter

    def enable_sandbox_mode(self):
        self.sandbox = True

    def include(self, policy_snippet):
        # Securely embed policy fragments
        return Markup(policy_snippet)

    def cache_template(self, policy_snippet):
        # Cache audited templates
        if policy_snippet not in self._cache:
            tpl = self.from_string(policy_snippet)
            self._cache[policy_snippet] = tpl
        return self._cache[policy_snippet]

    def render_stream(self, policy_snippet, ctx=None):
        # Stream logs or dumps without full buffering
        # Sandbox: block imports
        if self.sandbox and "__import__" in policy_snippet:
            raise Exception("Import not allowed in sandbox")
        tpl = self.from_string(policy_snippet)
        for chunk in tpl.generate(**(ctx or {})):
            yield chunk

    def escape_html(self, value):
        return html.escape(str(value), quote=True)

    def escape_json(self, value):
        try:
            return json.dumps(value)
        except Exception:
            return json.dumps(str(value))

    def escape_shell(self, value):
        s = str(value)
        # simple single-quote wrapping
        return "'" + s.replace("'", "'\"'\"'") + "'"

    def dot_lookup(self, ctx, path):
        parts = path.split('.')
        current = ctx
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                current = getattr(current, part, None)
            if current is None:
                break
        return current

    def minify(self, output):
        # remove HTML comments
        out = re.sub(r'<!--.*?-->', '', output, flags=re.DOTALL)
        # remove JS multi-line comments
        out = re.sub(r'/\*[\s\S]*?\*/', '', out)
        # remove JS single-line comments
        out = re.sub(r'//.*', '', out)
        # collapse whitespace
        out = re.sub(r'\s+', ' ', out)
        return out.strip()

    def default_filter(self, value, default_value=''):
        if value is None or (hasattr(value, '__len__') and len(value) == 0):
            return default_value
        return value

    def add_filter(self, name, func):
        self._custom_filters[name] = func
        if hasattr(self, 'env') and hasattr(self.env, 'filters'):
            self.env.filters[name] = func

    def profile_render(self, policy_snippet, ctx=None):
        ctx = ctx or {}
        # parse
        t0 = time.time()
        self.env.parse(policy_snippet)
        t1 = time.time()
        # compile
        template = self.env.from_string(policy_snippet)
        t2 = time.time()
        # render
        output = template.render(**ctx)
        t3 = time.time()
        return {
            'parse_time': t1 - t0,
            'compile_time': t2 - t1,
            'render_time': t3 - t2,
            'output': output
        }

    # Methods to satisfy env interface
    def parse(self, snippet):
        # Dummy parse
        return snippet

    def from_string(self, snippet):
        return Template(self, snippet)

    # Internal evaluation and generation
    def _generate(self, text, ctx):
        pos = 0
        length = len(text)
        while pos < length:
            # Find next tag
            idx_expr = text.find("{{", pos)
            idx_stmt = text.find("{%", pos)
            if idx_expr == -1 and idx_stmt == -1:
                # No more tags
                yield text[pos:]
                break
            # Choose earliest
            if idx_expr == -1 or (idx_stmt != -1 and idx_stmt < idx_expr):
                idx = idx_stmt
                tag_type = "{%"
            else:
                idx = idx_expr
                tag_type = "{{"
            # Yield text before tag
            if idx > pos:
                yield text[pos:idx]
            if tag_type == "{{":
                end_idx = text.find("}}", idx)
                if end_idx == -1:
                    # No close; yield rest
                    yield text[idx:]
                    break
                expr = text[idx+2:end_idx].strip()
                val = self._eval_expr(expr, ctx)
                yield str(val)
                pos = end_idx + 2
            else:  # tag_type == "{%"
                end_idx = text.find("%}", idx)
                if end_idx == -1:
                    yield text[idx:]
                    break
                tag = text[idx+2:end_idx].strip()
                if tag.startswith("for "):
                    # parse for var in iterable
                    m = re.match(r'for\s+(\w+)\s+in\s+(.+)', tag)
                    if not m:
                        pos = end_idx + 2
                        continue
                    var, iterable_expr = m.group(1), m.group(2).strip()
                    # find matching endfor
                    end_tag = "{% endfor %}"
                    body_start = end_idx + 2
                    endfor_idx = text.find(end_tag, body_start)
                    if endfor_idx == -1:
                        pos = body_start
                        continue
                    body = text[body_start:endfor_idx]
                    # evaluate iterable
                    try:
                        iterable = ast.literal_eval(iterable_expr)
                    except Exception:
                        iterable = self.dot_lookup(ctx, iterable_expr) or []
                    for item in iterable:
                        new_ctx = dict(ctx)
                        new_ctx[var] = item
                        for chunk in self._generate(body, new_ctx):
                            yield chunk
                    pos = endfor_idx + len(end_tag)
                else:
                    # skip unknown tags
                    pos = end_idx + 2
        # done

    def _eval_expr(self, expr, ctx):
        # Sandbox: block imports
        if self.sandbox and "__import__" in expr:
            raise Exception("Import not allowed in sandbox")
        # Filter support
        if "|" in expr:
            left, filt = expr.split("|", 1)
            val = self._eval_expr(left.strip(), ctx)
            filt = filt.strip()
            func = self.env.filters.get(filt)
            if callable(func):
                try:
                    return func(val)
                except TypeError:
                    # filter may expect other signature; try with two args
                    return func(val, '')
            return val
        # Try literal
        try:
            return ast.literal_eval(expr)
        except Exception:
            # Fallback to lookup
            val = self.dot_lookup(ctx, expr)
            if val is None:
                return ''
            return val
