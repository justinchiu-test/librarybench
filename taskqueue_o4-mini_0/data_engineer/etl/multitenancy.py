from collections import defaultdict

class Tenant:
    def __init__(self, name):
        self.name = name
        self.queue = []
        self.storage = {}
        self.metrics = {}
        self.quotas = {}

class MultiTenancySupport:
    def __init__(self):
        self.tenants = {}

    def create_tenant(self, name):
        if name in self.tenants:
            return self.tenants[name]
        tenant = Tenant(name)
        self.tenants[name] = tenant
        return tenant

    def get_tenant(self, name):
        return self.tenants.get(name, None)

    def list_tenants(self):
        return list(self.tenants.keys())
