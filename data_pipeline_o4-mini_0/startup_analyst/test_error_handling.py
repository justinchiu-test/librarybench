import pytest
from etllib.pipeline import Pipeline
from etllib.stages import InMemorySource, InMemorySink, MapperStage

def test_error_handling_skips_bad_records():
    data = [1, 2, 3, 4]
    def faulty(x):
        if x % 2 == 0:
            raise ValueError(f"bad {x}")
        return x
    source = InMemorySource(data)
    mapper = MapperStage(faulty)
    sink = InMemorySink()
    pipeline = Pipeline().add_stage(source).add_stage(mapper).add_stage(sink)
    pipeline.run()
    # Should process only odd numbers
    assert sink.storage == [1, 3]
    # Errors for 2 and 4
    assert len(pipeline.errors) == 2
    for stage, record, exc in pipeline.errors:
        assert stage is mapper
        assert record in (2, 4)
        assert isinstance(exc, ValueError)

def test_hooks_on_source_and_sink():
    data = ['a', 'b']
    source = InMemorySource(data)
    sink = InMemorySink()
    seen_pre_source = []
    seen_post_source = []
    seen_pre_sink = []
    seen_post_sink = []
    source.add_pre_hook(lambda r: seen_pre_source.append(('pre', r)))
    source.add_post_hook(lambda r: seen_post_source.append(('post', r)))
    sink.add_pre_hook(lambda r: seen_pre_sink.append(('pre', r)))
    sink.add_post_hook(lambda r: seen_post_sink.append(('post', r)))
    pipeline = Pipeline().add_stage(source).add_stage(sink)
    pipeline.run()
    assert seen_pre_source == [('pre', 'a'), ('pre', 'b')]
    assert seen_post_source == [('post', 'a'), ('post', 'b')]
    assert seen_pre_sink == [('pre', 'a'), ('pre', 'b')]
    assert seen_post_sink == [('post', 'a'), ('post', 'b')]
