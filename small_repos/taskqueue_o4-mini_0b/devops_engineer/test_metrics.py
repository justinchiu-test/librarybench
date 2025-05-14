from taskqueue.queue import TaskQueue

def test_metrics_integration():
    q = TaskQueue()
    for i in range(3):
        tid = q.enqueue(f'p{i}')
        task = q.dequeue()
        q.finish(task)
    m = q.get_metrics()
    lines = m.splitlines()
    d = {l.split()[0]: int(l.split()[1]) for l in lines}
    assert d['task_processed_total'] == 3
    assert d['task_enqueued_total'] == 3
    assert d['task_failed_total'] == 0
