class RetryHistoryCollector:
    def __init__(self):
        self.attempts = []

    def record(self, attempt_info):
        """
        Record a single attempt. attempt_info can be any data structure.
        """
        self.attempts.append(attempt_info)

    def get_history(self):
        """
        Return the list of recorded attempts.
        """
        return list(self.attempts)
