from retrylib.stop import MaxAttemptsStopCondition

def test_max_attempts_stop_condition():
    stop = MaxAttemptsStopCondition(3)
    assert not stop.should_stop(1)
    assert not stop.should_stop(2)
    assert stop.should_stop(3)
    assert stop.should_stop(10)
