import re
import getpass
from threading import Lock

# Globals for theme, cache, callbacks
THEME = {
    'mode': 'default',
    'colors': {
        'error': '\033[91m',
        'reset': '\033[0m'
    }
}
_CACHE = {}
_CACHE_LOCK = Lock()
_CALLBACKS = {}

class ValidationError(Exception):
    pass

def format_errors(field_name, error_key, message):
    """
    Returns a formatted error string with color based on theme.
    """
    color = THEME['colors'].get('error', '')
    reset = THEME['colors'].get('reset', '')
    return f"{color}[{field_name}:{error_key}] {message}{reset}"

def register_on_change(field_name, callback):
    """
    Register a callback to be called when a field changes.
    """
    _CALLBACKS.setdefault(field_name, []).append(callback)

def _trigger_on_change(field_name, value):
    """
    Internal: trigger callbacks for a field.
    """
    for cb in _CALLBACKS.get(field_name, []):
        cb(field_name, value)

def set_renderer_theme(theme_name):
    """
    Set global renderer theme.
    """
    if theme_name == 'dark':
        THEME['mode'] = 'dark'
        THEME['colors']['error'] = '\033[95m'
    elif theme_name == 'high-contrast':
        THEME['mode'] = 'high-contrast'
        THEME['colors']['error'] = '\033[93m'
    else:
        THEME['mode'] = 'default'
        THEME['colors']['error'] = '\033[91m'

def ask_text(prompt, placeholder=None, length_limit=None, regex=None, field_name=None):
    """
    Secure single-line input with validations.
    """
    hint = f" ({placeholder})" if placeholder else ""
    value = input(f"{prompt}{hint}: ").strip()
    if length_limit is not None and len(value) > length_limit:
        msg = format_errors(field_name or prompt, 'length_exceeded',
                            f"Input exceeds length limit of {length_limit}")
        raise ValidationError(msg)
    if regex is not None:
        if not re.fullmatch(regex, value):
            msg = format_errors(field_name or prompt, 'invalid_format',
                                f"Input does not match required format")
            raise ValidationError(msg)
    if field_name:
        _trigger_on_change(field_name, value)
    return value

def branch_flow(choice, branches, default=None):
    """
    Return branch fields based on choice.
    """
    return branches.get(choice, default or [])

def load_choices_async(loader_func, cache_key):
    """
    Load choices with caching and spinner simulation.
    """
    with _CACHE_LOCK:
        if cache_key in _CACHE:
            return _CACHE[cache_key]
    # Spinner simulation
    print("Loading...", end='', flush=True)
    result = loader_func()
    print(" done")
    with _CACHE_LOCK:
        _CACHE[cache_key] = result
    return result

def input_line_fallback(prompt):
    """
    Simple input fallback.
    """
    return input(f"{prompt}: ")

def review_submission(data, editable_fields):
    """
    Display summary and allow edits.
    """
    result = data.copy()
    print("Review Submission:")
    for key, value in result.items():
        print(f"- {key}: {value}")
    for field in editable_fields:
        new = input(f"Edit {field} (leave blank to keep current '{result[field]}'): ").strip()
        if new:
            result[field] = new
    return result

def ask_password(prompt, strength_meter=False, toggle=False, field_name=None):
    """
    Obscured entry for passwords.
    """
    pwd = getpass.getpass(f"{prompt}: ")
    if strength_meter:
        strength = len(pwd)
        print(f"Strength: {strength} characters")
    if field_name:
        _trigger_on_change(field_name, pwd)
    return pwd

def select_choices(prompt, choices, multi=False):
    """
    Select one or multiple choices.
    """
    print(prompt)
    for idx, item in enumerate(choices, 1):
        print(f"{idx}. {item}")
    if multi:
        sel = input("Enter numbers separated by comma: ").strip()
        indices = [int(s) for s in sel.split(',') if s.strip().isdigit()]
        return [choices[i-1] for i in indices if 1 <= i <= len(choices)]
    else:
        sel = input("Enter number: ").strip()
        idx = int(sel)
        if 1 <= idx <= len(choices):
            return choices[idx-1]
        else:
            raise ValidationError(format_errors(prompt, 'invalid_choice', 'Choice out of range'))
