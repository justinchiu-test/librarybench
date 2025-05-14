import datetime
import json

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
    return n % 2 != 0

def date(format_str, dt=None):
    dt = dt or datetime.datetime.now()
    return dt.strftime(format_str)

def strftime(format_str, dt=None):
    return date(format_str, dt)

def timeago(from_time, to_time=None):
    to_time = to_time or datetime.datetime.now()
    if isinstance(from_time, (int, float)):
        delta = datetime.timedelta(seconds=from_time)
    else:
        delta = to_time - from_time
    total_seconds = int(delta.total_seconds())
    if total_seconds < 1:
        return "just now"
    if total_seconds < 60:
        return f"{total_seconds} seconds ago"
    minutes = total_seconds // 60
    if minutes < 60:
        return f"{minutes} minutes ago"
    hours = minutes // 60
    return f"{hours} hours ago"

def to_json(data):
    return json.dumps(data)

def from_json(json_str):
    return json.loads(json_str)

def to_yaml(data, indent=0):
    lines = []
    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(' ' * indent + f"{key}:")
            lines.append(to_yaml(value, indent=indent+2))
        else:
            lines.append(' ' * indent + f"{key}: {value}")
    return "\n".join(lines)

def from_yaml(yaml_str):
    result = {}
    for line in yaml_str.splitlines():
        if not line.strip() or line.strip().startswith('#'):
            continue
        if ':' in line:
            key, val = line.split(':', 1)
            key = key.strip()
            val = val.strip()
            if val == "":
                continue
            # try parse int
            try:
                val_parsed = int(val)
            except ValueError:
                try:
                    val_parsed = float(val)
                except ValueError:
                    val_parsed = val
            result[key] = val_parsed
    return result

def render_stream(iterable):
    for item in iterable:
        yield item

def extends(*args, **kwargs):
    raise NotImplementedError("extends is not implemented")

def block(*args, **kwargs):
    raise NotImplementedError("block is not implemented")

def cache_template(*args, **kwargs):
    raise NotImplementedError("cache_template is not implemented")

def trans(*args, **kwargs):
    raise NotImplementedError("trans is not implemented")

def gettext(*args, **kwargs):
    raise NotImplementedError("gettext is not implemented")

def auto_reload(*args, **kwargs):
    raise NotImplementedError("auto_reload is not implemented")

def syntax_highlight(*args, **kwargs):
    raise NotImplementedError("syntax_highlight is not implemented")
