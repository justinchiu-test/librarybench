import time

class BackpressureController:
    def __init__(self, threshold=10000):
        self.threshold = threshold
    def control(self, queue_length):
        if queue_length > self.threshold:
            time.sleep(0.01)
