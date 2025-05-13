"""
Plugin Developer adapter: subcommand registry, config parsing, hooks, telemetry, aliases, caching, and CLI utilities.
"""
import signal

# Subcommand registry
_subcommands = {}

def register_subcommands(arg, cmds=None):
    # Registry mode: namespace and list of (cmd, opts)
    if isinstance(arg, str) and cmds is not None:
        ns = arg
        _subcommands.setdefault(ns, []).extend(cmds)
        return
    # CLI builder mode: arg is subparsers action
    subparsers = arg
    # Create a 'test' command with a 'run' subcommand and flags
    parser = subparsers.add_parser('test')
    sp = parser.add_subparsers(dest='test_cmd')
    cmd_parser = sp.add_parser('run')
    cmd_parser.add_argument('--env')
    cmd_parser.add_argument('--rerun', action='store_true')

def get_subcommands(ns):
    return list(_subcommands.get(ns, []))

# Config parsing with custom tags
def parse_config(base, override):
    def merge(a, b):
        result = {}
        for k in set(a) | set(b):
            if k in a and k in b and isinstance(a[k], dict) and isinstance(b[k], dict):
                result[k] = merge(a[k], b[k])
            elif k in b:
                result[k] = b[k]
            else:
                result[k] = a[k]
        return result
    merged = merge(base, override)
    # process custom '!upper ' tag
    for k, v in list(merged.items()):
        if isinstance(v, str) and v.startswith('!upper '):
            merged[k] = v[len('!upper '):].upper()
    return merged

# Prompt configuration
def configure_prompt(style):
    presets = {
        'default': {'color': 'blue', 'layout': 'simple'},
        'fancy': {'color': 'magenta', 'layout': 'rich'},
    }
    return presets.get(style, presets['default'])

# Signal handlers
_old_handlers = {}

def install_signal_handlers(teardown):
    global _old_handlers
    _old_handlers = {}
    def handler(signum, frame):
        teardown(signum)
    _old_handlers[signal.SIGINT] = signal.signal(signal.SIGINT, handler)
    _old_handlers[signal.SIGTERM] = signal.signal(signal.SIGTERM, handler)
    return _old_handlers

def unregister_signal_handlers():
    for sig, fn in _old_handlers.items():
        signal.signal(sig, fn)

# Plugin hooks
_before = {}
_after = {}

def register_plugin_hooks(when, cmd, fn):
    if when == 'pre_execute':
        _before.setdefault(cmd, []).append(fn)
    elif when == 'post_execute':
        _after.setdefault(cmd, []).append(fn)
    else:
        raise ValueError(f"Invalid hook time: {when}")

def run_hooks(when, cmd, *args, **kwargs):
    hooks = _before if when == 'pre_execute' else _after if when == 'post_execute' else None
    if hooks is None:
        return []
    return [fn(*args, **kwargs) for fn in hooks.get(cmd, [])]

# Telemetry
_telemetry_enabled = False
_events = []

def collect_telemetry(opt_in=False):
    global _telemetry_enabled
    _telemetry_enabled = bool(opt_in)

def record_event(event):
    if _telemetry_enabled:
        _events.append(event)

def get_events():
    return list(_events)

def clear_events():
    _events.clear()

# Alias registration
_aliases = {}

def register_aliases(alias, target):
    if alias in _aliases:
        raise ValueError(f"Alias already registered: {alias}")
    _aliases[alias] = target

def get_alias(alias):
    return _aliases.get(alias)

# Caching decorator
def cache_helper(func):
    cache = {}
    def wrapper(*args):
        if args in cache:
            return cache[args]
        result = func(*args)
        cache[args] = result
        return result
    return wrapper

# Common flags injector
def inject_common_flags(parser):
    import argparse
    parser.add_argument('--version', action='store_true')
    parser.add_argument('-v', '--verbose', action='count', default=0)
    parser.add_argument('--quiet', action='store_true')
    return parser

# Auto-build argument parser
def autobuild_parser(flags):
    import argparse
    parser = argparse.ArgumentParser()
    for flag in flags:
        args = flag.get('args', [])
        kwargs = flag.get('kwargs', {})
        parser.add_argument(*args, **kwargs)
    return parser