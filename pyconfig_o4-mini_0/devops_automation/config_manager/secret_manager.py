class SecretManager:
    def __init__(self, client=None):
        self.client = client
        self.secrets = {}

    def set_secret(self, path, secret):
        self.secrets[path] = secret

    def get_secret(self, path):
        if self.client:
            return self.client.read(path)
        return self.secrets.get(path)

    def rotate_secret(self, path):
        if self.client:
            return self.client.rotate(path)
        val = self.secrets.get(path)
        if isinstance(val, str):
            new = val + "_rotated"
            self.secrets[path] = new
            return new
        return val
