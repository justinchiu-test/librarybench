class ExecutionContext:
    def __init__(self):
        self._data = {}

    def set(self, key, value):
        self._data[key] = value

    def get(self, key):
        # Return None if key not present (tests don't expect KeyError)
        return self._data.get(key)
