from collections import defaultdict

class BuiltInGroup:
    def __init__(self, keys):
        if isinstance(keys, (str,)):
            keys = [keys]
        self.keys = list(keys)

    def group(self, records):
        groups = defaultdict(list)
        for rec in records:
            key = tuple(rec.get(k) for k in self.keys)
            if len(self.keys) == 1:
                key = key[0]
            groups[key].append(rec)
        return dict(groups)

    def aggregate(self, records, func):
        gr = self.group(records)
        return {k: func(v) for k, v in gr.items()}
