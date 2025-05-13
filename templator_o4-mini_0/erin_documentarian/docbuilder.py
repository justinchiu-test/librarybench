import datetime
import json
import functools
import gettext as _gettext
from functools import lru_cache

try:
    import yaml
except ImportError:
    yaml = None

def add(a, b):
    """Return sum of a and b."""
    return a + b

def sub(a, b):
    """Return difference of a and b."""
    return a - b

def mul(item, n):
    """Repeat item n times. Works for sequences and strings."""
    return item * n

def div(lst, n):
    """Split list lst into n roughly equal parts."""
    if n <= 0:
        raise ValueError("n must be positive")
    length = len(lst)
    base, rem = divmod(length, n)
    parts = []
    start = 0
    for i in range(n):
        size = base + (1 if i < rem else 0)
        parts.append(lst[start:start+size])
        start += size
    return parts

def is_even(n):
    """Return True if n is even."""
    return n % 2 == 0

def is_odd(n):
    """Return True if n is odd."""
    return n % 2 != 0

def date(fmt):
    """Return current date formatted by fmt."""
    return datetime.datetime.now().strftime(fmt)

def timeago(dt, now=None):
    """Return a relative time string like 'X days ago'."""
    now = now or datetime.datetime.now()
    if not isinstance(dt, datetime.datetime):
        raise TypeError("dt must be a datetime object")
    delta = now - dt
    days = delta.days
    seconds = delta.seconds
    if days < 0:
        # future date
        days = abs(days)
        return f"in {days} days"
    if days == 0:
        if seconds < 60:
            return "just now"
        if seconds < 3600:
            mins = seconds // 60
            return f"{mins} minutes ago"
        hours = seconds // 3600
        return f"{hours} hours ago"
    if days == 1:
        return "1 day ago"
    return f"{days} days ago"

def strftime(dt, fmt):
    """Format datetime dt with fmt."""
    if not isinstance(dt, datetime.datetime):
        raise TypeError("dt must be a datetime object")
    return dt.strftime(fmt)

def to_json(obj):
    """Serialize obj to JSON string."""
    return json.dumps(obj)

def from_json(s):
    """Deserialize JSON string to Python object."""
    return json.loads(s)

def to_yaml(obj):
    """Serialize obj to YAML string."""
    if yaml is None:
        raise RuntimeError("yaml library not available")
    return yaml.dump(obj)

def from_yaml(s):
    """Deserialize YAML string to Python object."""
    if yaml is None:
        raise RuntimeError("yaml library not available")
    return yaml.safe_load(s)

def render_stream(iterable):
    """Stream items from iterable, yielding them one by one."""
    for item in iterable:
        yield item

def extends(template_name):
    """Placeholder for extending a template."""
    return f"<extends {template_name}>"

def block(name, content=""):
    """Placeholder for defining a block in a template."""
    return f"<block {name}>{content}</block>"

def cache_template(func):
    """Decorator to cache template renderings."""
    cached = lru_cache(maxsize=None)(func)
    functools.update_wrapper(cached, func)
    return cached

def trans(s):
    """Translate string s."""
    return _gettext.gettext(s)

def gettext(s):
    """Alias for trans."""
    return trans(s)

def auto_reload(func):
    """Decorator to mark a function for auto reload."""
    func.auto_reload = True
    return func

def syntax_highlight(code, language="text"):
    """Simplistic syntax highlighter stub."""
    # Just return code wrapped
    return f"<pre class='highlight {language}'>{code}</pre>"
