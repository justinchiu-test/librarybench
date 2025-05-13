import pytest
from pipeline.versioning import Versioning

def test_versioning_record_and_retrieve():
    v = Versioning()
    data1 = [1,2,3]
    data2 = {"a": 10}
    v.record_version("stage1", "v1", data1)
    v.record_version("stage1", "v2", data2)
    assert v.get_versions("stage1") == ["v1", "v2"]
    assert v.get_data("stage1", "v1") == data1
    assert v.get_data("stage1", "v2") == data2

def test_versioning_missing():
    v = Versioning()
    with pytest.raises(KeyError):
        v.get_data("stageX", "nope")
