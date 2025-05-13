from streamkit.versioning import Versioning

def test_versioning():
    v = Versioning()
    assert v.get() == 1
    v.bump()
    assert v.get() == 2
