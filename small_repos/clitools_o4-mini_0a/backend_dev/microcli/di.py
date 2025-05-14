class Container:
    def __init__(self, providers: dict):
        self._providers = providers
        self._instances = {}

    def resolve(self, name: str):
        if name in self._instances:
            return self._instances[name]
        if name not in self._providers:
            raise KeyError(f"Provider '{name}' not found")
        instance = self._providers[name]()
        self._instances[name] = instance
        return instance

def init_di(dependencies: dict) -> Container:
    return Container(dependencies)
