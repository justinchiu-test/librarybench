def test_encryption_symmetric():
    from etl.encryption import EncryptionAtRest
    key = b"secret"
    e = EncryptionAtRest(key)
    data = b"hello world"
    encrypted = e.encrypt(data)
    assert encrypted != data
    decrypted = e.decrypt(encrypted)
    assert decrypted == data
