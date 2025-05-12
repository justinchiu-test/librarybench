class DefaultFallback:
    defaults = {
        'learning_rate': 0.001,
        'epochs': 10,
        'batch_size': 32
    }

    @staticmethod
    def apply(config):
        for key, value in DefaultFallback.defaults.items():
            config.setdefault(key, value)
        return config
