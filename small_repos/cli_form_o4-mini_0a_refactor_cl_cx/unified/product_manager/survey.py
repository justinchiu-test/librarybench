import json
import yaml
import inspect
from datetime import datetime

# Accessibility mode flag
ACCESSIBILITY_MODE = False

# Registry for custom field plugins
FIELD_PLUGINS = {}

def validate_input(value, required=False, min_value=None, max_value=None):
    """
    Validate requiredness and numeric range.
    Returns (is_valid, error_message).
    """
    if required and (value is None or (isinstance(value, str) and value.strip() == "")):
        return False, "This field is required"
    if (min_value is not None or max_value is not None) and isinstance(value, (int, float)):
        if min_value is not None and value < min_value:
            return False, f"Value must be between {min_value} and {max_value}"
        if max_value is not None and value > max_value:
            return False, f"Value must be between {min_value} and {max_value}"
    return True, ""

def format_error(message):
    """
    Prefix error messages for inline display.
    """
    return f"[ERROR] {message}"

class TextField:
    """
    Text field with length limit and placeholder.
    """
    def __init__(self, length_limit=None, placeholder=""):
        self.length_limit = length_limit
        self.placeholder = placeholder

    def validate(self, value):
        if self.length_limit is not None and isinstance(value, str):
            if len(value) > self.length_limit:
                return False, f"Input exceeds length limit of {self.length_limit}"
        return True, ""

class DateTimePicker:
    """
    Simple date-time picker stub.
    """
    def pick(self):
        return datetime.now()

class CursesRenderer:
    """
    Stub curses-based renderer.
    """
    def __init__(self):
        self.pages = []

    def render(self, page):
        return f"Rendering {page}"

class WizardLayout:
    """
    Multi-page wizard navigation.
    """
    def __init__(self, pages):
        self.pages = pages
        self.current_index = 0

    def current_page(self):
        if 0 <= self.current_index < len(self.pages):
            return self.pages[self.current_index]
        return None

    def next(self):
        if self.current_index < len(self.pages) - 1:
            self.current_index += 1
        return self.current_page()

    def prev(self):
        if self.current_index > 0:
            self.current_index -= 1
        return self.current_page()

    def is_finished(self):
        return self.current_index >= len(self.pages) - 1

def enable_accessibility_mode():
    """
    Enable accessibility features.
    """
    global ACCESSIBILITY_MODE
    ACCESSIBILITY_MODE = True
    # Also update in any caller module that imported the name
    try:
        frame = inspect.currentframe()
        caller = frame.f_back
        while caller:
            g = caller.f_globals
            if 'ACCESSIBILITY_MODE' in g:
                g['ACCESSIBILITY_MODE'] = True
                break
            caller = caller.f_back
    finally:
        # break reference cycles
        del frame

class AuditLog:
    """
    Simple audit log for changes.
    """
    def __init__(self):
        self._logs = []

    def record(self, user, action):
        entry = {
            "timestamp": datetime.now(),
            "user": user,
            "action": action
        }
        self._logs.append(entry)

    def get_logs(self):
        return list(self._logs)

def register_field_plugin(name, plugin_class):
    """
    Register a custom field plugin by name.
    """
    FIELD_PLUGINS[name] = plugin_class

def export_data(data, format="json"):
    """
    Export data as JSON or YAML.
    """
    if format == "json":
        return json.dumps(data)
    if format == "yaml":
        return yaml.safe_dump(data)
    raise ValueError("Unsupported format")
