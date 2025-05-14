import json

class BackupAndRestore:
    def backup(self, state: dict, filename: str):
        with open(filename, 'w') as f:
            json.dump(state, f)

    def restore(self, filename: str) -> dict:
        with open(filename, 'r') as f:
            return json.load(f)
