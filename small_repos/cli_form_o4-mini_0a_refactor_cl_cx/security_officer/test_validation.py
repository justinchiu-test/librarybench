import pytest
from incident_form.validation import validate_input

def test_incident_id_valid():
    ok, err = validate_input("incident_id", "INC-1234")
    assert ok and err is None

def test_incident_id_invalid():
    ok, err = validate_input("incident_id", "INC12")
    assert not ok and "format" in err

def test_ip_valid():
    ok, err = validate_input("ip", "192.168.0.1")
    assert ok

def test_ip_invalid():
    ok, err = validate_input("ip", "999.999.999.999")
    assert not ok

def test_general_valid():
    ok, err = validate_input("general", "Normal input, with punctuation.")
    assert ok

def test_general_invalid():
    ok, err = validate_input("general", "Bad chars <>")
    assert not ok
