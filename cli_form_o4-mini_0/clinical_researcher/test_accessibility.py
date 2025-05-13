from form_system.renderer import CursesRenderer
from form_system.accessibility import enable_accessibility_mode

def test_enable_accessibility_mode():
    rend = CursesRenderer({})
    assert not rend.accessibility_mode
    enable_accessibility_mode(rend, True)
    assert rend.accessibility_mode
    enable_accessibility_mode(rend, False)
    assert not rend.accessibility_mode
