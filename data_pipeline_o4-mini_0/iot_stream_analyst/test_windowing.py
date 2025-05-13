from streamkit.windowing import Windowing

def test_windows():
    w = Windowing(window_size=3, step=1)
    items = [1,2,3,4,5]
    assert w.windows(items) == [[1,2,3],[2,3,4],[3,4,5]]
