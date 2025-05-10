from cli_framework.defaults import compute_default

def test_uuid():
    u1 = compute_default("uuid")
    u2 = compute_default("uuid")
    assert u1 != u2
    assert len(u1) == 36

def test_salt():
    s = compute_default("salt", length=8)
    assert len(s) == 16
