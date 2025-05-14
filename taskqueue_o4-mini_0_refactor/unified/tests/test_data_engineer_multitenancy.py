from data_engineer.etl.multitenancy import MultiTenancySupport

def test_tenant_creation_and_lookup():
    m = MultiTenancySupport()
    t1 = m.create_tenant("teamA")
    t2 = m.get_tenant("teamA")
    assert t1 is t2
    assert m.list_tenants() == ["teamA"]
    t3 = m.create_tenant("teamB")
    assert set(m.list_tenants()) == {"teamA", "teamB"}
