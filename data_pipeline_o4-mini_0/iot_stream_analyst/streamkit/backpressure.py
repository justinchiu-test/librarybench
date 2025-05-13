class BackpressureControl:
    def __init__(self, capacity):
        self.capacity = capacity
        self.queue_len = 0

    def on_message(self):
        if self.queue_len < self.capacity:
            self.queue_len += 1
            return True
        return False

    def on_processed(self):
        if self.queue_len > 0:
            self.queue_len -= 1
