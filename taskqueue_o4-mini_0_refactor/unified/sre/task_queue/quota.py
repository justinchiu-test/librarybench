class QuotaExceeded(Exception):
    pass

class QuotaManager:
    def __init__(self):
        # service_name -> max concurrent tasks
        self.quotas = {}
        # service_name -> current usage
        self.usage = {}

    def set_quota(self, service, limit):
        self.quotas[service] = limit
        self.usage.setdefault(service, 0)

    def can_use(self, service):
        limit = self.quotas.get(service)
        if limit is None:
            return True
        return self.usage.get(service, 0) < limit

    def use(self, service):
        if not self.can_use(service):
            raise QuotaExceeded(f"Quota exceeded for service {service}")
        self.usage[service] = self.usage.get(service, 0) + 1

    def release(self, service):
        if self.usage.get(service, 0) > 0:
            self.usage[service] -= 1

    def get_usage(self, service):
        return self.usage.get(service, 0)

    def get_quota(self, service):
        return self.quotas.get(service, None)
