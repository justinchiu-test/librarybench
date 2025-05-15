class DependencyInjector:
    """
    Simple dependency injector storing providers by key.
    """
    def __init__(self):
        self._providers = {}

    def register(self, key, provider):
        """
        Register a provider (object or callable) under a key.
        """
        self._providers[key] = provider

    def resolve(self, key):
        """
        Resolve and return the provider registered under key.
        Raises KeyError if not found.
        """
        if key not in self._providers:
            raise KeyError(f"No provider registered for key: {key}")
        return self._providers[key]
