class Plugin:
    def process(self, task, result):
        return result

class SerializerPlugin(Plugin):
    def __init__(self, serializer):
        self.serializer = serializer

    def process(self, task, result):
        return self.serializer(result)
