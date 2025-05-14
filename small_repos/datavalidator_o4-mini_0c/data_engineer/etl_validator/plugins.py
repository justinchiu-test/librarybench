class Plugin:
    def transform(self, record):
        return record

    def enrich(self, record):
        return record

class PluginManager:
    def __init__(self):
        self.plugins = []

    def register(self, plugin):
        self.plugins.append(plugin)

    def apply(self, record):
        for plugin in self.plugins:
            if hasattr(plugin, 'transform'):
                record = plugin.transform(record)
        for plugin in self.plugins:
            if hasattr(plugin, 'enrich'):
                record = plugin.enrich(record)
        return record
