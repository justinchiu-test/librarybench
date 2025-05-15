import json
import yaml
import pytest
from datetime import datetime
from survey import (
    validate_input, format_error, TextField, DateTimePicker,
    CursesRenderer, WizardLayout, enable_accessibility_mode,
    ACCESSIBILITY_MODE, AuditLog, register_field_plugin,
    FIELD_PLUGINS, export_data
)

def test_validate_input_required():
    valid, err = validate_input("", required=True)
    assert not valid
    assert "required" in err.lower()

def test_validate_input_range():
    valid, err = validate_input(5, min_value=1, max_value=4)
    assert not valid
    assert "between" in err

    valid2, err2 = validate_input(3, min_value=1, max_value=4)
    assert valid2 and err2 == ""

def test_format_error():
    msg = format_error("Oops")
    assert msg.startswith("[ERROR]")
    assert "Oops" in msg

def test_text_field_validation():
    tf = TextField(length_limit=5, placeholder="enter")
    ok, err = tf.validate("toolong")
    assert not ok
    assert "limit" in err
    assert tf.placeholder == "enter"

def test_date_time_picker():
    dtp = DateTimePicker()
    val = dtp.pick()
    assert isinstance(val, datetime)

def test_curses_renderer():
    cr = CursesRenderer()
    out = cr.render("page1")
    assert "page1" in out
    assert out.startswith("Rendering")

def test_wizard_layout_navigation():
    pages = ["a", "b", "c"]
    wz = WizardLayout(pages)
    assert wz.current_page() == "a"
    assert wz.next() == "b"
    assert not wz.is_finished()
    assert wz.next() == "c"
    assert wz.is_finished()
    assert wz.prev() == "b"

def test_enable_accessibility_mode():
    # reset if needed
    global ACCESSIBILITY_MODE
    ACCESSIBILITY_MODE = False
    enable_accessibility_mode()
    assert ACCESSIBILITY_MODE is True

def test_audit_log_records():
    al = AuditLog()
    al.record("user1", "did something")
    logs = al.get_logs()
    assert len(logs) == 1
    entry = logs[0]
    assert entry["user"] == "user1"
    assert "timestamp" in entry
    assert isinstance(entry["timestamp"], datetime)

def test_register_field_plugin():
    class DummyPlugin:
        pass
    register_field_plugin("dummy", DummyPlugin)
    assert "dummy" in FIELD_PLUGINS
    assert FIELD_PLUGINS["dummy"] is DummyPlugin

def test_export_data_json():
    data = {"a": 1, "b": "text"}
    out = export_data(data, format="json")
    loaded = json.loads(out)
    assert loaded == data

def test_export_data_yaml():
    data = {"x": [1, 2, 3], "y": {"nested": True}}
    out = export_data(data, format="yaml")
    loaded = yaml.safe_load(out)
    assert loaded == data

def test_export_data_invalid_format():
    with pytest.raises(ValueError):
        export_data({}, format="xml")
