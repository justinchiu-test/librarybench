class SourceHook:
    def __init__(self, func):
        self.func = func
    def import_data(self, context):
        return self.func(context)

class SinkHook:
    def __init__(self, func):
        self.func = func
    def export_data(self, data, context):
        return self.func(data, context)
