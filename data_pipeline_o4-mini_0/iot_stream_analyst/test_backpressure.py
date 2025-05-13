from streamkit.backpressure import BackpressureControl

def test_backpressure_allows_until_capacity():
    bp = BackpressureControl(capacity=2)
    assert bp.on_message() is True
    assert bp.on_message() is True
    assert bp.on_message() is False
    bp.on_processed()
    assert bp.on_message() is True
