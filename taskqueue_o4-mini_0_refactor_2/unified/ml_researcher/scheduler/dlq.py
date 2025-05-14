class DeadLetterQueue:
    def __init__(self):
        self.queue = []
    def enqueue(self, run_id, reason):
        self.queue.append({'run_id': run_id, 'reason': reason})
    def get_all(self):
        return list(self.queue)
