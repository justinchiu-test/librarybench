from retry_toolkit.context_manager_api import retry_test_scope

def test_retry_test_scope():
    with retry_test_scope() as collector:
        @collector.record
        def f(x):
            return x * 2
        assert f(4) == 8
    history = collector.get_history()
    assert len(history) == 1
    assert history[0]["result"] == 8
