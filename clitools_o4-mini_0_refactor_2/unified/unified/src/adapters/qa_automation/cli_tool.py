"""
QA Automation CLI adapter: config, prompts, signals, plugins, telemetry, aliases, caching, and CLI builder.
"""
import os
import signal
import json
import configparser

# Config parsing
def parse_config(path):
    low = path.lower()
    if low.endswith('.json'):
        with open(path, 'r') as f:
            return json.load(f)
    if low.endswith('.ini'):
        cp = configparser.ConfigParser()
        cp.read(path)
        return {sec: dict(cp[sec]) for sec in cp.sections()}
    if low.endswith(('.yaml', '.yml')):
        # simple YAML
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
        # simple TOML
        result = {}
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or line.startswith('['):
                    continue
                if '=' in line:
                    k, v = line.split('=', 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if v.isdigit():
                        result[k] = int(v)
                    else:
                        result[k] = v
        return result
    # unknown
    return {}

# Prompt configuration
def configure_prompt(message):
    print(message)
    ans = input(message)
    return ans.strip().lower().startswith('y')

# Signal handlers
_old_handlers = {}

def install_signal_handlers(cleanup):
    global _old_handlers
    _old_handlers = {}
    def handler(signum, frame):
        print("Testing aborted")
        cleanup()
    _old_handlers[signal.SIGINT] = signal.signal(signal.SIGINT, handler)
    _old_handlers[signal.SIGTERM] = signal.signal(signal.SIGTERM, handler)
    return _old_handlers

# Plugin hooks
_before_hooks = []
_after_hooks = []

def register_plugin_hooks(before=None, after=None):
    if before:
        _before_hooks.append(before)
    if after:
        _after_hooks.append(after)

# Telemetry
telemetry_data = []
_telemetry_enabled = False

def collect_telemetry(opt_in):
    global _telemetry_enabled
    _telemetry_enabled = bool(opt_in)

def record_telemetry(event):
    if _telemetry_enabled:
        telemetry_data.append(event)

# Alias registration
aliases = {}

def register_aliases(mapping):
    aliases.update(mapping)

# Caching helper
import json as _json
import os as _os

cache_dir = os.path.expanduser('~')

class CacheHelper:
    def __init__(self, use_disk=False):
        self.use_disk = use_disk
        self.store = {}

    def set(self, key, value):
        self.store[key] = value
        if self.use_disk:
            _os.makedirs(cache_dir, exist_ok=True)
            path = _os.path.join(cache_dir, f"{key}.json")
            with open(path, 'w') as f:
                _json.dump(value, f)

    def get(self, key):
        if key in self.store:
            return self.store[key]
        if self.use_disk:
            path = _os.path.join(cache_dir, f"{key}.json")
            if _os.path.exists(path):
                with open(path, 'r') as f:
                    val = _json.load(f)
                self.store[key] = val
                return val
        return None

# Common flags injector
def inject_common_flags(parser):
    parser.add_argument('--version', action='store_true')
    parser.add_argument('-v', '--verbose', action='count', default=0)
    parser.add_argument('--quiet', action='store_true')
    return parser

# Auto-build argument parser
def autobuild_parser(specs):
    import argparse
    parser = argparse.ArgumentParser()
    for item in specs:
        name = item.get('name')
        kwargs = {k: v for k, v in item.items() if k != 'name'}
        parser.add_argument(name, **kwargs)
    return parser

# CLI builder
def register_subcommands(arg):
    subparsers = arg
    parser = subparsers.add_parser('test')
    sp = parser.add_subparsers(dest='test_cmd')
    cmd_parser = sp.add_parser('run')
    cmd_parser.add_argument('--env')
    cmd_parser.add_argument('--rerun', action='store_true')