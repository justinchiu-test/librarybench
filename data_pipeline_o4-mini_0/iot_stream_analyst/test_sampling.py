import random
from streamkit.sampling import SamplingStage

def test_sampling_monkeypatch(monkeypatch):
    items = list(range(10))
    # force random.random to return 0.05 always
    monkeypatch.setattr(random, 'random', lambda: 0.05)
    s = SamplingStage(fraction=0.1)
    sampled = s.sample(items)
    # since 0.05 < 0.1, all selected
    assert sampled == items
