import pytest
from iot.encryption import encrypt, decrypt

def test_encrypt_decrypt():
    data = b"test data for encryption"
    key = b"secret"
    token = encrypt(data, key)
    assert isinstance(token, bytes)
    recovered = decrypt(token, key)
    assert recovered == data

def test_wrong_key():
    data = b"another test"
    key = b"key1"
    wrong = b"key2"
    token = encrypt(data, key)
    with pytest.raises(AssertionError):
        assert decrypt(token, wrong) == data
