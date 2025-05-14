from pipeline.window import windowed_operations

def test_tumbling_count():
    recs = [1, 2, 3, 4, 5]
    windows = windowed_operations(recs, 2)
    assert windows == [[1, 2], [3, 4], [5]]

def test_sliding_count():
    recs = [1, 2, 3, 4]
    windows = windowed_operations(recs, 3, slide=2)
    assert windows == [[1, 2, 3], [3, 4]]

def test_tumbling_time():
    recs = [(0, 'a'), (1, 'b'), (3, 'c'), (5, 'd')]
    windows = windowed_operations(recs, 2, window_type='time')
    assert windows == [[(0, 'a'), (1, 'b')], [(3, 'c')], [(5, 'd')]]
