import functools
import getpass
import sys
from contextlib import contextmanager

# Global state
_current_theme = "minimal"
_on_change_callbacks = {}

def ask_text(prompt, min_length=1, max_length=None, placeholder=""):
    full_prompt = f"{prompt}"
    if placeholder:
        full_prompt += f" [{placeholder}]"
    full_prompt += ": "
    text = input(full_prompt)
    length = len(text)
    if length < min_length or (max_length is not None and length > max_length):
        raise ValueError(format_errors(
            f"Input length {length} not in range [{min_length}, {max_length or '∞'}]"
        ))
    return text

def branch_flow(choice, flows):
    if choice not in flows:
        raise ValueError(format_errors(f"Invalid choice '{choice}'"))
    return flows[choice]()

@functools.lru_cache(maxsize=None)
def load_choices_async(loader, *args, **kwargs):
    # loader should be a callable returning list of choices
    return loader(*args, **kwargs)

@contextmanager
def input_line_fallback():
    # Fallback CLI mode uses standard input/output
    class Fallback:
        def __init__(self):
            self.mode = "fallback"
        def __repr__(self):
            return "<FallbackCLI mode=fallback>"
    yield Fallback()

def review_submission(data_dict):
    # In real use would display and allow edits; here just return the dict
    return dict(data_dict)

def ask_password(prompt="Password", show_strength=False, toggle_reveal=False):
    return getpass.getpass(f"{prompt}: ")

def select_choices(options, default=None):
    if default is None:
        default = []
    prompt = "Select options by comma-separated indices"
    if default:
        prompt += f" [{','.join(map(str, default))}]"
    prompt += ": "
    resp = input(prompt)
    if not resp and default:
        indices = default
    else:
        indices = [int(x.strip()) for x in resp.split(",") if x.strip().isdigit()]
    selected = []
    for i in indices:
        if i < 0 or i >= len(options):
            raise ValueError(format_errors(f"Index {i} out of range"))
        selected.append(options[i])
    return selected

def set_renderer_theme(theme):
    global _current_theme
    if theme not in ("minimal", "high-contrast"):
        raise ValueError(format_errors(f"Unknown theme '{theme}'"))
    _current_theme = theme
    return _current_theme

def register_on_change(field_name, callback):
    if field_name not in _on_change_callbacks:
        _on_change_callbacks[field_name] = []
    _on_change_callbacks[field_name].append(callback)

def trigger_change(field_name, value):
    # Helper to simulate change
    for cb in _on_change_callbacks.get(field_name, []):
        cb(value)

def format_errors(message):
    # Wrap message in red ANSI codes
    return f"\033[91mERROR: {message}\033[0m"
