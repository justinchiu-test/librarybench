import base64
from config_framework.decryption import decrypt_secret

def test_decrypt_aes():
    assert decrypt_secret("AES:hello") == "olleh"

def test_decrypt_base64():
    orig = "secret"
    b = base64.b64encode(orig.encode()).decode()
    assert decrypt_secret(b) == orig

def test_decrypt_plain():
    s = "plain"
    assert decrypt_secret(s) == s
