import time
import heapq

class Scheduler:
    def __init__(self):
        # heap of (eta, task_id)
        self.heap = []

    def schedule(self, task_id, eta):
        heapq.heappush(self.heap, (eta, task_id))

    def get_ready(self, now=None):
        now = now or time.time()
        ready = []
        while self.heap and self.heap[0][0] <= now:
            eta, task_id = heapq.heappop(self.heap)
            ready.append(task_id)
        return ready

    def peek_next_eta(self):
        if not self.heap:
            return None
        return self.heap[0][0]
