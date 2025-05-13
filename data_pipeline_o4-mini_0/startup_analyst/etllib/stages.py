from .plugin_system import PluginSystem

class HookMixin:
    def __init__(self):
        self.pre_hooks = []
        self.post_hooks = []

    def add_pre_hook(self, hook):
        self.pre_hooks.append(hook)

    def add_post_hook(self, hook):
        self.post_hooks.append(hook)

    def _run_pre(self, record):
        for hook in self.pre_hooks:
            hook(record)

    def _run_post(self, record):
        for hook in self.post_hooks:
            hook(record)

class InMemorySource(HookMixin):
    def __init__(self, data):
        super().__init__()
        self.data = data

    def read(self):
        for record in self.data:
            self._run_pre(record)
            yield record
            self._run_post(record)

class InMemorySink(HookMixin):
    def __init__(self):
        super().__init__()
        self.storage = []

    def write(self, record):
        self._run_pre(record)
        self.storage.append(record)
        self._run_post(record)

class MapperStage:
    def __init__(self, func):
        self.func = func

    def process(self, record):
        return self.func(record)

# Register plugins
PluginSystem.register('source', 'memory', InMemorySource)
PluginSystem.register('sink', 'memory', InMemorySink)
PluginSystem.register('transform', 'mapper', MapperStage)
