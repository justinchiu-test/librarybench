import threading
import time

class Scheduler:
    """
    In-memory scheduler for workflows.
    Runs registered workflows at fixed intervals.
    """
    def __init__(self):
        # Each schedule: {'workflow_id': str, 'interval_seconds': int, 'last_run': float}
        self.schedules = []
        self.lock = threading.Lock()
        self.running = False
        self.thread = None

    def add_schedule(self, workflow_id, interval_seconds):
        with self.lock:
            self.schedules.append({
                'workflow_id': workflow_id,
                'interval_seconds': interval_seconds,
                'last_run': None
            })

    def start(self, run_callback):
        """
        Start the scheduler thread.
        run_callback: function(workflow_id) to invoke.
        """
        if not self.running:
            self.running = True
            self.thread = threading.Thread(
                target=self._run_loop, args=(run_callback,), daemon=True
            )
            self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def _run_loop(self, run_callback):
        while self.running:
            now = time.time()
            with self.lock:
                for entry in self.schedules:
                    last = entry['last_run']
                    interval = entry['interval_seconds']
                    if last is None or (now - last) >= interval:
                        entry['last_run'] = now
                        threading.Thread(target=run_callback,
                                         args=(entry['workflow_id'],),
                                         daemon=True).start()
            time.sleep(1)
