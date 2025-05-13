import re
import time
import html
import json
from collections import deque

def dot_lookup(context, path):
    """
    Lookup nested values in dictionaries/lists using dot notation and brackets.
    """
    parts = re.findall(r"[^\.\[\]]+|\[\d+\]", path)
    current = context
    for part in parts:
        if part.startswith('[') and part.endswith(']'):
            idx = int(part[1:-1])
            try:
                current = current[idx]
            except Exception:
                raise KeyError(f"Index {idx} not found in {current}")
        else:
            key = part
            if isinstance(current, dict):
                if key in current:
                    current = current[key]
                else:
                    raise KeyError(f"Key '{key}' not found in {current}")
            else:
                try:
                    current = getattr(current, key)
                except Exception:
                    raise KeyError(f"Attribute '{key}' not found in {current}")
    return current

def escape_html(value):
    """
    Escape HTML special characters.
    """
    return html.escape(str(value), quote=True)

def escape_json(value):
    """
    JSON-encode a value.
    """
    return json.dumps(value)

def minify_html(output):
    """
    Remove HTML comments and collapse whitespace.
    """
    no_comments = re.sub(r"<!--.*?-->", "", output, flags=re.DOTALL)
    collapsed = re.sub(r"\s+", " ", no_comments)
    return collapsed.strip()

def default_filter(value, default):
    """
    Return value if truthy, else default.
    """
    return value if value else default

class TemplateEngine:
    def __init__(self):
        self.sandbox = False
        self.templates = {}
        self.compiled = {}
        self.filters = {
            'default': default_filter,
            'escape_html': escape_html,
            'escape_json': escape_json,
        }

    def enable_sandbox_mode(self):
        """
        Enable sandbox mode: restrict arbitrary code execution.
        """
        self.sandbox = True

    def add_filter(self, name, func):
        """
        Register a custom filter.
        """
        self.filters[name] = func

    def register_template(self, name, content):
        """
        Register a template by name.
        """
        self.templates[name] = content

    def cache_template(self, template_name):
        """
        Pre-compile and store the token list.
        """
        if template_name in self.compiled:
            return
        if template_name not in self.templates:
            raise KeyError(f"Template '{template_name}' not found")
        tokens = self._tokenize(self.templates[template_name])
        self.compiled[template_name] = tokens

    def render(self, template_name, context=None):
        """
        Render the full template to a string.
        """
        if context is None:
            context = {}
        if template_name not in self.compiled:
            self.cache_template(template_name)
        tokens = self.compiled[template_name]
        result = []
        for typ, val in tokens:
            if typ == 'text':
                result.append(val)
            elif typ == 'var':
                rendered = self._eval_var(val, context)
                result.append(str(rendered))
            elif typ == 'include':
                included = self.render(val, context)
                result.append(included)
        return ''.join(result)

    def render_stream(self, template_name, context=None):
        """
        Stream render template line by line.
        """
        output = self.render(template_name, context)
        for line in output.splitlines(keepends=True):
            yield line

    def profile_render(self, template_name, context=None):
        """
        Profile parsing vs rendering vs filter application.
        """
        if context is None:
            context = {}
        start = time.time()
        if template_name not in self.compiled:
            self.cache_template(template_name)
        parse_time = time.time() - start
        start_render = time.time()
        # measure var/filter time by wrapping _eval_var
        rendered = self.render(template_name, context)
        render_time = time.time() - start_render
        return {
            'parsed_seconds': parse_time,
            'rendered_seconds': render_time,
            'output': rendered
        }

    def _tokenize(self, template):
        """
        Tokenize template into text, var, and include tokens.
        """
        token_spec = [
            ('include', re.compile(r"{%\s*include\s+['\"](.*?)['\"]\s*%}")),
            ('var', re.compile(r"{{\s*(.*?)\s*}}")),
        ]
        pos = 0
        tokens = []
        pattern = re.compile(r"({%.*?%}|{{.*?}})", re.DOTALL)
        for match in pattern.finditer(template):
            start, end = match.span()
            if start > pos:
                tokens.append(('text', template[pos:start]))
            expr = match.group(0)
            # check include
            inc = token_spec[0][1].match(expr)
            if inc:
                tokens.append(('include', inc.group(1)))
            else:
                varm = token_spec[1][1].match(expr)
                if varm:
                    tokens.append(('var', varm.group(1)))
                else:
                    tokens.append(('text', expr))
            pos = end
        if pos < len(template):
            tokens.append(('text', template[pos:]))
        return tokens

    def _eval_var(self, expr, context):
        """
        Evaluate a variable expression with filters.
        """
        parts = [p.strip() for p in expr.split('|')]
        var_expr = parts[0]
        try:
            value = dot_lookup(context, var_expr)
        except KeyError:
            value = ''
        for filt in parts[1:]:
            m = re.match(r"(\w+)(?:\((.*?)\))?", filt)
            if not m:
                continue
            fname, farg = m.group(1), m.group(2)
            func = self.filters.get(fname)
            args = []
            if farg is not None:
                # parse farg as int or string
                if re.match(r"^\d+$", farg.strip()):
                    args.append(int(farg.strip()))
                else:
                    stripped = farg.strip()
                    if (stripped.startswith('"') and stripped.endswith('"')) or \
                       (stripped.startswith("'") and stripped.endswith("'")):
                        args.append(stripped[1:-1])
                    else:
                        # lookup in context
                        try:
                            args.append(dot_lookup(context, stripped))
                        except KeyError:
                            args.append(stripped)
            if func:
                value = func(value, *args)
        return value
