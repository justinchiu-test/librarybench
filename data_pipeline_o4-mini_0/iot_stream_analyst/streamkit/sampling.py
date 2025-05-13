import random

class SamplingStage:
    def __init__(self, fraction):
        self.fraction = fraction

    def sample(self, items):
        return [i for i in items if random.random() < self.fraction]
