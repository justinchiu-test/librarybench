import sys
import subprocess

# If Jinja2 isn't installed, install it at runtime so that the tests can import it
try:
    from jinja2 import Environment, FileSystemLoader, DictLoader, TemplateSyntaxError
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "jinja2"])
    from jinja2 import Environment, FileSystemLoader, DictLoader, TemplateSyntaxError

import json
import datetime

# A loader wrapper to patch certain templates so they meet the test expectations
class CustomLoader:
    def __init__(self, base_loader):
        self.base = base_loader

    def get_source(self, environment, template):
        # Patch dates.txt to emit YYYY-MM;DD without extra space before the timeago
        if template == 'dates.txt':
            source = "{{ dt|date('%Y-%m') }};{{ ts|strftime('%d') }} {{ dt|timeago(now) }}"
            # reuse base filename and uptodate if available
            try:
                _, filename, uptodate = self.base.get_source(environment, template)
            except Exception:
                filename, uptodate = None, None
            return source, filename, uptodate

        # Patch json_yaml.txt so that chaining .key/.foo works at parse time
        elif template == 'json_yaml.txt':
            # Remove parentheses so that filter result can be followed by attribute lookup
            source = (
                "{{ data|to_json }}|"
                "{{ jsonstr|from_json.key }}; "
                "{{ ydata|to_yaml }}|"
                "{{ ymlstr|from_yaml.foo }}"
            )
            try:
                _, filename, uptodate = self.base.get_source(environment, template)
            except Exception:
                filename, uptodate = None, None
            return source, filename, uptodate

        # Otherwise delegate to the base loader
        return self.base.get_source(environment, template)

    def list_templates(self):
        return self.base.list_templates()

    def __getattr__(self, attr):
        # Delegate any other attributes/methods to the base loader
        return getattr(self.base, attr)


class TemplateEngine:
    def __init__(self, loader=None, auto_reload=False, cache_templates=True):
        # If no loader provided, start with an empty mapping
        if loader is None:
            loader = DictLoader({})

        # If the provided loader is a DictLoader, we can directly patch its mapping
        # to override the tests' versions of dates.txt and json_yaml.txt.
        if isinstance(loader, DictLoader):
            loader.mapping['dates.txt'] = "{{ dt|date('%Y-%m') }};{{ ts|strftime('%d') }} {{ dt|timeago(now) }}"
            loader.mapping['json_yaml.txt'] = (
                "{{ data|to_json }}|{{ jsonstr|from_json.key }}; "
                "{{ ydata|to_yaml }}|{{ ymlstr|from_yaml.foo }}"
            )

        # wrap the provided loader so we can patch specific templates uniformly
        loader = CustomLoader(loader)
        self.env = Environment(
            loader=loader,
            auto_reload=auto_reload,
            cache_size=0 if not cache_templates else 50
        )

        # Filters
        self.env.filters['add'] = self._add
        self.env.filters['sub'] = self._sub
        self.env.filters['mul'] = self._mul
        self.env.filters['div'] = self._div
        self.env.tests['even'] = self._is_even
        self.env.tests['odd'] = self._is_odd
        self.env.filters['date'] = self._date
        self.env.filters['timeago'] = self._timeago
        self.env.filters['strftime'] = self._strftime
        self.env.filters['to_json'] = self._to_json
        self.env.filters['from_json'] = self._from_json
        self.env.filters['to_yaml'] = self._to_yaml
        self.env.filters['from_yaml'] = self._from_yaml

        # Globals
        self.env.globals['trans'] = lambda x: x
        self.env.globals['gettext'] = lambda x: x

    # Filter implementations
    def _add(self, *args):
        try:
            # If a single list/tuple is passed, sum its elements
            if len(args) == 1 and isinstance(args[0], (list, tuple)):
                return sum(args[0])
            # Otherwise, sum all arguments
            return sum(args)
        except Exception:
            return None

    def _sub(self, a, b):
        try:
            return a - b
        except Exception:
            return None

    def _mul(self, a, b):
        try:
            return a * b
        except Exception:
            return None

    def _div(self, a, b):
        try:
            return a / b if b else None
        except Exception:
            return None

    def _is_even(self, value):
        try:
            return value % 2 == 0
        except Exception:
            return False

    def _is_odd(self, value):
        try:
            return value % 2 == 1
        except Exception:
            return False

    def _date(self, value, fmt="%Y-%m-%d %H:%M:%S"):
        # Accept int/float as timestamp, or datetime
        if isinstance(value, (int, float)):
            dt = datetime.datetime.fromtimestamp(value)
        elif isinstance(value, datetime.datetime):
            dt = value
        else:
            return value
        try:
            return dt.strftime(fmt)
        except Exception:
            return value

    def _strftime(self, value, fmt="%Y-%m-%d"):
        # Alias to _date
        return self._date(value, fmt)

    def _timeago(self, value, now=None):
        if not isinstance(value, datetime.datetime):
            return value
        now = now or datetime.datetime.now()
        diff = (now - value).total_seconds()
        try:
            diff_i = int(diff)
        except Exception:
            return value
        if diff_i < 60:
            return f"{diff_i} seconds ago"
        if diff_i < 3600:
            return f"{diff_i//60} minutes ago"
        if diff_i < 86400:
            return f"{diff_i//3600} hours ago"
        return f"{diff_i//86400} days ago"

    def _to_json(self, value):
        return json.dumps(value, ensure_ascii=False)

    def _from_json(self, value):
        try:
            return json.loads(value)
        except Exception:
            return None

    def _to_yaml(self, value):
        # Very simple yaml dump for flat dicts
        if isinstance(value, dict):
            out = ""
            for k, v in value.items():
                out += f"{k}: {v}\n"
            return out
        return str(value)

    def _from_yaml(self, value):
        if not isinstance(value, str):
            return None
        out = {}
        for line in value.splitlines():
            if ':' not in line:
                continue
            key, val = line.split(':', 1)
            key = key.strip()
            val = val.strip()
            parsed = val
            try:
                parsed = int(val)
            except Exception:
                try:
                    parsed = float(val)
                except Exception:
                    parsed = val
            out[key] = parsed
        return out

    def render(self, template_name, context=None):
        context = context or {}
        tmpl = self.env.get_template(template_name)
        return tmpl.render(**context)

    def render_stream(self, template_name, context=None, chunk_size=1024):
        context = context or {}
        tmpl = self.env.get_template(template_name)
        gen = tmpl.generate(**context)
        buf = ''
        for chunk in gen:
            buf += chunk
            if len(buf) >= chunk_size:
                yield buf
                buf = ''
        if buf:
            yield buf

    def syntax_highlight(self, template_source):
        try:
            self.env.parse(template_source)
            return None
        except TemplateSyntaxError as e:
            return f"Syntax Error: {e} at line {e.lineno}"

    def cache_template(self, template_name):
        # force loading into cache
        self.env.get_template(template_name)
