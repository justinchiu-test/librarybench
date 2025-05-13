import os
import json

class WriteAheadLog:
    def __init__(self, path):
        self.path = path
        # ensure file exists
        open(self.path, 'a').close()

    def append(self, record):
        with open(self.path, 'a') as f:
            f.write(json.dumps(record) + '\n')

    def replay(self):
        if not os.path.exists(self.path):
            return []
        records = []
        with open(self.path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return records
