import os
import json
import configparser
import getpass
import time
import functools

try:
    import yaml
except ImportError:
    yaml = None
try:
    import toml
except ImportError:
    toml = None

def load_config(path):
    """
    Load configuration from JSON, YAML, TOML, or INI file.
    """
    ext = os.path.splitext(path)[1].lower()
    if ext == '.json':
        with open(path, 'r') as f:
            return json.load(f)
    elif ext in ('.yaml', '.yml'):
        if yaml is None:
            raise ImportError("PyYAML is required for YAML support")
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    elif ext == '.toml':
        if toml is None:
            raise ImportError("toml package is required for TOML support")
        with open(path, 'r') as f:
            return toml.load(f)
    elif ext == '.ini':
        parser = configparser.ConfigParser()
        parser.read(path)
        return {section: dict(parser.items(section)) for section in parser.sections()}
    else:
        raise ValueError(f"Unsupported config format: {ext}")

def run_dry_run(steps):
    """
    Simulate running steps without side effects.
    steps: list of callables or step names (strings)
    Returns list of step identifiers.
    """
    result = []
    for step in steps:
        if isinstance(step, str):
            result.append(step)
        elif callable(step):
            result.append(step.__name__)
        else:
            result.append(str(step))
    return result

def branch_flow(condition, success_flow, failure_flow, context=None):
    """
    Execute success_flow or failure_flow based on condition.
    """
    if condition:
        return success_flow(context)
    else:
        return failure_flow(context)

def prompt_interactive(prompt):
    """
    Prompt the user for input.
    """
    return input(prompt)

def secure_prompt(prompt):
    """
    Securely prompt for a password or token.
    """
    pwd = getpass.getpass(prompt)
    return pwd

def retry(retries=3, exceptions=(Exception,), delay=1, backoff=2):
    """
    Decorator to retry a function on exception with backoff.
    """
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            mtries, mdelay = retries, delay
            last_exc = None
            while mtries > 0:
                try:
                    return fn(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    mtries -= 1
                    if mtries == 0:
                        break
                    time.sleep(mdelay)
                    mdelay *= backoff
            raise last_exc
        return wrapper
    return decorator

class Context(dict):
    """
    Simple context for passing data between steps.
    """
    def update_schema(self, name, schema):
        self[name] = schema

def export_docs(flows):
    """
    Generate Markdown documentation for the provided flow functions.
    flows: list of callables
    """
    lines = ["# Workflow Documentation", ""]
    for fn in flows:
        name = fn.__name__
        doc = fn.__doc__ or ""
        lines.append(f"## {name}")
        if doc:
            lines.append(doc.strip())
        lines.append("")
    return "\n".join(lines)

class HookManager:
    """
    Manage hooks for pipeline events.
    """
    def __init__(self):
        self._hooks = {'pre_run': [], 'on_success': [], 'on_failure': []}

    def register_hook(self, event, func):
        if event not in self._hooks:
            raise ValueError(f"Unknown event: {event}")
        self._hooks[event].append(func)

    def run_hooks(self, event, *args, **kwargs):
        if event not in self._hooks:
            raise ValueError(f"Unknown event: {event}")
        for hook in self._hooks[event]:
            hook(*args, **kwargs)

def validate_params(params, schema):
    """
    Validate params dict against schema.
    schema: dict of param -> {'type': type, 'required': bool, 'min': val, 'max': val}
    """
    for key, rules in schema.items():
        if rules.get('required', False) and key not in params:
            raise ValueError(f"Missing required parameter: {key}")
        if key in params:
            val = params[key]
            expected_type = rules.get('type')
            if expected_type and not isinstance(val, expected_type):
                raise ValueError(f"Parameter '{key}' must be {expected_type}, got {type(val)}")
            if 'min' in rules and val < rules['min']:
                raise ValueError(f"Parameter '{key}' must be >= {rules['min']}")
            if 'max' in rules and val > rules['max']:
                raise ValueError(f"Parameter '{key}' must be <= {rules['max']}")
    return True
