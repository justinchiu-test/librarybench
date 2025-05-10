import signal
import argparse
from functools import lru_cache

# Subcommands registry
_subcommands = {}

def register_subcommands(namespace, commands):
    """
    Register commands under a namespace with their flags.
    commands: list of tuples (command_name, flags_list)
    """
    if namespace not in _subcommands:
        _subcommands[namespace] = []
    _subcommands[namespace].extend(commands)

def get_subcommands(namespace):
    return _subcommands.get(namespace, [])

# Config parsing with merge and custom YAML-like tag handling
def parse_config(base_config, override_config):
    def merge(a, b):
        for key, val in b.items():
            if key in a and isinstance(a[key], dict) and isinstance(val, dict):
                merge(a[key], val)
            else:
                a[key] = val
        return a
    # Handle a simple custom tag !upper
    processed = {}
    for key, val in override_config.items():
        if isinstance(val, str) and val.startswith('!upper '):
            processed[key] = val[len('!upper '):].upper()
        else:
            processed[key] = val
    merged = merge(dict(base_config), processed)
    return merged

# Prompt configuration
_prompt_themes = {
    'default': {'color': 'blue', 'layout': 'simple'},
    'fancy': {'color': 'magenta', 'layout': 'rich'}
}

def configure_prompt(theme):
    return _prompt_themes.get(theme, _prompt_themes['default'])

# Signal handlers installation
_signal_handlers = []

def install_signal_handlers(teardown_func):
    """
    Install handlers for SIGINT and SIGTERM to call teardown_func(signum).
    Returns list of (signal, previous_handler).
    """
    def handler(signum, frame):
        teardown_func(signum)
    # Install and store previous handlers
    for sig in (signal.SIGINT, signal.SIGTERM):
        prev = signal.signal(sig, handler)
        _signal_handlers.append((sig, prev))
    # Return a copy so that later unregister doesn't clear caller's list
    return list(_signal_handlers)

def unregister_signal_handlers():
    """
    Restore previous signal handlers.
    """
    for sig, prev in _signal_handlers:
        signal.signal(sig, prev)
    _signal_handlers.clear()

# Plugin hooks registry
_hooks = {
    'pre_execute': {},
    'post_execute': {}
}

def register_plugin_hooks(hook_type, command, func):
    if hook_type not in _hooks:
        raise ValueError('Invalid hook type')
    if command not in _hooks[hook_type]:
        _hooks[hook_type][command] = []
    _hooks[hook_type][command].append(func)

def run_hooks(hook_type, command, *args, **kwargs):
    results = []
    for func in _hooks.get(hook_type, {}).get(command, []):
        results.append(func(*args, **kwargs))
    return results

# Telemetry collection
_telemetry_enabled = False
_telemetry_events = []

def collect_telemetry(opt_in=False):
    global _telemetry_enabled
    _telemetry_enabled = opt_in

def record_event(event):
    if _telemetry_enabled:
        _telemetry_events.append(event)

def get_events():
    return list(_telemetry_events)

def clear_events():
    _telemetry_events.clear()

# Alias registration
_aliases = {}

def register_aliases(alias, command):
    if alias in _aliases:
        raise ValueError('Alias conflict')
    _aliases[alias] = command

def get_alias(alias):
    return _aliases.get(alias)

# Caching helper decorator
def cache_helper(func=None):
    if func is None:
        return lru_cache(maxsize=None)
    return lru_cache(maxsize=None)(func)

# Common flags injection
def inject_common_flags(parser):
    parser.add_argument('--version', action='store_true', help='show version')
    parser.add_argument('--verbose', '-v', action='count', default=0, help='increase verbosity')
    parser.add_argument('--quiet', action='store_true', help='suppress output')
    return parser

# Autobuild parser from declarative flags
def autobuild_parser(flags):
    parser = argparse.ArgumentParser()
    for f in flags:
        args = f.get('args', [])
        kwargs = f.get('kwargs', {})
        parser.add_argument(*args, **kwargs)
    return parser
