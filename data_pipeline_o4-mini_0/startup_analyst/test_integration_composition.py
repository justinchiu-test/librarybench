import pytest
from etllib.pipeline import Pipeline
from etllib.stages import InMemorySource, InMemorySink, MapperStage

def test_integration_complex_pipeline():
    # Source -> +1 -> *2 -> filter odd -> sink
    data = [0, 1, 2, 3, 4]
    source = InMemorySource(data)
    add_one = MapperStage(lambda x: x + 1)
    times_two = MapperStage(lambda x: x * 2)
    def filter_odd(x):
        if x % 2 == 0:
            return x
        # skip odd by returning None
        return None
    filter_stage = MapperStage(filter_odd)
    sink = InMemorySink()
    pipeline = Pipeline().add_stage(source).add_stage(add_one)
    pipeline2 = Pipeline().add_stage(times_two).add_stage(filter_stage).add_stage(sink)
    full = pipeline + pipeline2
    full.run()
    # Compute expected manually
    expected = []
    for x in data:
        y = (x + 1) * 2
        if y % 2 == 0:
            expected.append(y)
    assert sink.storage == expected
    assert full.errors == []
