from iot_scheduler.lifecycle import register_lifecycle_hook, trigger_lifecycle

def test_lifecycle_hooks(tmp_path):
    calls = []
    def on_start():
        calls.append('start')
    def on_pre():
        calls.append('pre')
    def on_post():
        calls.append('post')
    register_lifecycle_hook('startup', on_start)
    register_lifecycle_hook('pre_shutdown', on_pre)
    register_lifecycle_hook('post_shutdown', on_post)
    trigger_lifecycle('startup')
    trigger_lifecycle('pre_shutdown')
    trigger_lifecycle('post_shutdown')
    assert calls == ['start', 'pre', 'post']
