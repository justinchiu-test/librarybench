import pytest
from pipeline.core import Pipeline, Stage
from pipeline.error_handlers import fallback_reads

class AddStage(Stage):
    name = 'add'
    def __call__(self, data, context):
        return data + 1

class MulStage(Stage):
    name = 'mul'
    def __call__(self, data, context):
        return data * 3

class FailStage(Stage):
    name = 'fail'
    def __call__(self, data, context):
        raise RuntimeError("error")

def test_pipeline_add_mul():
    p = Pipeline()
    p.add_stage(AddStage())
    p.add_stage(MulStage())
    assert p.run(2) == 9

def test_pipeline_remove_stage():
    p = Pipeline()
    p.add_stage(AddStage())
    p.add_stage(MulStage())
    p.remove_stage('add')
    assert p.run(2) == 6

def test_pipeline_fallback():
    p = Pipeline()
    p.add_stage(FailStage())
    p.context['error_handler_fallback'] = fallback_reads
    result = p.run([1, 2, 3])
    assert isinstance(result, list)
    assert result[0]['id'] == 'dummy'
