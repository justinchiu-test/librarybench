import argparse
import configparser
import json
import signal
import os
import tempfile
import pickle

# Globals
_before_hooks = []
_after_hooks = []
aliases = {}
telemetry_data = []
telemetry_enabled = False
cache_dir = os.path.join(tempfile.gettempdir(), 'cli_tool_cache')
os.makedirs(cache_dir, exist_ok=True)


def register_subcommands(parser):
    test_parser = parser.add_parser('test', help='Test commands')
    subparsers = test_parser.add_subparsers(dest='test_cmd')
    for cmd in ['run', 'smoke', 'report']:
        sp = subparsers.add_parser(cmd, help=f'test {cmd}')
        sp.add_argument('--env', default='dev', help='Environment')
        sp.add_argument('--rerun', action='store_true', help='Rerun tests')
    return parser


def parse_config(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == '.json':
        with open(path) as f:
            data = json.load(f)
    elif ext == '.ini':
        cfg = configparser.ConfigParser()
        cfg.read(path)
        data = {section: dict(cfg[section]) for section in cfg.sections()}
    elif ext in ('.yaml', '.yml'):
        # Try PyYAML if available, otherwise simple key: value parser
        try:
            import yaml
            with open(path) as f:
                data = yaml.safe_load(f) or {}
        except ImportError:
            data = {}
            with open(path) as f:
                for raw in f:
                    line = raw.strip()
                    if not line or line.startswith('#'):
                        continue
                    if ':' not in line:
                        continue
                    key, val = line.split(':', 1)
                    key = key.strip()
                    val = val.strip()
                    # strip quotes
                    if ((val.startswith('"') and val.endswith('"')) or
                        (val.startswith("'") and val.endswith("'"))):
                        val = val[1:-1]
                    # try integer conversion
                    try:
                        val = int(val)
                    except ValueError:
                        pass
                    data[key] = val
    elif ext == '.toml':
        # Try toml library if available, otherwise simple key = value parser
        try:
            import toml
            with open(path) as f:
                data = toml.load(f) or {}
        except ImportError:
            data = {}
            with open(path) as f:
                for raw in f:
                    line = raw.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' not in line:
                        continue
                    key, val = line.split('=', 1)
                    key = key.strip()
                    val = val.strip()
                    # strip quotes
                    if ((val.startswith('"') and val.endswith('"')) or
                        (val.startswith("'") and val.endswith("'"))):
                        val = val[1:-1]
                    # try integer conversion
                    try:
                        val = int(val)
                    except ValueError:
                        pass
                    data[key] = val
    else:
        raise ValueError('Unsupported config format')
    return data


def configure_prompt(summary):
    print(summary)
    resp = input('Continue with rerun? [Y/n] ')
    return not resp.lower().startswith('n')


def install_signal_handlers(cleanup_func):
    def handler(signum, frame):
        cleanup_func()
        print('Testing aborted')
    old = {}
    for sig in (signal.SIGINT, signal.SIGTERM):
        old[sig] = signal.signal(sig, handler)
    return old


def register_plugin_hooks(before=None, after=None):
    if before:
        _before_hooks.append(before)
    if after:
        _after_hooks.append(after)


def collect_telemetry(enabled=True):
    global telemetry_enabled
    telemetry_enabled = enabled


def record_telemetry(event):
    if telemetry_enabled:
        telemetry_data.append(event)


def register_aliases(maps):
    aliases.update(maps)


class CacheHelper:
    def __init__(self, use_disk=False):
        self.store = {}
        self.use_disk = use_disk
        self.dir = cache_dir

    def set(self, key, value):
        self.store[key] = value
        if self.use_disk:
            path = os.path.join(self.dir, key + '.pkl')
            with open(path, 'wb') as f:
                pickle.dump(value, f)

    def get(self, key):
        if key in self.store:
            return self.store[key]
        if self.use_disk:
            path = os.path.join(self.dir, key + '.pkl')
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    val = pickle.load(f)
                    self.store[key] = val
                    return val
        return None


def inject_common_flags(parser):
    parser.add_argument('--version', action='version', version='1.0')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet output')


def autobuild_parser(spec):
    parser = argparse.ArgumentParser()
    for arg in spec:
        name = arg['name']
        opts = {}
        if 'type' in arg:
            opts['type'] = arg['type']
        if 'choices' in arg:
            opts['choices'] = arg['choices']
        if 'default' in arg:
            opts['default'] = arg['default']
        if 'help' in arg:
            opts['help'] = arg['help']
        parser.add_argument(name, **opts)
    return parser
