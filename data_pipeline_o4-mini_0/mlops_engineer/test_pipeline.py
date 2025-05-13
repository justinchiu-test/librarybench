import pytest
import os
import json
from pipeline import (
    Pipeline, ErrorHandlingFallback, ErrorHandlingRetry, ErrorHandlingSkip,
    JSONSerialization, BackpressureControl, DynamicReconfiguration,
    BuiltInBatch, BuiltInSort, MemoryUsageControl, Windowing,
    SamplingStage, BuiltInGroup, PipelineStage, BuiltInFilter,
    BuiltInMap, DataValidation, SchemaEnforcement, PluginSystem,
    CachingStage, TransientError, DataValidationError, SchemaEnforcementError
)

class DummyLogger:
    def __init__(self):
        self.logged = []
    def log(self, rec):
        self.logged.append(rec)

def test_error_handling_fallback():
    def fail_func(rec):
        if rec.get('x') > 0:
            raise Exception("fail")
        return rec
    stage = ErrorHandlingFallback(fail_func, defaults={'x': 0})
    data = [{'x':1}, {'x':-1}]
    out = list(stage.run(data))
    assert out[0]['x'] == 0
    assert out[1]['x'] == -1

def test_error_handling_retry():
    counter = {'cnt':0}
    def flaky(rec):
        if counter['cnt'] < 2:
            counter['cnt'] += 1
            raise TransientError()
        return rec
    stage = ErrorHandlingRetry(flaky, retries=3)
    data = [{'v':10}]
    out = list(stage.run(data))
    assert out == [{'v':10}]

def test_error_handling_skip():
    def bad(rec):
        if rec['v']==0:
            raise ValueError()
        return rec
    logger = DummyLogger()
    stage = ErrorHandlingSkip(bad, logger)
    data = [{'v':0},{'v':1}]
    out = list(stage.run(data))
    assert out == [{'v':1}]
    assert logger.logged == [{'v':0}]

def test_json_serialization():
    stage = JSONSerialization()
    data = [{'a':1}, {'b':2}]
    out = list(stage.run(data))
    assert out == [json.dumps({'a':1}), json.dumps({'b':2})]

def test_backpressure_control():
    stage = BackpressureControl(threshold=2)
    data = [{'i':i} for i in range(5)]
    out = list(stage.run(data))
    flags = [rec['_backpressure'] for rec in out]
    assert flags == [False, False, True, True, True]

def test_dynamic_reconfiguration():
    def f1(rec): return {'x':1}
    def f2(rec): return {'x':2}
    stage = DynamicReconfiguration(f1)
    out1 = list(stage.run([{}]))
    assert out1 == [{'x':1}]
    stage.set_function(f2)
    out2 = list(stage.run([{}]))
    assert out2 == [{'x':2}]

def test_built_in_batch_and_sort():
    batch = BuiltInBatch(batch_size=3)
    sorter = BuiltInSort(key='v')
    data = [{'v':3},{'v':1},{'v':2},{'v':5}]
    out_batches = list(batch.run(data))
    assert len(out_batches) == 2
    sorted1 = list(sorter.run(out_batches))
    assert sorted1[0] == [{'v':1},{'v':2},{'v':3}]
    assert sorted1[1] == [{'v':5}]

def test_memory_usage_control(tmp_path):
    batch = BuiltInBatch(batch_size=2)
    mem = MemoryUsageControl(memory_budget_bytes=10)
    data = [{'a':'x'*10},{'b':'y'*10},{'c':'z'}]
    batches = batch.run(data)
    out = list(mem.run(batches))
    # first batch spills
    assert isinstance(out[0], str) and os.path.exists(out[0])
    # read back
    with open(out[0]) as f:
        lines = f.readlines()
    assert json.loads(lines[0]) == {'a':'x'*10}
    # second batch small
    assert out[1] == [{'c':'z'}]
    os.remove(out[0])

def test_windowing():
    win = Windowing(window_size=3)
    data = [1,2,3,4]
    out = list(win.run(data))
    assert out == [[1,2,3],[2,3,4]]

def test_sampling_stage():
    samp = SamplingStage(fraction=1.0)
    data = list(range(5))
    out = list(samp.run(data))
    assert out == data
    samp0 = SamplingStage(fraction=0.0)
    out0 = list(samp0.run(data))
    assert out0 == []

def test_built_in_group():
    grp = BuiltInGroup(key='sid')
    data = [{'sid':1,'v':10},{'sid':2,'v':20},{'sid':1,'v':30}]
    out = list(grp.run(data))
    out = sorted(out, key=lambda x: list(x.keys())[0])
    assert out == [{1:[{'sid':1,'v':10},{'sid':1,'v':30}]},{2:[{'sid':2,'v':20}]}]

def test_pipeline_composition():
    sub = Pipeline(stages=[BuiltInMap(lambda rec: {'x':rec['v']*2})])
    stage = PipelineStage(sub)
    data = [{'v':3}]
    out = list(stage.run(data))
    assert out == [{'x':6}]

def test_filter_and_map():
    filt = BuiltInFilter(lambda rec: rec['v']>0)
    mp = BuiltInMap(lambda rec: {'v':rec['v']+1})
    data = [{'v':-1},{'v':0},{'v':2}]
    out = list(mp.run(filt.run(data)))
    assert out == [{'v':1},{'v':3}]

def test_data_validation_and_schema_enforcement():
    dv = DataValidation({'v':(0,10)})
    se = SchemaEnforcement({'v':int})
    good = {'v':5}
    badval = {'v':-1}
    badschema = {'v':'a'}
    assert list(se.run([good])) == [good]
    assert list(dv.run([good])) == [good]
    with pytest.raises(SchemaEnforcementError):
        list(se.run([badschema]))
    with pytest.raises(DataValidationError):
        list(dv.run([badval]))

def test_plugin_system():
    ps = PluginSystem()
    ps.register('double', lambda x: x*2)
    func = ps.get('double')
    assert func(3) == 6
    assert ps.get('none') is None

def test_caching_stage():
    counter = {'cnt':0}
    def lookup(k):
        counter['cnt'] += 1
        return k*10
    cs = CachingStage(lookup, key_field='id', out_field='val')
    data = [{'id':1},{'id':2},{'id':1}]
    out = list(cs.run(data))
    assert out == [{'id':1,'val':10},{'id':2,'val':20},{'id':1,'val':10}]
    assert counter['cnt'] == 2

def test_pipeline_full_flow():
    # compose several stages
    pipeline = Pipeline(version='v1')
    pipeline.add_stage(BuiltInMap(lambda rec: {'v':rec['x']}))
    pipeline.add_stage(ErrorHandlingFallback(lambda rec: rec if rec['v']>=0 else (_ for _ in ()).throw(Exception()), defaults={'v':0}))
    pipeline.add_stage(BuiltInFilter(lambda rec: rec['v']>0))
    pipeline.add_stage(JSONSerialization())
    data = [{'x':1},{'x':-1},{'x':2}]
    out = pipeline.run(data)
    assert out == [json.dumps({'v':1}), json.dumps({'v':2})]
    assert pipeline.version == 'v1'
