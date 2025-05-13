import pytest
from scheduler.hooks import register_pre_post_hooks, apply_hooks, _pre_hooks, _post_hooks

logs = []

def pre_hook():
    logs.append('pre')

def post_hook(exception):
    logs.append(f'post:{"error" if exception else "ok"}')

def test_register_and_apply_hooks():
    register_pre_post_hooks(pre_hook, post_hook)
    @apply_hooks
    def successful():
        logs.append('run')
    @apply_hooks
    def failing():
        logs.append('runfail')
        raise ValueError()
    logs.clear()
    successful()
    assert logs == ['pre', 'run', 'post:ok']
    logs.clear()
    with pytest.raises(ValueError):
        failing()
    assert logs == ['pre', 'runfail', 'post:error']
