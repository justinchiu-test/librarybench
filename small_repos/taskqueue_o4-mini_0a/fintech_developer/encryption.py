import base64

class EncryptionManager:
    def __init__(self, key: bytes):
        self.key = key

    def encrypt(self, data: bytes) -> bytes:
        # simple XOR cipher then base64
        encrypted = bytes(b ^ self.key[i % len(self.key)] for i, b in enumerate(data))
        return base64.b64encode(encrypted)

    def decrypt(self, token: bytes) -> bytes:
        encrypted = base64.b64decode(token)
        decrypted = bytes(b ^ self.key[i % len(self.key)] for i, b in enumerate(encrypted))
        return decrypted
