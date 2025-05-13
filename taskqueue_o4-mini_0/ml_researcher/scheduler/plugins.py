class PluginRegistry:
    def __init__(self):
        self.serializers = {}
        self.reporters = {}
        self.validators = {}
    def register_serializer(self, name, fn):
        self.serializers[name] = fn
    def register_reporter(self, name, fn):
        self.reporters[name] = fn
    def register_validator(self, name, fn):
        self.validators[name] = fn
    def get_serializer(self, name):
        return self.serializers.get(name)
    def get_reporter(self, name):
        return self.reporters.get(name)
    def get_validator(self, name):
        return self.validators.get(name)
