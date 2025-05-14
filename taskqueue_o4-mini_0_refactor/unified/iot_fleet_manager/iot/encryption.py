import base64

def encrypt(data: bytes, key: bytes) -> bytes:
    encrypted = bytearray()
    key_len = len(key)
    for i, b in enumerate(data):
        encrypted.append(b ^ key[i % key_len])
    return base64.b64encode(bytes(encrypted))

def decrypt(token: bytes, key: bytes) -> bytes:
    data = base64.b64decode(token)
    decrypted = bytearray()
    key_len = len(key)
    for i, b in enumerate(data):
        decrypted.append(b ^ key[i % key_len])
    return bytes(decrypted)
