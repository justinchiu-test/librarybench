import os
from journaling.crypto import AESCipher
import pytest

def test_encrypt_decrypt():
    key = os.urandom(32)
    cipher = AESCipher(key)
    data = b'hello world'
    encrypted = cipher.encrypt(data)
    assert encrypted != data
    decrypted = cipher.decrypt(encrypted)
    assert decrypted == data

def test_key_length():
    with pytest.raises(ValueError):
        AESCipher(b'tooshort')
