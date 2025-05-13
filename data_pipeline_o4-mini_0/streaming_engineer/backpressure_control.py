class BackpressureControl:
    def __init__(self, max_queue_size):
        self.max_queue_size = max_queue_size
        self.monitors = []

    def register(self, get_queue_size_func, throttle_callback):
        self.monitors.append((get_queue_size_func, throttle_callback))

    def check(self):
        for get_size, callback in self.monitors:
            size = get_size()
            if size > self.max_queue_size:
                callback(True)
            else:
                callback(False)
