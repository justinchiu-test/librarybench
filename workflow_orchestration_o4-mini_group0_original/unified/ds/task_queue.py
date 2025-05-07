from queue import Queue

class TaskQueue:
    """
    Simple FIFO task queue.
    """
    def __init__(self):
        self.queue = Queue()

    def add_task(self, task):
        self.queue.put(task)

    def get_task(self):
        return self.queue.get()

    def task_done(self):
        self.queue.task_done()