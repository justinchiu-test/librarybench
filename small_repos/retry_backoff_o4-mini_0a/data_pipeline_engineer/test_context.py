from retrylib.context import ContextPropagation, retry_scope

def test_context_propagation_clone_and_update():
    ctx = ContextPropagation(run_id=1, version="v1")
    assert ctx.get("run_id") == 1
    ctx2 = ctx.clone()
    ctx2.update(version="v2", extra=123)
    assert ctx.get("version") == "v1"
    assert ctx2.get("version") == "v2"
    assert ctx2.get("extra") == 123

def test_retry_scope_context_manager():
    ctx = ContextPropagation(a=1)
    with retry_scope(ctx) as inner:
        inner.update(b=2)
    assert ctx.get("b") == 2
