from backend_developer.background_dispatcher import Dispatcher, SimpleBackend

def test_serializer_plugin():
    dsp = Dispatcher()
    dsp.set_role('bob', 'user')
    backend = SimpleBackend(dsp)
    dsp.register_pluggable_backend('simple', backend)
    dsp.use_backend('simple')
    called = {}
    def fake_serializer(data):
        called['data'] = data
    dsp.register_serializer('jpeg', fake_serializer)
    task_id = dsp.api_enqueue_image_task('bob', {'format': 'jpeg'})
    # serializer called in processing
    assert called['data'] == {'format': 'jpeg'}

def test_hooks_plugin():
    dsp = Dispatcher()
    dsp.set_role('eve', 'user')
    backend = SimpleBackend(dsp)
    dsp.register_pluggable_backend('simple', backend)
    dsp.use_backend('simple')
    pre_called = {}
    post_called = {}
    def pre_hook(tid, *args, **kwargs):
        pre_called['id'] = tid
    def post_hook(tid, result):
        post_called['result'] = result
    dsp.register_hook('pre_hooks', pre_hook)
    dsp.register_hook('post_hooks', post_hook)
    task_id = dsp.api_enqueue_image_task('eve', {'format': 'none'})
    assert pre_called['id'] == task_id
    assert post_called['result']['status'] == 'done'
