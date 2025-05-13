import json

class RealTimeLogger:
    def __init__(self):
        self.logs = []
    def log(self, event):
        entry = json.dumps(event)
        self.logs.append(entry)
    def get_logs(self):
        return list(self.logs)
