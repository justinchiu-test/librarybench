import pytest
from charlie_game_dev.game_service.storage import GameStore
from charlie_game_dev.game_service.metrics import metrics

@pytest.fixture(autouse=True)
def clear_metrics():
    metrics.counters = {'save_latency': 0, 'load_latency': 0, 'index_hit_rate': 0}
    yield

def test_metrics():
    # store_dir is not used in the body, so we drop that param entirely
    store = GameStore(str(__import__('tempfile').mkdtemp()))
    store.save({'a': 1})
    store.load()
    assert metrics.get('save_latency') >= 1
    assert metrics.get('load_latency') >= 0
