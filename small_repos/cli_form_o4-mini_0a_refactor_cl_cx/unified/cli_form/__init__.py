"""
cli_form: A Unified Command-Line Form Builder

This package provides a flexible framework for building interactive
command-line forms with fields, validation, and layout controls.
"""

from cli_form.fields import TextField, DateTimePicker
from cli_form.validation import validate_input
from cli_form.renderer import CursesRenderer
from cli_form.layout import WizardLayout
from cli_form.errors import format_error
from cli_form.accessibility import enable_accessibility_mode
from cli_form.audit import audit_log
from cli_form.plugins import register_field_plugin
from cli_form.exporter import export_data

__version__ = '1.0.0'