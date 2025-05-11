import pytest
from data_engineer.etl.pipeline import ETLPipeline

def test_extension_transform():
    p = ETLPipeline()
    def transform_upper(s):
        return s.upper()
    p.registerExtension('upper', transform_upper)
    ext = p.extension_registry.get('upper')
    assert ext('test') == 'TEST'

def test_propagate_multiple_contexts():
    p = ETLPipeline()
    results = []
    def collect(ctx):
        results.append(ctx)
        return ctx
    ctx1 = {'id': 1}
    ctx2 = {'id': 2}
    w1 = p.propagateContext(collect, ctx1)
    w2 = p.propagateContext(collect, ctx2)
    assert w1('x') == {'context': ctx1, 'args': ('x',), 'kwargs': {}}
    assert w2('y', key=5) == {'context': ctx2, 'args': ('y',), 'kwargs': {'key': 5}}
    assert results[0]['context'] is ctx1
    assert results[1]['context'] is ctx2
