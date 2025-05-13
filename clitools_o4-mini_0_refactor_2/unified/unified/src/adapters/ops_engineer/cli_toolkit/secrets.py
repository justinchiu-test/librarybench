"""
Secrets management for Operations Engineer CLI.
"""
class SecretManager:
    def __init__(self):
        self.store = {}

    def set_secret(self, key, value):
        self.store[key] = value

    def get_secret(self, key):
        return self.store.get(key)