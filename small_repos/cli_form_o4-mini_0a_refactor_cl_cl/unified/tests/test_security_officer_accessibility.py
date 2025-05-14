from security_officer.incident_form.renderer import is_accessibility_mode, enable_accessibility_mode

def test_accessibility_flag():
    # reset by new process
    if is_accessibility_mode():
        # simulate fresh
        pass
    flag = enable_accessibility_mode()
    assert flag is True
