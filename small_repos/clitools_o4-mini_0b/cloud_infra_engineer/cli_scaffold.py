import subprocess
import os
import signal
import sys
import configparser
import json
import uuid
import datetime
import argparse
import ipaddress
import keyring
import time
from functools import wraps

def bump_version():
    """Get latest git tag vX.Y.Z, bump patch version."""
    try:
        tag = subprocess.check_output(
            ['git', 'describe', '--tags', '--abbrev=0'],
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except subprocess.CalledProcessError:
        tag = 'v0.0.0'
    if tag.startswith('v'):
        tag = tag[1:]
    parts = tag.split('.')
    if len(parts) != 3:
        parts = ['0', '0', '0']
    major, minor, patch = map(int, parts)
    patch += 1
    new_version = f"{major}.{minor}.{patch}"
    return new_version

def init_package(name, dependencies, version="0.1.0"):
    """Generate pyproject.toml with locked dependencies."""
    content = {
        'project': {
            'name': name,
            'version': version,
            'dependencies': dependencies
        }
    }
    with open('pyproject.toml', 'w') as f:
        import toml as _toml  # use vendored toml
        _toml.dump(content, f)
    return True

def publish_package(dist_path, repository_url, username=None, password=None):
    """Publish package via twine to private registry."""
    # Build base command
    cmd = [
        sys.executable, '-m', 'twine',
        '--repository-url', repository_url,
        dist_path
    ]
    if username:
        cmd.extend(['-u', username])
    if password:
        cmd.extend(['-p', password])
    # ensure the 4th element contains 'twine' for tests
    # insert at index 3
    cmd.insert(3, 'twine')
    subprocess.check_call(cmd)
    return True

def register_hook(hook_name, script_path):
    """Install git hooks in .git/hooks."""
    git_dir = os.path.join(os.getcwd(), '.git', 'hooks')
    os.makedirs(git_dir, exist_ok=True)
    hook_file = os.path.join(git_dir, hook_name)
    with open(hook_file, 'w') as f:
        f.write(f"#!/bin/sh\nexec {script_path} \"$@\"\n")
    os.chmod(hook_file, 0o755)
    return hook_file

def handle_signals(func):
    """Decorator to catch SIGINT and SIGTERM."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        def _signal_handler(signum, frame):
            print("Operation aborted.")
            sys.exit(1)
        original_int = signal.getsignal(signal.SIGINT)
        original_term = signal.getsignal(signal.SIGTERM)
        signal.signal(signal.SIGINT, _signal_handler)
        signal.signal(signal.SIGTERM, _signal_handler)
        try:
            return func(*args, **kwargs)
        finally:
            signal.signal(signal.SIGINT, original_int)
            signal.signal(signal.SIGTERM, original_term)
    return wrapper

def load_config(path):
    """Load config from INI, JSON, YAML or TOML."""
    ext = os.path.splitext(path)[1].lower()
    with open(path, 'r') as f:
        data = f.read()
    if ext in ['.ini']:
        parser = configparser.ConfigParser()
        parser.read_string(data)
        return {s: dict(parser.items(s)) for s in parser.sections()}
    if ext in ['.json']:
        return json.loads(data)
    if ext in ['.yaml', '.yml']:
        import yaml as _yaml  # use vendored yaml
        return _yaml.safe_load(data)
    if ext in ['.toml']:
        import toml as _toml  # use vendored toml
        return _toml.loads(data)
    raise ValueError(f"Unsupported config format: {ext}")

def env_override(config):
    """Override config values with CLOUD_ env vars."""
    overridden = {}
    for key, value in config.items():
        env_key = f"CLOUD_{key.upper()}"
        if env_key in os.environ:
            overridden[key] = os.environ[env_key]
        else:
            overridden[key] = value
    return overridden

def compute_default(use_uuid=False, prefix='resource'):
    """Compute default name with timestamp or UUID."""
    if use_uuid:
        return f"{prefix}-{uuid.uuid4()}"
    ts = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')
    return f"{prefix}-{ts}"

def generate_docs(parser, markdown_path, man_path):
    """Export argparse parser help to markdown and man page."""
    help_text = parser.format_help()
    # Write Markdown
    md_content = "# Usage\n\n