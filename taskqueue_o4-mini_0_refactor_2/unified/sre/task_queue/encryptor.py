import base64

class Encryptor:
    def __init__(self, key=b'secret'):
        self.key = key

    def encrypt(self, data: bytes) -> bytes:
        # simple xor with key then base64
        xored = bytes(b ^ self.key[i % len(self.key)] for i, b in enumerate(data))
        return base64.b64encode(xored)

    def decrypt(self, token: bytes) -> bytes:
        xored = base64.b64decode(token)
        data = bytes(b ^ self.key[i % len(self.key)] for i, b in enumerate(xored))
        return data
