from retry.context import ContextPropagation

def test_context_propagation():
    ctx = ContextPropagation(service='s1', request_id='r1')
    data = ctx.get_context()
    assert data == {'service': 's1', 'request_id': 'r1'}
    # mutation of returned dict does not affect original
    data['x'] = 10
    assert 'x' in data
    assert 'x' not in ctx.context
