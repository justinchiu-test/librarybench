import json
import configparser
import getpass
import time
from functools import wraps

# YAML and TOML imports may require installation
try:
    import yaml
except ImportError:
    yaml = None

try:
    import toml
except ImportError:
    toml = None

# tomllib is in stdlib Python 3.11+
try:
    import tomllib
except ImportError:
    tomllib = None

hooks = {}

def _parse_simple_yaml(content):
    """
    A minimal YAML parser for simple mappings and lists.
    Supports:
      key: value
      key:
        - item1
        - item2
    """
    result = {}
    current_key = None
    for line in content.splitlines():
        if not line.strip():
            continue
        stripped = line.lstrip()
        # Detect list items (indented with '- ')
        if stripped.startswith('- '):
            if current_key is None or not isinstance(result.get(current_key), list):
                raise ValueError("Invalid YAML content")
            item = stripped[2:].strip()
            result[current_key].append(item)
        else:
            # Parse a key: value or key:
            if ':' not in line:
                continue
            key_part, val_part = line.split(':', 1)
            key = key_part.strip()
            val = val_part.strip()
            if val == '':
                # Start of a list
                result[key] = []
                current_key = key
            else:
                # Scalar value: try int, float, else string
                if val.isdigit():
                    parsed = int(val)
                else:
                    try:
                        parsed = float(val)
                    except ValueError:
                        parsed = val.strip('"').strip("'")
                result[key] = parsed
                current_key = None
    return result

def load_config(path):
    ext = path.lower().split('.')[-1]
    with open(path, 'r') as f:
        content = f.read()
        if ext == 'json':
            return json.loads(content)
        elif ext in ('yaml', 'yml'):
            if yaml is not None:
                return yaml.safe_load(content)
            else:
                # Fallback minimal YAML parsing
                return _parse_simple_yaml(content)
        elif ext == 'toml':
            if toml is not None:
                return toml.loads(content)
            elif tomllib is not None:
                return tomllib.loads(content)
            else:
                raise ImportError("toml is required for TOML support")
        elif ext in ('ini', 'cfg'):
            cp = configparser.ConfigParser()
            cp.read_string(content)
            return {section: dict(cp[section]) for section in cp.sections()}
        else:
            raise ValueError(f"Unsupported config format: {ext}")

def run_dry_run(commands, hosts):
    preview = []
    for host in hosts:
        for cmd in commands:
            preview.append((host, cmd))
    return preview

def branch_flow(exit_code, branches):
    if exit_code in branches:
        return branches[exit_code]()
    elif 'default' in branches:
        return branches['default']()
    else:
        raise KeyError(f"No branch for exit_code {exit_code}")

def prompt_interactive(prompt, choices=None):
    prompt_str = f"{prompt}"
    if choices:
        prompt_str += f" {choices}"
    prompt_str += ": "
    while True:
        ans = input(prompt_str)
        if choices is None or ans in choices:
            return ans

def secure_prompt(prompt):
    val = getpass.getpass(prompt)
    # attempt to clear sensitive variable
    try:
        _ = [''] * len(val)
    except Exception:
        pass
    return val

def retry(func=None, *, retries=3, exceptions=(Exception,), backoff=0):
    if func is None:
        return lambda f: retry(f, retries=retries, exceptions=exceptions, backoff=backoff)
    @wraps(func)
    def wrapper(*args, **kwargs):
        attempt = 0
        while True:
            try:
                return func(*args, **kwargs)
            except exceptions:
                attempt += 1
                if attempt > retries:
                    raise
                if backoff:
                    time.sleep(backoff * attempt)
    return wrapper

class Context:
    def __init__(self):
        self.data = {
            'results': [],
            'hosts': [],
            'compliance': {}
        }
    def add_result(self, result):
        self.data['results'].append(result)
    def add_host(self, host):
        self.data['hosts'].append(host)
    def update_compliance(self, key, value):
        self.data['compliance'][key] = value
    def get_state(self):
        return self.data

def export_docs(context, fmt='md'):
    state = context.get_state()
    if fmt == 'md':
        lines = ["# Audit Report", "", "## Hosts"]
        for h in state['hosts']:
            lines.append(f"- {h}")
        lines += ["", "## Results"]
        for r in state['results']:
            lines.append(f"- {r}")
        lines += ["", "## Compliance"]
        for k, v in state['compliance'].items():
            lines.append(f"- {k}: {v}")
        return "\n".join(lines)
    elif fmt == 'html':
        lines = ["<h1>Audit Report</h1>", "<h2>Hosts</h2>", "<ul>"]
        for h in state['hosts']:
            lines.append(f"<li>{h}</li>")
        lines.append("</ul><h2>Results</h2><ul>")
        for r in state['results']:
            lines.append(f"<li>{r}</li>")
        lines.append("</ul><h2>Compliance</h2><ul>")
        for k, v in state['compliance'].items():
            lines.append(f"<li>{k}: {v}</li>")
        lines.append("</ul>")
        return "\n".join(lines)
    else:
        raise ValueError(f"Unsupported format: {fmt}")

def register_hook(event, fn):
    if event not in hooks:
        hooks[event] = []
    hooks[event].append(fn)

def run_hooks(event, *args, **kwargs):
    for fn in hooks.get(event, []):
        fn(*args, **kwargs)

def validate_params(targets=None, severity=None, policy_ids=None):
    if targets is not None:
        import ipaddress
        for t in targets:
            try:
                ipaddress.ip_address(t)
            except Exception:
                raise ValueError(f"Invalid IP address: {t}")
    if severity is not None:
        if not isinstance(severity, (int, float)) or not (0 <= severity <= 10):
            raise ValueError("Severity must be between 0 and 10")
    if policy_ids is not None:
        if not isinstance(policy_ids, (list, tuple)):
            raise ValueError("Policy IDs must be a list")
        for p in policy_ids:
            if not isinstance(p, str) or not p:
                raise ValueError(f"Invalid policy ID: {p}")
    return True
