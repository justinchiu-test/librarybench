"""
Plugin Developer CLI support.
"""
import signal
import argparse
from functools import wraps

# Subcommands registry
_subcommands = {}

# Signal handlers storage
_old_signal_handlers = {}

# Plugin hooks storage
_event_hooks = {'pre_execute': {}, 'post_execute': {}}

# Telemetry storage
_events = []
_telemetry_enabled = False

# Aliases storage
_aliases = {}

def register_subcommands(namespace, cmds):
    if namespace not in _subcommands:
        _subcommands[namespace] = []
    _subcommands[namespace].extend(cmds)

def get_subcommands(namespace):
    return list(_subcommands.get(namespace, []))

def parse_config(base, override):
    def merge(b, o):
        result = dict(b)
        for key, val in o.items():
            if isinstance(val, str) and val.startswith('!upper '):
                result[key] = val[len('!upper '):].upper()
            elif key in b and isinstance(b[key], dict) and isinstance(val, dict):
                result[key] = merge(b[key], val)
            else:
                result[key] = val
        return result
    return merge(base, override)

def configure_prompt(name):
    prompts = {
        'default': {'color': 'blue', 'layout': 'simple'},
        'fancy': {'color': 'magenta', 'layout': 'rich'},
    }
    return prompts.get(name, prompts['default'])

def install_signal_handlers(teardown):
    handlers = {}
    def make_handler(cb):
        def handler(signum, frame):
            cb(signum)
        return handler
    for sig in (signal.SIGINT, signal.SIGTERM):
        old = signal.getsignal(sig)
        handlers[sig] = old
        signal.signal(sig, make_handler(teardown))
    global _old_signal_handlers
    _old_signal_handlers = handlers.copy()
    return handlers

def unregister_signal_handlers():
    global _old_signal_handlers
    for sig, old in _old_signal_handlers.items():
        signal.signal(sig, old)
    _old_signal_handlers.clear()

def register_plugin_hooks(event, cmd, hook):
    if event not in _event_hooks:
        raise ValueError(f"Invalid event: {event}")
    if cmd not in _event_hooks[event]:
        _event_hooks[event][cmd] = []
    _event_hooks[event][cmd].append(hook)

def run_hooks(event, cmd, arg):
    results = []
    for hook in _event_hooks.get(event, {}).get(cmd, []):
        results.append(hook(arg))
    return results

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

def register_aliases(alias, command):
    if alias in _aliases:
        raise ValueError(f"Alias already registered: {alias}")
    _aliases[alias] = command

def get_alias(alias):
    return _aliases.get(alias)

def cache_helper(func):
    cache = {}
    @wraps(func)
    def wrapper(*args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    return wrapper

def inject_common_flags(parser):
    parser.add_argument('--version', action='store_true')
    parser.add_argument('-v', '--verbose', action='count', default=0)
    parser.add_argument('--quiet', action='store_true')
    return parser

def autobuild_parser(flags):
    parser = argparse.ArgumentParser()
    for f in flags:
        args = f.get('args', [])
        kwargs = f.get('kwargs', {})
        parser.add_argument(*args, **kwargs)
    return parser