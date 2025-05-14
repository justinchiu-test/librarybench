from fs_watcher import Watcher

def test_rate_limit_storage():
    watcher = Watcher()
    watcher.apply_rate_limit('artifact_uploader', 5)
    assert watcher._rate_limits.get('artifact_uploader') == 5

def test_polling_strategy_storage():
    watcher = Watcher()
    strat = object()
    watcher.set_polling_strategy(strat)
    assert watcher._polling_strategy is strat
