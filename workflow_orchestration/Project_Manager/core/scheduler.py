import threading
import time
from core.logger import logger

class Scheduler:
    def __init__(self):
        self._jobs = []
        self._stop = False

    def schedule_workflow(self, workflow, interval_seconds):
        def job():
            while not self._stop:
                logger.info(f"Scheduler triggering workflow {workflow.name}.")
                workflow.run()
                time.sleep(interval_seconds)
        t = threading.Thread(target=job, daemon=True)
        t.start()
        self._jobs.append(t)

    def stop_all(self):
        self._stop = True
        for t in self._jobs:
            if t.is_alive():
                t.join(timeout=1)
