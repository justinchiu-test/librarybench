import pytest
import json
from fintech_compliance_officer.encryption import encrypt, decrypt

def test_encrypt_decrypt():
    key = 'secret'
    data = json.dumps({'foo': 'bar'})
    encrypted = encrypt(data, key)
    assert encrypted != data
    decrypted = decrypt(encrypted, key)
    assert decrypted == data
