import os

class EnvVarOverrides:
    def __init__(self):
        self.max_attempts = int(os.getenv('RETRY_MAX_ATTEMPTS', '3'))
        self.base_delay = float(os.getenv('RETRY_BASE_DELAY', '1.0'))
        self.max_delay = float(os.getenv('RETRY_MAX_DELAY', '10.0'))
        self.backoff_strategy = os.getenv('RETRY_BACKOFF_STRATEGY', 'exponential')
        self.failure_threshold = int(os.getenv('CB_FAILURE_THRESHOLD', '3'))
        self.recovery_timeout = int(os.getenv('CB_RECOVERY_TIMEOUT', '60'))
