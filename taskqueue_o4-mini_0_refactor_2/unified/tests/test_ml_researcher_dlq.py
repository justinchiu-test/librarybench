from ml_researcher.scheduler.dlq import DeadLetterQueue

def test_dlq_enqueue_get_all():
    dlq = DeadLetterQueue()
    dlq.enqueue('r1','error1')
    dlq.enqueue('r2','error2')
    all_items = dlq.get_all()
    assert len(all_items) == 2
    assert all_items[0]['run_id']=='r1'
    assert all_items[1]['reason']=='error2'
