class BuiltInSort:
    def __init__(self, key, reverse=False):
        self.key = key
        self.reverse = reverse

    def sort(self, records):
        return sorted(records, key=lambda rec: rec.get(self.key), reverse=self.reverse)
