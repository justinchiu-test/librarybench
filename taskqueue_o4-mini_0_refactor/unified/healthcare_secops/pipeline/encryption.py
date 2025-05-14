import base64

class EncryptionAtRest:
    def __init__(self, key: bytes):
        self.key = key

    def encrypt(self, data: bytes) -> bytes:
        # Simple reversible encode: reverse bytes, append key, then base64
        return base64.b64encode(data[::-1] + self.key)

    def decrypt(self, token: bytes) -> bytes:
        decoded = base64.b64decode(token)
        data_rev = decoded[:-len(self.key)]
        return data_rev[::-1]
