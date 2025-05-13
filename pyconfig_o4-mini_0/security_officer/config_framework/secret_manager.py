class SecretManager:
    def __init__(self):
        self._cache = {}
        self._vault = {}
        self._version = {}

    def get_secret(self, name):
        if name in self._cache:
            return self._cache[name]
        value = self._vault.get(name, f"secret_{name}")
        self._cache[name] = value
        self._version[name] = self._version.get(name, 1)
        return value

    def rotate_secret(self, name):
        new_version = self._version.get(name, 1) + 1
        self._version[name] = new_version
        new_value = f"secret_{name}_v{new_version}"
        self._vault[name] = new_value
        self._cache[name] = new_value
        return new_value
