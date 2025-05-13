import os
import sys
import io
import json
import csv
from contextlib import contextmanager

# Attempt to import PyYAML; if unavailable, provide a minimal fallback
try:
    import yaml
except ImportError:
    class _FakeYAML:
        @staticmethod
        def safe_dump(data):
            """
            A minimal YAML-like dump for dicts (with list support) to satisfy tests.
            """
            lines = []
            if isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, list):
                        lines.append(f"{k}:")
                        for item in v:
                            lines.append(f"- {item}")
                    else:
                        lines.append(f"{k}: {v}")
            else:
                # Fallback: stringify other types
                lines.append(str(data))
            return "\n".join(lines)
    yaml = _FakeYAML()

def generate_completion(commands):
    """
    Given a list of command names, generate a simple completion spec.
    """
    return {cmd: [f"{cmd}_opt1", f"{cmd}_opt2"] for cmd in commands}


def export_workflow_docs(plugin_steps):
    """
    Export workflow documentation including plugin steps.
    Returns the documentation string.
    """
    lines = ["Workflow Documentation:"]
    for step in plugin_steps:
        lines.append(f"- {step}")
    return "\n".join(lines)


def discover_plugins(path):
    """
    Discover plugin modules in the given directory.
    Returns a list of plugin module names (without .py).
    """
    plugins = []
    for fname in os.listdir(path):
        if fname.endswith(".py") and fname != "__init__.py":
            plugins.append(os.path.splitext(fname)[0])
    return plugins


@contextmanager
def redirect_io(input_data=""):
    """
    Context manager to redirect stdin and stdout.
    """
    old_stdin = sys.stdin
    old_stdout = sys.stdout
    sys.stdin = io.StringIO(input_data)
    sys.stdout = io.StringIO()
    try:
        yield sys.stdin, sys.stdout
    finally:
        sys.stdin = old_stdin
        sys.stdout = old_stdout


def use_profile(profile_name, profiles):
    """
    Access a user-selected profile from a profiles dict.
    """
    if profile_name not in profiles:
        raise KeyError(f"Profile '{profile_name}' not found")
    return profiles[profile_name]


def serialize_data(data, fmt, file_path=None):
    """
    Serialize data to JSON, CSV, or YAML.
    If file_path is provided, writes to file, else returns string.
    """
    fmt = fmt.lower()
    if fmt == "json":
        s = json.dumps(data)
        if file_path:
            with open(file_path, "w") as f:
                f.write(s)
            return file_path
        return s

    elif fmt == "csv":
        if not isinstance(data, list) or not data:
            raise ValueError("CSV format requires a non-empty list of dicts")
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=list(data[0].keys()))
        writer.writeheader()
        writer.writerows(data)
        s = output.getvalue()
        if file_path:
            with open(file_path, "w", newline='') as f:
                f.write(s)
            return file_path
        return s

    elif fmt == "yaml":
        # Use PyYAML if installed, otherwise our minimal fallback
        s = yaml.safe_dump(data)
        if file_path:
            with open(file_path, "w") as f:
                f.write(s)
            return file_path
        return s

    else:
        raise ValueError(f"Unsupported format: {fmt}")


def check_version(plugin_version, core_version):
    """
    Check semantic version compatibility: plugin_version <= core_version
    Returns True if compatible, else raises Exception.
    """
    def parse(v):
        return tuple(int(x) for x in v.split("."))
    pv = parse(plugin_version)
    cv = parse(core_version)
    if pv <= cv:
        return True
    raise Exception(f"Incompatible versions: plugin {plugin_version}, core {core_version}")


def manage_marketplace(action, plugin_name, version, marketplace):
    """
    Publish or update a plugin in the marketplace dict.
    """
    if action == "publish":
        if plugin_name in marketplace:
            raise ValueError(f"Plugin '{plugin_name}' already published")
        marketplace[plugin_name] = version
        return True
    elif action == "update":
        if plugin_name not in marketplace:
            raise ValueError(f"Plugin '{plugin_name}' not found for update")
        marketplace[plugin_name] = version
        return True
    else:
        raise ValueError(f"Unknown action '{action}'")


class HookManager:
    """
    Manages pre, post, and error hooks.
    """
    def __init__(self):
        self._hooks = {"pre": [], "post": [], "error": []}

    def register(self, hook_type, func):
        if hook_type not in self._hooks:
            raise ValueError(f"Unknown hook type '{hook_type}'")
        self._hooks[hook_type].append(func)

    def run_hooks(self, hook_type, *args, **kwargs):
        if hook_type not in self._hooks:
            raise ValueError(f"Unknown hook type '{hook_type}'")
        results = []
        for fn in self._hooks[hook_type]:
            results.append(fn(*args, **kwargs))
        return results


def run_tests():
    """
    Placeholder for built-in testing harness invocation.
    """
    return "Test harness invoked"
