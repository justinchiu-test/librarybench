import pytest
import hashlib
from unified.src.security_specialist import SecureFieldMasking

def test_redact():
    assert SecureFieldMasking.redact('secret') == '****'

def test_hash():
    val = 'password'
    expected = hashlib.sha256(val.encode('utf-8')).hexdigest()
    assert SecureFieldMasking.hash(val) == expected
