from collections import defaultdict

class BuiltInGroup:
    def group(self, items, key_fn):
        grouped = defaultdict(list)
        for item in items:
            grouped[key_fn(item)].append(item)
        return dict(grouped)
