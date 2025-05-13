import threading
import time

class MonitoringDashboard:
    def __init__(self):
        self._running = False
        self._status = {}
        self._thread = None

    def start_server(self):
        if self._running:
            return False
        self._running = True
        self._thread = threading.Thread(target=self._run)
        self._thread.daemon = True
        self._thread.start()
        return True

    def _run(self):
        while self._running:
            # dummy status update
            self._status['timestamp'] = time.time()
            time.sleep(0.1)

    def stop_server(self):
        if not self._running:
            return False
        self._running = False
        self._thread.join(timeout=1)
        return True

    def get_status(self):
        return dict(self._status)
