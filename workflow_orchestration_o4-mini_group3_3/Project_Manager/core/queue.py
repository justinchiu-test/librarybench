import time
import threading
from collections import deque
from core.logger import logger
from utils import start_daemon_thread

class TaskQueue:
    def __init__(self):
        self._queue = deque()
        self._lock = threading.Lock()
        self._stop = False

    def enqueue(self, workflow):
        with self._lock:
            self._queue.append(workflow)
            logger.info(f"Enqueued workflow {workflow.name} v{workflow.version}.")

    def process(self):
        logger.info("TaskQueue processing started.")
        while not self._stop:
            wf = None
            with self._lock:
                if self._queue:
                    wf = self._queue.popleft()
            if wf:
                logger.info(f"Processing workflow {wf.name}.")
                wf.run()
            else:
                time.sleep(0.1)

    def start(self):
        start_daemon_thread(self.process)

    def stop(self):
        self._stop = True
