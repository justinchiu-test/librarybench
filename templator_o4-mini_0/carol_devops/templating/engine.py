import os
import json
import yaml
import gettext
import datetime
import re
import pygments
import pygments.lexers
import pygments.formatters
import jinja2

class TemplateEngine:
    def __init__(self, template_dir, production=False):
        self.template_dir = template_dir
        loader = jinja2.FileSystemLoader(self.template_dir)
        auto_reload = not production
        self.env = jinja2.Environment(
            loader=loader,
            auto_reload=auto_reload,
            extensions=['jinja2.ext.i18n']
        )
        if production:
            cache_dir = os.path.join(temp_dir := os.getenv('TMPDIR', '/tmp'), 'jinja_cache')
            os.makedirs(cache_dir, exist_ok=True)
            self.env.bytecode_cache = jinja2.FileSystemBytecodeCache(cache_dir)
        # Filters
        self.env.filters['add'] = lambda a, b: a + b
        self.env.filters['sub'] = lambda a, b: a - b
        self.env.filters['mul'] = lambda a, b: a * b
        self.env.filters['div'] = lambda a, b: a / b if b != 0 else ''
        self.env.filters['is_even'] = lambda n: n % 2 == 0
        self.env.filters['is_odd'] = lambda n: n % 2 != 0
        self.env.filters['date'] = lambda fmt: datetime.datetime.now().strftime(fmt)
        self.env.filters['timeago'] = self._timeago
        self.env.filters['strftime'] = lambda dt, fmt: dt.strftime(fmt)
        self.env.filters['to_json'] = lambda obj: json.dumps(obj)
        self.env.filters['from_json'] = lambda s: json.loads(s)
        self.env.filters['to_yaml'] = lambda obj: yaml.safe_dump(obj)
        self.env.filters['from_yaml'] = lambda s: yaml.safe_load(s)
        self.env.filters['syntax_highlight'] = self._syntax_highlight
        # Translations
        self.env.filters['gettext'] = gettext.gettext
        self.env.filters['trans'] = gettext.gettext
        self.env.install_gettext_translations(gettext, newstyle=True)

    def _timeago(self, value):
        now = datetime.datetime.now()
        if not isinstance(value, datetime.datetime):
            return ''
        diff = now - value
        seconds = int(diff.total_seconds())
        if seconds < 60:
            return f"{seconds} seconds ago"
        minutes = seconds // 60
        if minutes < 60:
            return f"{minutes} minutes ago"
        hours = minutes // 60
        if hours < 24:
            return f"{hours} hours ago"
        days = hours // 24
        return f"{days} days ago"

    def _syntax_highlight(self, code):
        """
        Highlight Python code, but strip ANSI escape sequences so that
        plain text (e.g. 'def foo') remains contiguous.
        """
        lexer = pygments.lexers.get_lexer_by_name('python')
        formatter = pygments.formatters.TerminalFormatter()
        highlighted = pygments.highlight(code, lexer, formatter)
        # strip ANSI escape codes
        ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
        return ansi_escape.sub('', highlighted)

    def render(self, template_name, context=None):
        context = context or {}
        tmpl = self.env.get_template(template_name)
        return tmpl.render(**context)

    def render_stream(self, template_name, context=None, chunk_size=1024):
        context = context or {}
        tmpl = self.env.get_template(template_name)
        # Use generate to yield the template in chunks (ignores chunk_size)
        return tmpl.generate(**context)
