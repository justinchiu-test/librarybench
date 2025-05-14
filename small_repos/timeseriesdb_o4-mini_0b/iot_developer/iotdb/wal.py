import os
import json

class WriteAheadLog:
    def __init__(self, path):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(self.path, 'a').close()

    def append(self, record):
        with open(self.path, 'a') as f:
            f.write(json.dumps(record) + '\n')

    def replay(self):
        records = []
        with open(self.path) as f:
            for line in f:
                records.append(json.loads(line.strip()))
        return records
