class CompliancePlugin:
    def before_validate(self, request):
        pass

    def after_validate(self, result):
        pass

class PluginManager:
    def __init__(self, plugins=None):
        self.plugins = plugins or []

    def before(self, request):
        for plugin in self.plugins:
            plugin.before_validate(request)

    def after(self, result):
        for plugin in self.plugins:
            plugin.after_validate(result)
