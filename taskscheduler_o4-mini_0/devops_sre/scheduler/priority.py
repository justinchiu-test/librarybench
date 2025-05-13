import heapq

class JobPriorityQueue:
    def __init__(self):
        self._queue = []
        self._counter = 0

    def push(self, job, priority):
        # lower priority number means higher priority
        heapq.heappush(self._queue, (priority, self._counter, job))
        self._counter += 1

    def pop(self):
        if not self._queue:
            raise IndexError("pop from empty queue")
        return heapq.heappop(self._queue)[2]

    def __len__(self):
        return len(self._queue)
