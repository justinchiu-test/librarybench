from taskqueue.queue import TaskQueue, WebDashboard

def test_webdashboard_render():
    q = TaskQueue()
    q.enqueue('p1')
    q.enqueue('p2')
    db = WebDashboard(q)
    html = db.render()
    assert 'Pending: 2' in html
    assert 'Running: 0' in html
    assert 'Finished: 0' in html
    assert 'DLQ: 0' in html
