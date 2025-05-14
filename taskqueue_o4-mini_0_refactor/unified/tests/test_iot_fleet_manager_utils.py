import pytest
from iot_fleet_manager.iot.utils import generate_unique_id

def test_generate_unique_id_length():
    uid = generate_unique_id()
    assert isinstance(uid, str)
    assert len(uid) == 32

def test_generate_unique_id_uniqueness():
    uids = {generate_unique_id() for _ in range(100)}
    assert len(uids) == 100
