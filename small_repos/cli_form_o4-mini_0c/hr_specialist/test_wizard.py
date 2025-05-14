import os
import json
import pytest
from wizard import OnboardingWizard

def test_real_time_validate_email():
    wiz = OnboardingWizard()
    assert wiz.real_time_validate("user@example.com", "email")
    assert not wiz.real_time_validate("userexample.com", "email")

def test_real_time_validate_ssn():
    wiz = OnboardingWizard()
    assert wiz.real_time_validate("123-45-6789", "ssn")
    assert not wiz.real_time_validate("123456789", "ssn")

def test_real_time_validate_phone():
    wiz = OnboardingWizard()
    assert wiz.real_time_validate("+12345678901", "phone")
    assert wiz.real_time_validate("1234567890", "phone")
    assert not wiz.real_time_validate("123-4567", "phone")

def test_apply_skip_logic_full_time():
    wiz = OnboardingWizard()
    wiz.context["employment_type"] = "full-time"
    skip = wiz.apply_skip_logic()
    assert skip["pension_plan"] is False

def test_apply_skip_logic_part_time():
    wiz = OnboardingWizard()
    wiz.context["employment_type"] = "part-time"
    skip = wiz.apply_skip_logic()
    assert skip["pension_plan"] is True

def test_navigate_next_prev():
    wiz = OnboardingWizard()
    assert wiz.current_page == "Personal Info"
    nxt = wiz.navigate("next")
    assert nxt == "Benefits"
    prev = wiz.navigate("prev")
    assert prev == "Personal Info"

def test_navigate_boundary_next():
    wiz = OnboardingWizard()
    # go to last
    wiz.current_page = "Review"
    res = wiz.navigate("next")
    assert res == "Review"

def test_navigate_jump():
    wiz = OnboardingWizard()
    res = wiz.navigate("jump", "Equipment")
    assert res == "Equipment"
    # history should have one entry
    assert wiz.history[-1] == "Personal Info"

def test_enable_accessibility_mode():
    wiz = OnboardingWizard()
    wiz.enable_accessibility_mode()
    assert wiz.accessibility
    assert wiz.high_contrast

def test_init_curses_renderer():
    wiz = OnboardingWizard()
    dummy = object()
    wiz.init_curses_renderer(dummy)
    assert wiz.renderer_initialized
    assert wiz.stdscr is dummy

def test_audit_log_event():
    wiz = OnboardingWizard()
    wiz.audit_log_event("my_event", {"a": 1})
    assert wiz.audit_log[-1]["event"] == "my_event"
    assert wiz.audit_log[-1]["data"] == {"a": 1}

def test_start_wizard():
    wiz = OnboardingWizard()
    wiz.current_page = "Equipment"
    wiz.history = ["Personal Info", "Benefits"]
    wiz.start_wizard()
    assert wiz.current_page == "Personal Info"
    assert wiz.history == []
    assert any(e["event"] == "start_wizard" for e in wiz.audit_log)

def test_save_and_load_session(tmp_path):
    wiz = OnboardingWizard()
    wiz.context = {"foo": "bar"}
    wiz.history = ["Personal Info"]
    wiz.current_page = "Equipment"
    file = tmp_path / "sess.json"
    wiz.save_session(str(file))
    # load into new wizard
    wiz2 = OnboardingWizard()
    wiz2.load_session(str(file))
    assert wiz2.context == {"foo": "bar"}
    assert wiz2.history == ["Personal Info"]
    assert wiz2.current_page == "Equipment"
    # audit logs for save and load
    assert any(e["event"] == "save_session" for e in wiz.audit_log)
    assert any(e["event"] == "load_session" for e in wiz2.audit_log)

def test_register_plugin_and_invoke():
    wiz = OnboardingWizard()
    def plugin(x):
        return x * 2
    wiz.register_plugin("dbl", plugin)
    assert "dbl" in wiz.plugins
    assert wiz.plugins["dbl"](3) == 6

def test_branch_flow():
    wiz = OnboardingWizard()
    wiz.context["Relocate"] = "no"
    assert not wiz.branch_flow()
    wiz.context["Relocate"] = "yes"
    assert wiz.branch_flow()

def test_apply_skip_logic_audit_logged():
    wiz = OnboardingWizard()
    wiz.context["employment_type"] = "contractor"
    wiz.apply_skip_logic()
    assert any(e["event"] == "apply_skip_logic" for e in wiz.audit_log)

def test_navigate_audit_logged():
    wiz = OnboardingWizard()
    wiz.navigate("next")
    assert any(e["event"] == "navigate" for e in wiz.audit_log)
