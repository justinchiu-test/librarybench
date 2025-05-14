from retry.context import ContextPropagation

def test_context_propagation():
    ctx = ContextPropagation({'a': 1})
    assert ctx.get_context()['a'] == 1
    # ensure empty default
    empty = ContextPropagation()
    assert empty.get_context() == {}
