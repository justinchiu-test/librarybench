import pytest
from etllib.pipeline import Pipeline
from etllib.stages import InMemorySource, InMemorySink, MapperStage

def test_pipeline_with_transform_and_sink():
    source = InMemorySource([1, 2, 3])
    mapper = MapperStage(lambda x: x * 2)
    sink = InMemorySink()
    pipeline = Pipeline().add_stage(source).add_stage(mapper).add_stage(sink)
    result = pipeline.run()
    # run returns None when sink is used
    assert result is None
    assert sink.storage == [2, 4, 6]
    assert pipeline.errors == []

def test_pipeline_without_sink_returns_list():
    mapper = MapperStage(lambda x: x + 1)
    pipeline = Pipeline().add_stage(mapper)
    out = pipeline.run(input_data=[1, 2, 3])
    assert out == [2, 3, 4]

def test_pipeline_composition():
    mapper1 = MapperStage(lambda x: x + 1)
    mapper2 = MapperStage(lambda x: x * 10)
    pipeline1 = Pipeline().add_stage(mapper1)
    pipeline2 = Pipeline().add_stage(mapper2)
    combined = pipeline1 + pipeline2
    out = combined.run(input_data=[0, 1, 2])
    assert out == [10, 20, 30]
