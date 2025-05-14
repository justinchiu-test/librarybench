import json

class JSONImport:
    def __init__(self, tsdb):
        self.tsdb = tsdb

    def import_file(self, path):
        with open(path, 'r') as f:
            data = json.load(f)
        for record in data:
            self.tsdb.insert(record, replicate=False)
