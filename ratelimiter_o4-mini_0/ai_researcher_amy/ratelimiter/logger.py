class RateLimitLogger:
    events = []

    @classmethod
    def log_throttle(cls, func_name, client):
        cls.events.append({'func': func_name, 'client': client, 'action': 'throttle'})

    @classmethod
    def log_allow(cls, func_name, client):
        cls.events.append({'func': func_name, 'client': client, 'action': 'allow'})

    @classmethod
    def clear(cls):
        cls.events.clear()
