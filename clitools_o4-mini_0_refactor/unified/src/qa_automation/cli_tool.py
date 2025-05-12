"""
QA Automation CLI tool implementation.
"""
import os
import signal
import json
import configparser
import argparse

# Hook storage
_before_hooks = []
_after_hooks = []

# Telemetry storage
telemetry_data = []
_telemetry_enabled = False

# Aliases storage
aliases = {}

# Cache directory (can be overridden)
cache_dir = os.getcwd()

class CacheHelper:
    def __init__(self, use_disk=False):
        self.use_disk = use_disk
        self.store = {}
        if self.use_disk:
            os.makedirs(cache_dir, exist_ok=True)

    def set(self, key, value):
        self.store[key] = value
        if self.use_disk:
            path = os.path.join(cache_dir, f"{key}.json")
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(value, f)

    def get(self, key):
        if key in self.store:
            return self.store[key]
        if self.use_disk:
            path = os.path.join(cache_dir, f"{key}.json")
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    val = json.load(f)
                    self.store[key] = val
                    return val
            except Exception:
                return None
        return None

def inject_common_flags(parser):
    parser.add_argument('--version', action='store_true')
    parser.add_argument('-v', '--verbose', action='count', default=0)
    parser.add_argument('--quiet', action='store_true')
    return parser

def autobuild_parser(spec):
    parser = argparse.ArgumentParser()
    for item in spec:
        name = item.get('name')
        kwargs = {k: v for k, v in item.items() if k != 'name'}
        if name:
            parser.add_argument(name, **kwargs)
    return parser

def parse_config(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == '.json':
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    elif ext in ('.ini', '.cfg'):
        cp = configparser.ConfigParser()
        cp.read(path)
        config = {}
        for sec in cp.sections():
            config[sec] = dict(cp[sec])
        return config
    elif ext in ('.yaml', '.yml'):
        data = {}
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if ':' in line:
                    key, val = line.split(':', 1)
                    val = val.strip()
                    if val.isdigit():
                        data[key.strip()] = int(val)
                    else:
                        data[key.strip()] = val
        return data
    elif ext == '.toml':
        data = {}
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, val = line.split('=', 1)
                    val = val.strip()
                    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                        data[key.strip()] = val[1:-1]
                    elif val.isdigit():
                        data[key.strip()] = int(val)
                    else:
                        data[key.strip()] = val
        return data
    return {}

def configure_prompt(prompt):
    # display prompt
    prompt_text = f"{prompt}?"
    print(prompt_text)
    # pass prompt to input(), so overridden input(prompt) works as expected
    ans = input(prompt_text)
    return ans.strip().lower() in ('y', 'yes')

def install_signal_handlers(cleanup):
    old = {}
    for sig in (signal.SIGINT, signal.SIGTERM):
        old[sig] = signal.getsignal(sig)
        def handler(signum, frame, cleanup=cleanup):
            print("Testing aborted")
            cleanup()
        signal.signal(sig, handler)
    return old

def register_plugin_hooks(before=None, after=None):
    if before is not None:
        _before_hooks.append(before)
    if after is not None:
        _after_hooks.append(after)

def collect_telemetry(opt_in):
    global _telemetry_enabled
    _telemetry_enabled = bool(opt_in)

def record_telemetry(event):
    if _telemetry_enabled:
        telemetry_data.append(event)

def register_aliases(mapping):
    aliases.update(mapping)

def register_subcommands(subparsers):
    # primary 'test' command
    test_parser = subparsers.add_parser('test')
    test_sub = test_parser.add_subparsers(dest='test_cmd')
    run_parser = test_sub.add_parser('run')
    run_parser.add_argument('--env', required=True)
    run_parser.add_argument('--rerun', action='store_true')
    return subparsers