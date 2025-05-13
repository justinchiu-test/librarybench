import os
import json
import pickle
import pytest
from datetime import datetime, timedelta
from pipeline.framework import (
    Pipeline, ErrorHandlingFallback, ErrorHandlingRetry, ErrorHandlingSkip,
    JSONSerialization, BackpressureControl, DynamicReconfiguration, BuiltInBatch,
    BuiltInSort, MemoryUsageControl, Versioning, Windowing, SamplingStage,
    BuiltInGroup, PipelineComposition, BuiltInFilter, BuiltInMap,
    DataValidation, SchemaEnforcement, CachingStage
)
from pipeline.plugins import PluginSystem

def test_builtin_map_filter_sort_batch_group():
    data = [
        {'id': 1, 'timestamp': '2021-01-01T10:15:00', 'value': 10, 'user': 'a'},
        {'id': 2, 'timestamp': '2021-01-01T10:45:00', 'value': 20, 'user': 'b'},
        {'id': 3, 'timestamp': '2021-01-02T11:00:00', 'value': 5, 'user': 'a'},
    ]
    # map: add 1 to value
    m = BuiltInMap(lambda r: {**r, 'value': r['value']+1})
    data2 = m.process(data)
    assert data2[0]['value'] == 11
    # filter: value>11
    f = BuiltInFilter(lambda r: r['value'] > 11)
    data3 = f.process(data2)
    assert all(r['value'] > 11 for r in data3)
    # sort by timestamp
    s = BuiltInSort()
    sorted_data = s.process(data)
    times = [r['timestamp'] for r in sorted_data]
    assert times == sorted(times)
    # batch hourly
    b = BuiltInBatch(window='hour')
    batches = b.process(data)
    assert all('window_start' in x and 'records' in x for x in batches)
    # group by user
    g = BuiltInGroup('user')
    grouped = g.process(data)
    assert set(grouped.keys()) == {'a', 'b'}

def test_sampling_windowing():
    data = []
    base = datetime(2021,1,1,0,0,0)
    for i in range(10):
        data.append({'id': i, 'timestamp': (base + timedelta(hours=i)).isoformat()})
    # sample 0.5
    samp = SamplingStage(fraction=0.5)
    out = samp.process(data)
    assert len(out) == 5
    # tumbling windows by day
    w = Windowing(mode='tumbling', size=1, unit='day')
    tw = w.process(data)
    assert isinstance(tw, list)
    # sliding windows 2 hours
    w2 = Windowing(mode='sliding', size=2, unit='hour')
    sw = w2.process(data)
    assert all('window_start' in x and 'window_end' in x for x in sw)

def test_error_handling_skip_fallback_retry():
    data = [
        {'a':1,'b':2},
        {'a':3},
        {'a':5,'b':6}
    ]
    skip = ErrorHandlingSkip(['a','b'])
    out = skip.process(data)
    assert len(out) == 2
    assert len(skip.skipped) == 1
    # fallback on b
    fb = ErrorHandlingFallback(['b'])
    out2 = fb.process(data)
    # second record b gets 2 (last known)
    assert out2[1]['b'] == 2
    # retry: flaky function
    calls = {'count':0}
    def flaky(d):
        calls['count'] +=1
        if calls['count'] < 2:
            raise ValueError
        return ['ok']
    retry = ErrorHandlingRetry(flaky, retries=3, delay=0)
    res = retry.process(None)
    assert res == ['ok']
    with pytest.raises(Exception):
        bad = ErrorHandlingRetry(lambda x: (_ for _ in ()).throw(Exception()), retries=1, delay=0)
        bad.process(None)

def test_backpressure_memory_versioning_dynamic():
    data = list(range(5))
    bp = BackpressureControl(max_buffer=3)
    # small input
    assert bp.process(data[:3]) == data[:3]
    # large input triggers sleep but returns
    assert bp.process(data) == data
    # memory control
    m = MemoryUsageControl(max_records=3, spill_file='test_spill.pkl')
    out = m.process([1,2,3,4])
    assert isinstance(out, dict) and 'spill_file' in out
    assert os.path.exists('test_spill.pkl')
    os.remove('test_spill.pkl')
    # versioning stage
    v = Versioning('2.0','3.0')
    ver = v.process([1,2])
    assert ver['pipeline_version']=='2.0'
    assert ver['schema_version']=='3.0'
    assert ver['data']==[1,2]
    # dynamic reconfig
    p = Pipeline()
    dr = DynamicReconfiguration(p)
    dr.add_stage(bp)
    assert isinstance(p.stages[0], BackpressureControl)
    dr.remove_stage(BackpressureControl)
    assert p.stages == []

def test_json_serialization_and_composition():
    data = [{'x':1}]
    js = JSONSerialization()
    s = js.process(data)
    assert isinstance(s, str)
    assert json.loads(s) == data
    # pipeline composition
    p = PipelineComposition.compose([BuiltInMap(lambda r:{'y':r['x']*2}), JSONSerialization()])
    out = p.run([{'x':2}])
    assert json.loads(out) == [{'y':4}]

def test_schema_enforcement_validation_caching():
    data = [{'a':'1','b':'2'},{'a':'3','b':'4'}]
    schema = {'a': int, 'b': int}
    se = SchemaEnforcement(schema)
    out = se.process(data)
    assert isinstance(out[0]['a'], int)
    # validation
    json_schema = {'type':'object','properties':{'a':{'type':'integer'}},'required':['a']}
    dv = DataValidation(json_schema)
    dv.process([{'a':1}])
    with pytest.raises(Exception):
        dv.process([{'a':'no'}])
    # caching
    loader = lambda: {'k1':'v1'}
    cs = CachingStage(loader)
    recs = [{'key':'k1'},{'key':'k2'}]
    enriched = cs.process(recs)
    assert enriched[0]['lookup']=='v1'
    assert enriched[1]['lookup'] is None

def test_plugin_system():
    ps = PluginSystem()
    connector = object()
    ps.register('test', connector)
    assert ps.get('test') is connector
    assert ps.get('none') is None
