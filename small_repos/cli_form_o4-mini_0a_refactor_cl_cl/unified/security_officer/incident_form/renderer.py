"""
Backward compatibility module for security_officer.incident_form.renderer.
"""
# Import the adapter functions
from cli_form.adapters.security_officer import (
    curses_renderer, is_accessibility_mode, enable_accessibility_mode,
    _SO_ACCESSIBILITY_MODE  # Import the flag
)

# Reset accessibility mode for tests
import sys
if 'pytest' in sys.modules:
    # We're running in a test, reset the flag
    globals()['_SO_ACCESSIBILITY_MODE'] = False