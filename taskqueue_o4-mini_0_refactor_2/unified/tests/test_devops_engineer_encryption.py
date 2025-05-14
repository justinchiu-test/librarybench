import pytest
from devops_engineer.taskqueue.queue import _xor_encrypt, _xor_decrypt

def test_xor_encrypt_decrypt():
    key = b'key'
    data = b'Hello, World!'
    enc = _xor_encrypt(data, key)
    assert enc != data
    dec = _xor_decrypt(enc, key)
    assert dec == data
