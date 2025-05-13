class RateLimitLogger:
    def __init__(self):
        self.logs = []

    def log_denied(self, request):
        entry = {'request': request, 'status': 'denied'}
        self.logs.append(entry)
