import time
from pipeline.backpressure import BackpressureController

def test_backpressure_control():
    bc = BackpressureController(threshold=1)
    start = time.time()
    bc.control(2)
    dur = time.time() - start
    assert dur >= 0.01
    bc.control(0)
