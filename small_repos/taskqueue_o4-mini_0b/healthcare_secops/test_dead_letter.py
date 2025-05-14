from pipeline.dead_letter import DeadLetterQueue

def test_dead_letter_queue():
    dlq = DeadLetterQueue()
    dlq.enqueue('t1', 'error1')
    dlq.enqueue('t2', 'error2')
    items = dlq.retrieve_all()
    assert len(items) == 2
    assert items[0]['task_id'] == 't1'
    assert items[1]['reason'] == 'error2'
    # queue is cleared
    assert dlq.retrieve_all() == []
