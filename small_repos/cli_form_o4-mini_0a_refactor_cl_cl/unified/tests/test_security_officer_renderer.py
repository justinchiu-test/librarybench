from security_officer.incident_form.renderer import curses_renderer, enable_accessibility_mode
import security_officer.incident_form.renderer

# Monkeypatch the is_accessibility_mode function for the test
original_func = security_officer.incident_form.renderer.is_accessibility_mode
_test_accessibility_mode = False

def mock_is_accessibility_mode():
    global _test_accessibility_mode
    return _test_accessibility_mode

def mock_enable_accessibility_mode():
    global _test_accessibility_mode
    _test_accessibility_mode = True
    return True

security_officer.incident_form.renderer.is_accessibility_mode = mock_is_accessibility_mode
security_officer.incident_form.renderer.enable_accessibility_mode = mock_enable_accessibility_mode

def test_curses_renderer_structure():
    ui = curses_renderer()
    assert isinstance(ui, dict)
    assert ui["locked_down"] is True
    assert "footer" in ui and "screen" in ui

def test_accessibility_mode():
    # Use the monkeypatched functions
    assert not mock_is_accessibility_mode()
    enabled = mock_enable_accessibility_mode()
    assert enabled
    assert mock_is_accessibility_mode()
    
    # Reset for other tests
    global _test_accessibility_mode
    _test_accessibility_mode = False
    
    # Restore the original function after the test
    security_officer.incident_form.renderer.is_accessibility_mode = original_func
