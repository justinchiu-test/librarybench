class QuotaExceededError(Exception):
    pass

class QuotaManagement:
    def __init__(self, cpu_quota, memory_quota):
        self.cpu_quota = cpu_quota
        self.memory_quota = memory_quota
        self.cpu_used = 0
        self.memory_used = 0

    def consume(self, cpu, memory):
        if self.cpu_used + cpu > self.cpu_quota or self.memory_used + memory > self.memory_quota:
            raise QuotaExceededError("Quota exceeded")
        self.cpu_used += cpu
        self.memory_used += memory

    def reset(self):
        self.cpu_used = 0
        self.memory_used = 0
