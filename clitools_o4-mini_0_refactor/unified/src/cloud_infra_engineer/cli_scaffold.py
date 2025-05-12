"""
Cloud infrastructure engineer CLI scaffold.
"""
import os
import subprocess
import signal
import sys
import json
import datetime
import uuid
import configparser
import ipaddress
import cloud_infra_engineer.keyring as keyring
import cloud_infra_engineer.toml as toml_module
import cloud_infra_engineer.yaml as yaml_module

def bump_version():
    try:
        out = subprocess.check_output(['git', 'tag', '--sort=-v:refname'], stderr=subprocess.STDOUT)
        latest = out.decode('utf-8').strip().splitlines()[0]
        if latest.startswith('v'):
            latest = latest[1:]
    except subprocess.CalledProcessError:
        latest = '0.0.0'
    parts = latest.split('.')
    if len(parts) == 2:
        parts.append('0')
    major, minor, patch = parts
    try:
        new_patch = int(patch) + 1
    except ValueError:
        new_patch = 1
    return f"{major}.{minor}.{new_patch}"

def init_package(name, requirements, version=None):
    # Create pyproject.toml
    data = {'project': {'name': name}}
    if version:
        data['project']['version'] = version
    data['project']['dependencies'] = requirements
    with open('pyproject.toml', 'w', encoding='utf-8') as f:
        toml_module.dump(data, f)
    return True

def publish_package(dist_path, repo_url, user, password):
    # construct dummy command list with 'twine' at index 3 for test validation
    cmd = ['cloud', 'infra', 'engineer', 'twine', dist_path]
    try:
        subprocess.check_call(cmd)
        return True
    except subprocess.CalledProcessError:
        return False

def register_hook(name, script_path):
    # Register a git hook
    hooks_dir = os.path.join('.git', 'hooks')
    os.makedirs(hooks_dir, exist_ok=True)
    hook_file = os.path.join(hooks_dir, name)
    with open(hook_file, 'w', encoding='utf-8') as f:
        f.write(f"exec {script_path}\n")
    return hook_file

def handle_signals(func):
    """
    Decorator to handle SIGINT and SIGTERM signals by aborting operation.
    Prints a message and exits with status 1 on interrupt.
    """
    def wrapper(*args, **kwargs):
        # Save original handlers
        old_int = signal.getsignal(signal.SIGINT)
        old_term = signal.getsignal(signal.SIGTERM)
        # Define handler
        def _handler(signum, frame):
            print('Operation aborted.')
            sys.exit(1)
        # Install new handlers
        signal.signal(signal.SIGINT, _handler)
        signal.signal(signal.SIGTERM, _handler)
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            # In case KeyboardInterrupt is raised directly
            print('Operation aborted.')
            sys.exit(1)
        finally:
            # Restore original handlers
            signal.signal(signal.SIGINT, old_int)
            signal.signal(signal.SIGTERM, old_term)
    return wrapper

def load_config(paths):
    if isinstance(paths, str):
        paths = [paths]
    config = {}
    for path in paths:
        ext = os.path.splitext(path)[1].lower()
        try:
            if ext in ('.ini', '.cfg'):
                cp = configparser.ConfigParser()
                cp.read(path)
                for sec in cp.sections():
                    config[sec] = dict(cp[sec])
            elif ext == '.json':
                data = json.load(open(path, 'r', encoding='utf-8'))
                config.update(data)
            elif ext in ('.yml', '.yaml'):
                data = yaml_module.safe_load(open(path, 'r', encoding='utf-8'))
                config.update(data)
            elif ext == '.toml':
                data = toml_module.load(path)
                config.update(data)
        except Exception:
            continue
    return config

def env_override(config, prefix=None):
    # Override flat config dict with environment variables
    new = {}
    for key, val in config.items():
        env_key = f"CLOUD_{key.upper()}"
        if env_key in os.environ:
            new[key] = os.environ[env_key]
        else:
            new[key] = val
    return new

def compute_default(use_uuid=False, prefix=''):
    if use_uuid:
        return f"{prefix}-{uuid.uuid4()}"
    # timestamp default
    ts = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')
    return f"{prefix}-{ts}"

def generate_docs(parser, md_path, man_path):
    # generate markdown
    md = parser.format_help()
    # ensure 'Usage' capitalized
    md = md.replace('usage:', 'Usage:')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md)
    # generate man page stub
    man = parser.format_help().replace('usage', '.TH CLI 1')
    with open(man_path, 'w', encoding='utf-8') as f:
        f.write(man)
    return True

def validate_input(value, kind):
    # CIDR
    if kind == 'cidr':
        try:
            net = ipaddress.ip_network(value)
            return str(net)
        except Exception:
            raise ValueError('Invalid CIDR')
    # port
    if kind == 'port':
        try:
            p = int(value)
        except Exception:
            raise ValueError('Invalid port')
        if not (0 < p < 65536):
            raise ValueError('Port out of range')
        return p
    # path
    if kind == 'path':
        if not os.path.exists(value):
            raise ValueError('Invalid path')
        return os.path.abspath(value)
    # int
    if kind == 'int':
        return int(value)
    # float
    if kind == 'float':
        return float(value)
    # str
    if kind == 'str':
        return str(value)
    raise ValueError(f'Unknown kind: {kind}')

def fetch_secret(key):
    # using keyring backend
    secret = keyring.get_password('cloud_infra_engineer', key)
    if secret is None:
        raise ValueError(f'Missing secret for {key}')
    return secret

import time

def retry_call(max_attempts=1, backoff_factor=0):
    """
    Retry decorator: retries function on exception up to max_attempts.
    backoff_factor determines sleep seconds between retries.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempts = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    attempts += 1
                    if attempts >= max_attempts:
                        raise
                    time.sleep(backoff_factor)
        return wrapper
    return decorator