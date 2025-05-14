import os
import uuid
import json

class DeadLetterQueue:
    def __init__(self, queue_dir):
        self.queue_dir = queue_dir
        os.makedirs(queue_dir, exist_ok=True)

    def push(self, message):
        file_path = os.path.join(self.queue_dir, f"{uuid.uuid4()}.json")
        with open(file_path, 'w') as f:
            json.dump(message, f)

    def pop_all(self):
        messages = []
        for fname in os.listdir(self.queue_dir):
            path = os.path.join(self.queue_dir, fname)
            try:
                with open(path, 'r') as f:
                    messages.append(json.load(f))
            except Exception:
                continue
            os.remove(path)
        return messages
