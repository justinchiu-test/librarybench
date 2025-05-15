import re
import pytest
from security_officer.incident_form.fields import TextField

def test_textfield_basic():
    tf = TextField(pattern=r"^CVE-\d{4}-\d+$", max_length=20)
    ok, err = tf.input("CVE-2021-1234")
    assert ok
    assert tf.get_value() == "CVE-2021-1234"

def test_textfield_pattern_fail():
    tf = TextField(pattern=r"^CVE-\d{4}-\d+$", max_length=10)
    ok, err = tf.input("INVALID")
    assert not ok

def test_textfield_length_fail():
    tf = TextField(pattern=None, max_length=5)
    ok, err = tf.input("123456")
    assert not ok

def test_textfield_masking():
    tf = TextField(pattern=None, max_length=10, mask_sensitive=True)
    ok, err = tf.input("secret")
    assert ok
    assert tf.get_value() == "******"
