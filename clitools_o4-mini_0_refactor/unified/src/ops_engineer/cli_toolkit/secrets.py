"""
Secrets manager for ops engineers.
"""
class SecretManager:
    def __init__(self):
        self._store = {}

    def set_secret(self, key, value):
        self._store[key] = value

    def get_secret(self, key):
        return self._store.get(key)