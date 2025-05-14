"""
Backward compatibility module for product_manager.survey.
"""
from cli_form.adapters.product_manager import (
    validate_input, format_error, TextField, DateTimePicker,
    CursesRenderer, WizardLayout, enable_accessibility_mode,
    AuditLog, register_field_plugin, export_data
)

# Import globals for backward compatibility
from cli_form.plugins.registry import FIELD_PLUGINS

# Define global ACCESSIBILITY_MODE for backward compatibility
ACCESSIBILITY_MODE = False

# Override enable_accessibility_mode to update our global
_original_enable_accessibility_mode = enable_accessibility_mode

def enable_accessibility_mode():
    global ACCESSIBILITY_MODE
    result = _original_enable_accessibility_mode()
    ACCESSIBILITY_MODE = True
    return result