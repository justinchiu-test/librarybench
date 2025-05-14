from iot_fleet_manager.iot.dead_letter_queue import DeadLetterQueue

def test_enqueue_and_get_all():
    dlq = DeadLetterQueue()
    dlq.enqueue("task1")
    dlq.enqueue("task2")
    assert dlq.get_all() == ["task1", "task2"]

def test_clear():
    dlq = DeadLetterQueue()
    dlq.enqueue("t1")
    dlq.clear()
    assert dlq.get_all() == []
