import sys
import json
import csv
import io
import contextlib

registered_hooks = {}

def generate_completion(shell="bash"):
    completions = {
        "bash": "complete -C 'cli' cli",
        "zsh": "#compdef cli\n_cli() { _arguments '*: :_cli_help'}",
        "fish": "complete -c cli -a '(cli --help)'",
    }
    return completions.get(shell, "")

def export_workflow_docs(workflows, format="md"):
    if format == "md":
        docs = ""
        for name, desc in workflows.items():
            docs += f"## {name}\n{desc}\n\n"
        return docs.strip()
    elif format == "html":
        docs = ""
        for name, desc in workflows.items():
            docs += f"<h2>{name}</h2><p>{desc}</p>\n"
        return docs.strip()
    else:
        raise ValueError("Unsupported format")

def discover_plugins(plugin_list):
    certified = []
    for plugin in plugin_list:
        if "unsafe" not in plugin:
            certified.append(plugin)
    return certified

@contextlib.contextmanager
def redirect_io(stdout=None, stderr=None):
    old_out, old_err = sys.stdout, sys.stderr
    if stdout is None:
        stdout = old_out
    if stderr is None:
        stderr = old_err
    sys.stdout, sys.stderr = stdout, stderr
    try:
        yield
    finally:
        sys.stdout, sys.stderr = old_out, old_err

def use_profile(profile_name, profiles=None):
    defaults = {
        "dev": {"debug": True, "optimizations": False},
        "staging": {"debug": False, "optimizations": True},
        "prod": {"debug": False, "optimizations": True},
    }
    if profiles is None:
        profiles = defaults
    return profiles.get(profile_name, {})

def serialize_data(data, format="json"):
    if format == "json":
        return json.dumps(data)
    elif format == "yaml":
        lines = []
        if isinstance(data, dict):
            for k, v in data.items():
                lines.append(f"{k}: {v}")
            return "\n".join(lines)
        else:
            raise ValueError("YAML format supports only dict")
    elif format == "csv":
        if isinstance(data, list) and data and isinstance(data[0], dict):
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=list(data[0].keys()))
            writer.writeheader()
            for row in data:
                writer.writerow(row)
            return output.getvalue().strip()
        else:
            raise ValueError("CSV format supports only list of dicts")
    else:
        raise ValueError("Unsupported format")

def check_version(current_version, latest_version):
    def parse(v):
        return tuple(int(x) for x in v.split("."))
    return parse(current_version) >= parse(latest_version)

def manage_marketplace(plugins):
    return sorted(plugins, key=lambda p: p.get("rating", 0), reverse=True)

def register_hooks(hooks):
    for stage, funcs in hooks.items():
        if stage not in registered_hooks:
            registered_hooks[stage] = []
        registered_hooks[stage].extend(funcs)
    return registered_hooks

def run_tests(test_specs):
    results = {"passed": 0, "failed": 0, "details": []}
    for spec in test_specs:
        func = spec.get("func")
        args = spec.get("args", ())
        kwargs = spec.get("kwargs", {})
        expected = spec.get("expected")
        try:
            res = func(*args, **kwargs)
            if res == expected:
                results["passed"] += 1
            else:
                results["failed"] += 1
                results["details"].append({
                    "func": func.__name__,
                    "expected": expected,
                    "got": res
                })
        except Exception as e:
            results["failed"] += 1
            results["details"].append({
                "func": func.__name__,
                "error": str(e)
            })
    return results
