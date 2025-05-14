import pytest
from windowed_operations import sliding_window_vwap, tumbling_candles

def test_sliding_window_vwap():
    data = [(10, 2), (20, 3), (30, 5)]
    # window size 2: windows [(10,2),(20,3)] and [(20,3),(30,5)]
    result = sliding_window_vwap(data, 2)
    assert pytest.approx(result) == [(10*2+20*3)/5, (20*3+30*5)/8]

def test_sliding_window_zero_volume():
    data = [(10, 0), (20, 0)]
    assert sliding_window_vwap(data, 2) == [0]

def test_tumbling_candles():
    prices = [1, 3, 2, 5, 4]
    candles = tumbling_candles(prices, 2)
    expected = [
        {'open':1,'high':3,'low':1,'close':3},
        {'open':2,'high':5,'low':2,'close':5},
        {'open':4,'high':4,'low':4,'close':4},
    ]
    assert candles == expected

def test_invalid_window_size():
    with pytest.raises(ValueError):
        sliding_window_vwap([], 0)
    with pytest.raises(ValueError):
        tumbling_candles([], 0)
