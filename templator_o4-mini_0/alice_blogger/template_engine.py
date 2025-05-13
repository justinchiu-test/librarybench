import os
import re
import json
from datetime import datetime, timedelta
import yaml
from jinja2 import TemplateSyntaxError

# Filters

def add(a, b):
    return a + b

def sub(a, b):
    return a - b

def mul(a, b):
    return a * b

def div(a, b):
    return a / b

def is_even(n):
    return n % 2 == 0

def is_odd(n):
    return n % 2 == 1

def date_filter(value, fmt="%Y-%m-%d"):
    if isinstance(value, datetime):
        return value.strftime(fmt)
    return value

def strftime_filter(value, fmt):
    if isinstance(value, datetime):
        return value.strftime(fmt)
    return value

def timeago_filter(value):
    if not isinstance(value, datetime):
        return value
    now = datetime.utcnow()
    delta = now - value
    if delta.days > 0:
        return f"{delta.days} days ago"
    hours = delta.seconds // 3600
    if hours > 0:
        return f"{hours} hours ago"
    minutes = (delta.seconds % 3600) // 60
    if minutes > 0:
        return f"{minutes} minutes ago"
    return "just now"

def to_json(obj):
    return json.dumps(obj)

def from_json(s):
    return json.loads(s)

def to_yaml(obj):
    return yaml.safe_dump(obj)

def from_yaml(s):
    return yaml.safe_load(s)

def syntax_highlight(template_str, error):
    lineno = getattr(error, 'lineno', None)
    if lineno is not None:
        return f">> {lineno}"
    return ">>"

# AST Nodes

class TextNode:
    def __init__(self, text):
        self.text = text
    def render(self, engine, context, blocks):
        yield self.text

class VarNode:
    def __init__(self, expr, lineno):
        self.expr = expr
        self.lineno = lineno
    def render(self, engine, context, blocks):
        val = engine.eval_expr(self.expr, context, self.lineno)
        yield str(val)

class SetNode:
    def __init__(self, name, expr, lineno):
        self.name = name
        self.expr = expr
        self.lineno = lineno
    def render(self, engine, context, blocks):
        context[self.name] = engine.eval_expr(self.expr, context, self.lineno)
        if False:
            yield ''

class ForNode:
    def __init__(self, var_name, iterable_expr, body, lineno):
        self.var_name = var_name
        self.iterable_expr = iterable_expr
        self.body = body
        self.lineno = lineno
    def render(self, engine, context, blocks):
        iterable = engine.eval_expr(self.iterable_expr, context, self.lineno)
        if iterable is None:
            return
        for item in iterable:
            context[self.var_name] = item
            for node in self.body:
                yield from node.render(engine, context, blocks)

class BlockNode:
    def __init__(self, name, body):
        self.name = name
        self.body = body
    def render(self, engine, context, blocks):
        # if overridden, use override
        if self.name in blocks:
            nodes = blocks[self.name].body
        else:
            nodes = self.body
        for node in nodes:
            yield from node.render(engine, context, blocks)

class TransNode:
    def __init__(self, body):
        self.body = body
    def render(self, engine, context, blocks):
        for node in self.body:
            yield from node.render(engine, context, blocks)

class ExtendsNode:
    def __init__(self, template_name):
        self.template_name = template_name

# Parser

class Parser:
    def __init__(self, template_str):
        self.template = template_str
        self.pos = 0
        self.len = len(template_str)

    def parse(self, end_tags=None):
        nodes = []
        while self.pos < self.len:
            if self.template.startswith('{{', self.pos):
                lineno = self._lineno(self.pos)
                end = self.template.find('}}', self.pos)
                if end == -1:
                    raise TemplateSyntaxError('Unclosed variable tag', lineno)
                content = self.template[self.pos+2:end].strip()
                nodes.append(VarNode(content, lineno))
                self.pos = end + 2
            elif self.template.startswith('{%', self.pos):
                lineno = self._lineno(self.pos)
                end = self.template.find('%}', self.pos)
                if end == -1:
                    raise TemplateSyntaxError('Unclosed tag', lineno)
                tag = self.template[self.pos+2:end].strip()
                self.pos = end + 2
                parts = tag.split(None, 1)
                key = parts[0]
                rest = parts[1] if len(parts) > 1 else ''
                if key == 'for':
                    m = re.match(r'(\w+)\s+in\s+(.+)', rest)
                    if not m:
                        raise TemplateSyntaxError('Malformed for tag', lineno)
                    var_name, iterable = m.group(1), m.group(2)
                    body = self.parse(end_tags=['endfor'])
                    nodes.append(ForNode(var_name, iterable.strip(), body, lineno))
                elif key == 'endfor':
                    if end_tags and 'endfor' in end_tags:
                        return nodes
                    # stray endfor
                elif key == 'block':
                    name = rest.strip().split()[0]
                    body = self.parse(end_tags=['endblock'])
                    nodes.append(BlockNode(name, body))
                elif key == 'endblock':
                    if end_tags and 'endblock' in end_tags:
                        return nodes
                elif key == 'trans':
                    body = self.parse(end_tags=['endtrans'])
                    nodes.append(TransNode(body))
                elif key == 'endtrans':
                    if end_tags and 'endtrans' in end_tags:
                        return nodes
                elif key == 'set':
                    m = re.match(r'(\w+)\s*=\s*(.+)', rest)
                    if not m:
                        raise TemplateSyntaxError('Malformed set tag', lineno)
                    name, expr = m.group(1), m.group(2)
                    nodes.append(SetNode(name, expr.strip(), lineno))
                elif key == 'extends':
                    m = re.match(r"['\"](.+?)['\"]", rest.strip())
                    if not m:
                        raise TemplateSyntaxError('Malformed extends tag', lineno)
                    tpl_name = m.group(1)
                    nodes.append(ExtendsNode(tpl_name))
                elif key == 'if':
                    # only support syntax error detection
                    if not rest.strip():
                        raise TemplateSyntaxError('Missing condition', lineno)
                    # skip to endif
                    _ = self.parse(end_tags=['endif'])
                elif key == 'endif':
                    if end_tags and 'endif' in end_tags:
                        return nodes
                else:
                    # unknown tag, ignore
                    pass
            else:
                next_var = self.template.find('{{', self.pos)
                next_tag = self.template.find('{%', self.pos)
                candidates = [p for p in (next_var, next_tag) if p != -1]
                next_pos = min(candidates) if candidates else self.len
                text = self.template[self.pos:next_pos]
                nodes.append(TextNode(text))
                self.pos = next_pos
        if end_tags:
            # missing end tag
            lineno = self._lineno(self.pos)
            raise TemplateSyntaxError('Unclosed tag', lineno)
        return nodes

    def _lineno(self, pos):
        return self.template[:pos].count('\n') + 1

# The engine

class TemplateEngine:
    def __init__(self, template_dir, cache=True, auto_reload=True, translations=None, locale='en'):
        self.template_dir = template_dir
        # register filters
        self.filters = {
            'add': add,
            'sub': sub,
            'mul': mul,
            'div': div,
            'is_even': is_even,
            'is_odd': is_odd,
            'date': date_filter,
            'strftime': strftime_filter,
            'timeago': timeago_filter,
            'to_json': to_json,
            'from_json': from_json,
            'to_yaml': to_yaml,
            'from_yaml': from_yaml,
        }

    def render(self, template_name, **context):
        path = os.path.join(self.template_dir, template_name)
        with open(path, encoding='utf-8') as f:
            src = f.read()
        try:
            parser = Parser(src)
            ast = parser.parse()
            # handle inheritance
            ext = next((n for n in ast if isinstance(n, ExtendsNode)), None)
            if ext:
                # collect child blocks
                child_blocks = {n.name: n for n in ast if isinstance(n, BlockNode)}
                # load base
                base_path = os.path.join(self.template_dir, ext.template_name)
                with open(base_path, encoding='utf-8') as bf:
                    base_src = bf.read()
                base_ast = Parser(base_src).parse()
                nodes = base_ast
                blocks = child_blocks
            else:
                nodes = ast
                blocks = {}
            rendered = list(self._render_nodes(nodes, dict(context), blocks))
            return ''.join(rendered)
        except TemplateSyntaxError as e:
            msg = syntax_highlight(src, e)
            raise TemplateSyntaxError(msg, e.lineno)

    def render_stream(self, template_name, **context):
        path = os.path.join(self.template_dir, template_name)
        with open(path, encoding='utf-8') as f:
            src = f.read()
        parser = Parser(src)
        ast = parser.parse()
        ext = next((n for n in ast if isinstance(n, ExtendsNode)), None)
        if ext:
            child_blocks = {n.name: n for n in ast if isinstance(n, BlockNode)}
            base_path = os.path.join(self.template_dir, ext.template_name)
            with open(base_path, encoding='utf-8') as bf:
                base_src = bf.read()
            nodes = Parser(base_src).parse()
            blocks = child_blocks
        else:
            nodes = ast
            blocks = {}
        return self._render_nodes(nodes, dict(context), blocks)

    def _render_nodes(self, nodes, context, blocks):
        for node in nodes:
            if isinstance(node, ExtendsNode):
                continue
            yield from node.render(self, context, blocks)

    def eval_expr(self, expr, context, lineno):
        # split by | outside parentheses
        parts = []
        buf = ''
        depth = 0
        for ch in expr:
            if ch == '(':
                depth += 1
                buf += ch
            elif ch == ')':
                depth -= 1
                buf += ch
            elif ch == '|' and depth == 0:
                parts.append(buf.strip())
                buf = ''
            else:
                buf += ch
        if buf:
            parts.append(buf.strip())
        # base value
        base = parts[0]
        # literal string
        if base.startswith(("'", '"')) and base.endswith(("'", '"')):
            val = base[1:-1]
        # integer literal
        elif re.match(r'^-?\d+$', base):
            val = int(base)
        # float literal
        elif re.match(r'^-?\d+\.\d*$', base):
            val = float(base)
        else:
            # variable lookup
            try:
                val = context[base]
            except Exception:
                val = None
        # process filters and chains
        for part in parts[1:]:
            # extract filter name
            name = part
            args = []
            chain = ''
            # function call with args?
            if '(' in part:
                m = re.match(r'^(\w+)\((.*)\)(.*)$', part)
                if not m:
                    raise TemplateSyntaxError('Bad filter syntax', lineno)
                name = m.group(1)
                raw_args = m.group(2)
                chain = m.group(3)
                # parse arguments (simple split)
                # respect quotes
                arg_list = []
                cur = ''
                in_quote = False
                quote_char = ''
                for c in raw_args:
                    if c in ("'", '"'):
                        if in_quote and c == quote_char:
                            in_quote = False
                        elif not in_quote:
                            in_quote = True
                            quote_char = c
                        cur += c
                    elif c == ',' and not in_quote:
                        arg_list.append(cur.strip())
                        cur = ''
                    else:
                        cur += c
                if cur.strip():
                    arg_list.append(cur.strip())
                for a in arg_list:
                    if a.startswith(("'", '"')) and a.endswith(("'", '"')):
                        args.append(a[1:-1])
                    elif re.match(r'^\d+$', a):
                        args.append(int(a))
                    else:
                        args.append(context.get(a))
            else:
                # no args, maybe chain
                m2 = re.match(r'^(\w+)(.*)$', part)
                if m2:
                    name = m2.group(1)
                    chain = m2.group(2)
            func = self.filters.get(name)
            if not func:
                raise TemplateSyntaxError(f'Unknown filter {name}', lineno)
            val = func(val, *args)
            # apply attribute/index chain
            if chain:
                tokens = re.findall(r'(\.\w+|\[\d+\])', chain)
                for tok in tokens:
                    if tok.startswith('.'):
                        key = tok[1:]
                        try:
                            if isinstance(val, dict):
                                val = val[key]
                            else:
                                val = getattr(val, key)
                        except Exception:
                            val = None
                    elif tok.startswith('['):
                        idx = int(tok[1:-1])
                        try:
                            val = val[idx]
                        except Exception:
                            val = None
        return val
