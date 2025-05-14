class DeadLetterQueue:
    def __init__(self):
        self._queue = []

    def enqueue(self, task_id: str, reason: str):
        self._queue.append({'task_id': task_id, 'reason': reason})

    def retrieve_all(self):
        items = list(self._queue)
        self._queue.clear()
        return items
