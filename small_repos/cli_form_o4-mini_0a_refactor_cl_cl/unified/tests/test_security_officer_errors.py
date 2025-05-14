import pytest
from security_officer.incident_form.errors import format_error

def test_format_error_non_critical():
    msg = format_error("Missing field")
    assert msg == "ERROR: Missing field"

def test_format_error_critical():
    msg = format_error("Critical failure", critical=True)
    assert msg.startswith("*** ERROR")
    assert msg.endswith("***")
