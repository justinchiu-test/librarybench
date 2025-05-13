from encryption import EncryptionManager

def test_encryption_roundtrip():
    key = b"key"
    mgr = EncryptionManager(key)
    data = b"secret data"
    token = mgr.encrypt(data)
    assert token != data
    out = mgr.decrypt(token)
    assert out == data
