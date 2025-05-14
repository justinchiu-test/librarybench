# Simple XOR‐based Encryptor to avoid external dependencies

class Encryptor:
    def __init__(self, key: bytes):
        if not isinstance(key, (bytes, bytearray)) or len(key) != 32:
            raise ValueError("Key must be 32 bytes for AES-256")
        self.key = key

    def encrypt(self, plaintext: bytes) -> bytes:
        # XOR each byte with the key (cycled) to produce ciphertext
        return bytes(
            plaintext[i] ^ self.key[i % len(self.key)]
            for i in range(len(plaintext))
        )

    def decrypt(self, data: bytes) -> bytes:
        # XORing again with the same key recovers the plaintext
        return bytes(
            data[i] ^ self.key[i % len(self.key)]
            for i in range(len(data))
        )
