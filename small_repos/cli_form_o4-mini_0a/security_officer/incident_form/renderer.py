import threading

_accessibility_enabled = False

def curses_renderer():
    # Stub for curses-based full-screen renderer
    return {
        "screen": "FULL_SCREEN_CAPTURE",
        "footer": "Press Tab to navigate, Enter to select",
        "locked_down": True
    }

def enable_accessibility_mode():
    global _accessibility_enabled
    _accessibility_enabled = True
    return _accessibility_enabled

def is_accessibility_mode():
    return _accessibility_enabled
