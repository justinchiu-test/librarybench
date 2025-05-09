class TransformationPipeline:
    def __init__(self):
        self._transforms = []

    def add(self, func):
        if not callable(func):
            raise ValueError("Transform must be callable")
        self._transforms.append(func)

    def run(self, value):
        v = value
        for fn in self._transforms:
            v = fn(v)
        return v
