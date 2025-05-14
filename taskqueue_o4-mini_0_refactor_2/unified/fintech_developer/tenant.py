import threading

class AccessDenied(Exception):
    pass

class TenantContext:
    _thread_local = threading.local()

    def __init__(self, tenant_id):
        self.tenant_id = tenant_id

    def __enter__(self):
        TenantContext._thread_local.current = self.tenant_id

    def __exit__(self, exc_type, exc_value, traceback):
        TenantContext._thread_local.current = None

    @staticmethod
    def current_tenant():
        return getattr(TenantContext._thread_local, 'current', None)

class MultiTenancySupport:
    def __init__(self):
        # Maps resource_id to owning tenant
        self._resources = {}

    def register_resource(self, resource_id, tenant_id):
        self._resources[resource_id] = tenant_id

    def check_access(self, resource_id):
        current = TenantContext.current_tenant()
        owner = self._resources.get(resource_id)
        if owner != current:
            raise AccessDenied(f"Tenant {current} cannot access resource {resource_id}")
        return True
