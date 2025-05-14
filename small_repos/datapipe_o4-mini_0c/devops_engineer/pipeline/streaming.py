import threading
import time

class StreamingRunner:
    def __init__(self, process_func):
        self.process = process_func
        self.running = False
        self.thread = None

    def _run(self):
        while self.running:
            self.process()
            time.sleep(0.1)

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run)
            self.thread.start()

    def stop(self):
        if self.running:
            self.running = False
            self.thread.join()
