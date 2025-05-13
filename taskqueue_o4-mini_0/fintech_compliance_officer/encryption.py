import base64

def encrypt(data: str, key: str) -> str:
    data_bytes = data.encode('utf-8')
    key_bytes = key.encode('utf-8')
    encrypted = bytes([b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data_bytes)])
    return base64.b64encode(encrypted).decode('utf-8')

def decrypt(data: str, key: str) -> str:
    encrypted = base64.b64decode(data.encode('utf-8'))
    key_bytes = key.encode('utf-8')
    decrypted = bytes([b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(encrypted)])
    return decrypted.decode('utf-8')
