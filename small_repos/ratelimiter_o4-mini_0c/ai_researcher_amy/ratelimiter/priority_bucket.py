from ratelimiter.token_bucket import TokenBucket

class PriorityBucket(TokenBucket):
    def __init__(self, refill_rate, bucket_capacity, priority_override=True, clock=None):
        super().__init__(refill_rate, bucket_capacity, clock=clock)
        self.priority_override = priority_override

    def allow(self, priority=False, tokens=1):
        if priority and self.priority_override:
            return True
        return super().allow(tokens)
