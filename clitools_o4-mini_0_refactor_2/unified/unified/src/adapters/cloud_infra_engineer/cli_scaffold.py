"""
CLI scaffold for Cloud Infrastructure Engineer.
Includes version bump, package init, publish, hooks, signals, config loading, env override, defaults, docs, validation, secrets, and retry.
"""
import subprocess
import os
import signal
import json
import configparser
import ipaddress
import uuid
import datetime
import adapters.cloud_infra_engineer.keyring as keyring
import adapters.cloud_infra_engineer.toml as toml
import adapters.cloud_infra_engineer.yaml as yaml

def bump_version():
    try:
        out = subprocess.check_output(['git', 'tag', '--sort=-v:refname'], stderr=subprocess.DEVNULL)
        last = out.decode().splitlines()[0]
        if last.startswith('v'):
            ver = last.lstrip('v')
        else:
            ver = '0.0.0'
    except Exception:
        ver = '0.0.0'
    parts = ver.split('.')
    if len(parts) == 3 and all(p.isdigit() for p in parts):
        major, minor, patch = map(int, parts)
    else:
        major, minor, patch = 0, 0, 0
    patch += 1
    return f"{major}.{minor}.{patch}"

def init_package(name, deps, version=None):
    # Initialize project using pyproject.toml
    data = {'project': {'name': name, 'version': version or bump_version(), 'dependencies': deps}}
    content = toml.dumps(data)
    with open('pyproject.toml', 'w') as f:
        f.write(content)
    return True

def publish_package(dist, repo, user=None, password=None):
    # Simplest simulation using subprocess.check_call
    cmd = ['twine', 'upload', dist]
    if repo:
        cmd.insert(2, repo)
    try:
        subprocess.check_call(cmd)
        return True
    except Exception:
        return False

def register_hook(name, script_path):
    hooks_dir = os.path.join('.git', 'hooks')
    os.makedirs(hooks_dir, exist_ok=True)
    hook_file = os.path.join(hooks_dir, name)
    with open(hook_file, 'w') as f:
        f.write(f"#!/bin/sh\nexec {script_path}\n")
    os.chmod(hook_file, 0o755)
    return hook_file

def handle_signals(func):
    def handler(signum, frame):
        print("Operation aborted.")
        raise SystemExit(1)
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def load_config(path):
    low = path.lower()
    if low.endswith('.ini'):
        cp = configparser.ConfigParser()
        cp.read(path)
        return {sec: dict(cp[sec]) for sec in cp.sections()}
    if low.endswith('.json'):
        with open(path, 'r') as f:
            return json.load(f)
    if low.endswith(('.yaml', '.yml')):
        result = {}
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if ':' in line:
                    k, v = line.split(':', 1)
                    v = v.strip()
                    result[k.strip()] = int(v) if v.isdigit() else v
        return result
    if low.endswith('.toml'):
        result = {}
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or line.startswith('['):
                    continue
                if '=' in line:
                    k, v = line.split('=', 1)
                    k = k.strip()
                    val = v.strip().strip("'\"")
                    if val.isdigit():
                        result[k] = int(val)
                    else:
                        result[k] = val
        return result
    return {}

def env_override(config):
    new = {}
    for k, v in config.items():
        envvar = f"CLOUD_{k.upper()}"
        new[k] = os.getenv(envvar, v)
    return new

def compute_default(use_uuid=False, prefix=''):
    if use_uuid:
        return f"{prefix}-{uuid.uuid4()}"
    else:
        ts = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')
        return f"{prefix}-{ts}"

def generate_docs(parser, md_path, man_path):
    # Generate md
    md_raw = parser.format_help()
    # Ensure 'Usage' uppercase for the header
    md = md_raw.replace('usage:', 'Usage:', 1)
    with open(md_path, 'w') as f:
        f.write(md)
    # Generate man
    man = f".TH {parser.prog} 1\n" + parser.format_help()
    with open(man_path, 'w') as f:
        f.write(man)
    return True

def validate_input(val, type_):
    if type_ == 'cidr':
        # Validate network prefix
        try:
            ipaddress.ip_network(val)
        except Exception:
            raise ValueError(f"Invalid CIDR: {val}")
        return val
    if type_ == 'port':
        p = int(val)
        if p < 1 or p > 65535:
            raise ValueError
        return p
    if type_ == 'path':
        abs_path = os.path.abspath(val)
        if not os.path.exists(abs_path):
            raise ValueError
        return abs_path
    if type_ == 'int':
        return int(val)
    if type_ == 'float':
        return float(val)
    if type_ == 'str':
        return str(val)
    raise ValueError(f"Unknown type: {type_}")

def fetch_secret(uri):
    # Use keyring
    val = keyring.get_password(None, uri)
    if val is None:
        raise ValueError
    return val

def retry_call(max_attempts=3, backoff_factor=1):
    import time
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempts = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts >= max_attempts:
                        raise
                    time.sleep(backoff_factor)
        return wrapper
    return decorator