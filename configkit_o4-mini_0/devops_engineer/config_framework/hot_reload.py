class HotReload:
    def __init__(self, loader):
        self.loader = loader
        self.callbacks = []

    def watch(self, callback):
        self.callbacks.append(callback)

    def reload(self):
        config = self.loader.load()
        for cb in self.callbacks:
            cb(config)
        return config
