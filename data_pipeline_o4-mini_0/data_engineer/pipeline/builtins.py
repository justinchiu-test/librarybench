from .core import Stage

class BatchStage(Stage):
    def __init__(self, size):
        self.size = size

    def process(self, records):
        batches = []
        batch = []
        for r in records:
            batch.append(r)
            if len(batch) >= self.size:
                batches.append(batch)
                batch = []
        if batch:
            batches.append(batch)
        return batches

class SortStage(Stage):
    def __init__(self, key):
        self.key = key

    def process(self, records):
        return sorted(records, key=lambda r: r.get(self.key))

class GroupStage(Stage):
    def __init__(self, key):
        self.key = key

    def process(self, records):
        groups = {}
        for r in records:
            k = r.get(self.key)
            groups.setdefault(k, []).append(r)
        return list(groups.values())
