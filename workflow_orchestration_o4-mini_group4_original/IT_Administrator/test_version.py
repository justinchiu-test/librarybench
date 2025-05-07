import pytest
from IT_Administrator.it_manager.version import VersionedEntity

class Dummy(VersionedEntity):
    def __init__(self):
        super().__init__()
        self.state = 0

    def update(self, val):
        self.state = val
        self.save_version(val)

def test_versioning_and_rollback():
    d = Dummy()
    assert d.versions == []
    d.update(1)
    d.update(2)
    d.update(3)
    assert [v for _, v in d.versions] == [1,2,3]
    assert d.current == 3
    snapshot = d.rollback(1)
    assert snapshot == 2
    assert d.current == 2
    assert len(d.versions) == 2
    with pytest.raises(IndexError):
        d.rollback(5)
