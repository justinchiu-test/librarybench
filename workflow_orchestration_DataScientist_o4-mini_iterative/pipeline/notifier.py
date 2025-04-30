class DummyNotifier:
    """
    A simple in-memory notifier for testing: captures successes, retries, and failures.
    """
    def __init__(self):
        self.successes = []
        self.retries = []
        self.failures = []

    def notify_success(self, task_name):
        self.successes.append(task_name)

    def notify_retry(self, task_name, exception, attempt):
        self.retries.append((task_name, exception, attempt))

    def notify_error(self, task_name, exception):
        self.failures.append((task_name, exception))
