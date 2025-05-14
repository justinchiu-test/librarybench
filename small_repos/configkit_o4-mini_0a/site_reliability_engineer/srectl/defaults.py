import copy

class DefaultFallback:
    """
    Provides safe default thresholds and timeouts.
    """
    defaults = {
        'circuit_breaker': {
            'error_rate': 0.05,
            'timeout': 30
        },
        'alert': {
            'threshold': 0.9
        },
        'service': {
            'timeout': 10
        },
        'alerts': []
    }

    def load(self):
        return copy.deepcopy(self.defaults)
