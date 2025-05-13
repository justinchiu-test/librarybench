import json
import configparser
import re
import time
from getpass import getpass
from functools import wraps

try:
    import yaml
except ImportError:
    yaml = None

try:
    import toml
except ImportError:
    toml = None

# Hook registry
_hooks = {
    'before_tests': [],
    'after_each_test': [],
    'on_failure': [],
    'on_complete': []
}

class Context:
    def __init__(self):
        self.artifacts = {}
        self.logs = []
        self.results = {}

    def add_artifact(self, name, data):
        self.artifacts[name] = data

    def add_log(self, message):
        self.logs.append(message)

    def set_result(self, test_name, result):
        self.results[test_name] = result

def register_hook(event, func):
    if event not in _hooks:
        raise ValueError(f"Unknown hook event: {event}")
    _hooks[event].append(func)

def _run_hooks(event, *args, **kwargs):
    for hook in _hooks.get(event, []):
        hook(*args, **kwargs)

def load_config(path):
    if path.endswith('.json'):
        with open(path) as f:
            return json.load(f)
    elif path.endswith(('.yaml', '.yml')):
        if yaml is None:
            raise ImportError("PyYAML is required for YAML support")
        with open(path) as f:
            return yaml.safe_load(f)
    elif path.endswith('.toml'):
        if toml is None:
            raise ImportError("toml is required for TOML support")
        with open(path) as f:
            return toml.load(f)
    elif path.endswith('.ini'):
        config = configparser.ConfigParser()
        config.read(path)
        return {section: dict(config[section]) for section in config.sections()}
    else:
        raise ValueError("Unsupported config format")

def run_dry_run(test_plan):
    return [test['name'] for test in test_plan]

def branch_flow(prev_exit_code, mapping):
    key = 'pass' if prev_exit_code == 0 else 'fail'
    return mapping.get(key, [])

def prompt_interactive(prompt_text, choices):
    print(prompt_text)
    for idx, choice in enumerate(choices, 1):
        print(f"{idx}. {choice}")
    selection = input("Select option: ")
    idx = int(selection) - 1
    return choices[idx]

def secure_prompt(prompt_text):
    cred = getpass(prompt_text)
    try:
        return cred
    finally:
        try:
            del cred
        except UnboundLocalError:
            pass

def retry(retries=3, backoff=0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    attempt += 1
                    if attempt > retries:
                        raise
                    time.sleep(backoff)
        return wrapper
    return decorator

def export_docs(test_plan, format='markdown'):
    if format == 'markdown':
        lines = ["# Test Plan", ""]
        for t in test_plan:
            lines.append(f"- **{t['name']}**: {t.get('desc','')}")
        return "\n".join(lines)
    elif format == 'html':
        lines = ["<h1>Test Plan</h1>", "<ul>"]
        for t in test_plan:
            lines.append(f"<li><strong>{t['name']}</strong>: {t.get('desc','')}</li>")
        lines.append("</ul>")
        return "\n".join(lines)
    else:
        raise ValueError("Unsupported format")

def validate_params(env, browser, tags):
    # env: lowercase letters and underscores only
    if not re.match(r'^[a-z_]+$', env):
        raise ValueError("Invalid env name")
    # browser must be one of the supported
    if browser not in ['chrome', 'firefox', 'safari']:
        raise ValueError("Unsupported browser")
    # tags: alphanumeric, underscore, hyphen only
    if not all(re.match(r'^[\w-]+$', t) for t in tags):
        raise ValueError("Invalid tag pattern")
