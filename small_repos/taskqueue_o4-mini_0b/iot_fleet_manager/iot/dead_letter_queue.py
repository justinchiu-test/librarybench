from collections import deque

class DeadLetterQueue:
    def __init__(self):
        self._queue = deque()

    def enqueue(self, task):
        self._queue.append(task)

    def get_all(self):
        return list(self._queue)

    def clear(self):
        self._queue.clear()
