import time
from iotdb.retention import apply_retention

def test_retention_raw_and_aggregate():
    now = 1000000
    device = 'dev1'
    fifteen = now - 15*24*3600
    one = now - 1*24*3600
    hundred = now - 100*24*3600
    eighty_nine = now - 89*24*3600
    data = {
        device: [
            (hundred, 10),
            (fifteen, 20),
            (eighty_nine, 30),
            (one, 40)
        ]
    }
    new = apply_retention(data, now)
    readings = new[device]
    assert any(val == 40 for _, val in readings)
    assert any(val == 20 for _, val in readings)
    assert any(val == 30 for _, val in readings)
