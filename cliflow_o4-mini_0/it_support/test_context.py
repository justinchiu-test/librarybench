from onboarding.context import Context

def test_context_set_get():
    ctx = Context()
    ctx.set("a", 1)
    assert ctx.get("a") == 1
    assert ctx.get("b", 2) == 2

def test_to_dict():
    ctx = Context()
    ctx.set("x", "y")
    assert ctx.to_dict() == {"x": "y"}
