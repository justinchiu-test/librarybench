class Versioning:
    def __init__(self):
        self.version = 1

    def bump(self):
        self.version += 1

    def get(self):
        return self.version
