import pytest
from pipeline.encryption import EncryptionAtRest

def test_encrypt_decrypt():
    key = b'secret'
    e = EncryptionAtRest(key)
    data = b'patientdata'
    token = e.encrypt(data)
    assert token != data
    assert e.decrypt(token) == data
