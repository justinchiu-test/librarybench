import os
import json

class Journal:
    def __init__(self, journal_path):
        self.journal_path = journal_path
        open(self.journal_path, 'a').close()

    def append(self, op):
        with open(self.journal_path, 'a') as f:
            f.write(json.dumps(op) + '\n')

    def replay(self):
        ops = []
        with open(self.journal_path) as f:
            for line in f:
                ops.append(json.loads(line))
        return ops

    def clear(self):
        open(self.journal_path, 'w').close()
