class TransformationPipeline:
    def __init__(self):
        self.transforms = []

    def add(self, func):
        self.transforms.append(func)

    def process(self, value):
        for func in self.transforms:
            value = func(value)
        return value
