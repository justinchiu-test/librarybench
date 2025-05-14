"""
Adapter for clinical_researcher.form_system backward compatibility.
"""
from ..core.fields import TextField as BaseTextField, DateTimePicker as BaseDateTimePicker
from ..core.validation import validate_input as base_validate_input
from ..core.renderer import CursesRenderer as BaseCursesRenderer
from ..core.layout import WizardLayout as BaseWizardLayout
from ..core.accessibility import enable_accessibility_mode as base_enable_accessibility_mode
from ..core.errors import format_error as base_format_error
from ..extensions.export import export_data as base_export_data
from ..extensions.audit import AuditLog as BaseAuditLog
from ..plugins.registry import register_field_plugin as base_register_field_plugin
from ..plugins.registry import get_field_plugin as base_get_field_plugin
import time
from datetime import datetime


# Field types
class TextField(BaseTextField):
    def __init__(self, name, regex=None, max_length=None, placeholder=''):
        super().__init__(name=name, regex=regex, max_length=max_length, placeholder=placeholder)
        
    def validate(self, value):
        valid, error = super().validate(value)
        if not valid:
            raise ValueError(error)
        return valid


class DateTimePicker(BaseDateTimePicker):
    def pick_date(self, date_str: str) -> str:
        """Parse date string and return formatted date without time."""
        date_obj = super().pick_date(date_str)
        return date_str


# Validation
def validate_input(values):
    return base_validate_input(values)


# Layout
class WizardLayout(BaseWizardLayout):
    pass


# Renderer
class CursesRenderer(BaseCursesRenderer):
    pass


# Error formatting
def format_error(field, message, highlight=True):
    return base_format_error(field, message, highlight)


# Accessibility
def enable_accessibility_mode(renderer, enabled=True):
    return base_enable_accessibility_mode(renderer, enabled)


# Audit logging
class AuditLog(BaseAuditLog):
    def __init__(self):
        super().__init__()
        self._history = []
    
    def record(self, field, old, new):
        """Record a field change in the audit log."""
        entry = {
            'timestamp': time.time(),
            'field': field,
            'old': old,
            'new': new
        }
        self._history.append(entry)
    
    def get_history(self):
        """Get the full audit history."""
        return self._history
    
    # Maintain compatibility with base class
    def get_logs(self):
        return super().get_logs()


# Export
def export_data(data, format='json'):
    return base_export_data(data, format=format)


# Plugin system
def register_field_plugin(name, plugin_class):
    """
    Register a field plugin, with CR-specific behavior for duplicates.
    
    In the clinical_researcher implementation, registering a duplicate plugin
    raises a KeyError, so we need to reproduce that behavior.
    """
    # Import here to avoid circular imports
    from ..plugins.registry import FIELD_PLUGINS
    
    # Check for duplicates explicitly
    if name in FIELD_PLUGINS:
        raise KeyError(f"Plugin '{name}' is already registered")
        
    return base_register_field_plugin(name, plugin_class)


def get_field_plugin(name):
    return base_get_field_plugin(name)