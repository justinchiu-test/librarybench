from retry.stop_condition import MaxAttemptsStopCondition

def test_stop_condition():
    cond = MaxAttemptsStopCondition(max_attempts=3)
    assert not cond.should_stop(1)
    assert not cond.should_stop(2)
    assert cond.should_stop(3)
    assert cond.should_stop(10)
