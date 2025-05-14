class EncryptionAtRest:
    def __init__(self, key: bytes):
        self.key = key

    def encrypt(self, data: bytes) -> bytes:
        return bytes([b ^ self.key[i % len(self.key)] for i, b in enumerate(data)])

    def decrypt(self, data: bytes) -> bytes:
        return self.encrypt(data)  # symmetric
