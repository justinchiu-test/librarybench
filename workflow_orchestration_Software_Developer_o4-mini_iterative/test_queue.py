import time
from task_manager.queue import TaskQueue

def test_fifo_order():
    q = TaskQueue(max_workers=1)
    out = []
    q.push(lambda: out.append(1))
    q.push(lambda: out.append(2))
    time.sleep(0.2)
    q.stop()
    assert out == [1,2]

def test_concurrency():
    q = TaskQueue(max_workers=2)
    out = []
    def job(i):
        time.sleep(0.1)
        out.append(i)
    for i in range(4):
        q.push(lambda i=i: job(i))
    time.sleep(0.5)
    q.stop()
    assert sorted(out) == [0,1,2,3]
