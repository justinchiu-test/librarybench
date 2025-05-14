import os
from data_scientist.ml_pipeline.dead_letter import DeadLetterQueue

def test_dead_letter_queue(tmp_path):
    q = DeadLetterQueue(str(tmp_path))
    msg1 = {"x": 1}
    msg2 = {"y": 2}
    q.push(msg1)
    q.push(msg2)
    all_msgs = q.pop_all()
    assert len(all_msgs) == 2
    assert msg1 in all_msgs and msg2 in all_msgs
    # afterwards empty
    assert q.pop_all() == []
