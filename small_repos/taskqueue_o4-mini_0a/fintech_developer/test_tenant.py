import pytest
from tenant import TenantContext, MultiTenancySupport, AccessDenied

def test_tenant_access_allowed():
    tenancy = MultiTenancySupport()
    tenancy.register_resource("r1", "t1")
    with TenantContext("t1"):
        assert tenancy.check_access("r1")

def test_tenant_access_denied():
    tenancy = MultiTenancySupport()
    tenancy.register_resource("r1", "t1")
    with TenantContext("t2"):
        with pytest.raises(AccessDenied):
            tenancy.check_access("r1")
