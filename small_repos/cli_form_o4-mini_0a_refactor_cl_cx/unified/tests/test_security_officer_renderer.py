from security_officer.incident_form.renderer import curses_renderer, enable_accessibility_mode, is_accessibility_mode

def test_curses_renderer_structure():
    ui = curses_renderer()
    assert isinstance(ui, dict)
    assert ui["locked_down"] is True
    assert "footer" in ui and "screen" in ui

def test_accessibility_mode():
    enabled = enable_accessibility_mode()
    assert enabled
    assert is_accessibility_mode()
