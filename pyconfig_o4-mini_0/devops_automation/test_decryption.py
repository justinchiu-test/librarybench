import pytest
from config_manager.decryption import decrypt_base64

def test_decrypt_base64():
    encoded = "aGVsbG8="
    res = decrypt_base64(encoded)
    assert res == b"hello"
