from telemetry.cli import cli_manager, registered_devices

def test_register():
    registered_devices.clear()
    res = cli_manager(['register', 'devX'])
    assert res is True
    assert 'devX' in registered_devices

def test_backfill():
    out = cli_manager(['backfill', '2021-01-01', '2021-01-02'])
    assert out['status'] == 'backfill_complete'
    assert out['start'] == '2021-01-01'

def test_trace():
    stream = ['a', 'b', 'c', 'd', 'e', 'f']
    res = cli_manager(['trace'] + stream)
    assert res == stream[:5]
