import pytest
from pipeline.task import UniqueTaskID

def test_unique_task_id_generation():
    t = UniqueTaskID()
    id1 = t.generate()
    id2 = t.generate()
    assert id1 != id2

def test_register_duplicate():
    t = UniqueTaskID()
    t.register('xyz')
    with pytest.raises(ValueError):
        t.register('xyz')
