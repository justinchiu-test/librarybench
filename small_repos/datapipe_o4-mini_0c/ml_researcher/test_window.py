import pytest
from feature_pipeline.window import sliding_window

def test_sliding_window_basic():
    data = [1,2,3,4,5]
    windows = sliding_window(data, 3, 2)
    assert windows == [[1,2,3], [3,4,5]]

def test_sliding_window_invalid():
    with pytest.raises(ValueError):
        sliding_window([1,2,3], 0, 1)
