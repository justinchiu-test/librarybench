from background_dispatcher import Dispatcher, SimpleBackend, NonRecoverableError

def test_dead_letter_queue():
    dsp = Dispatcher()
    dsp.set_role('user1', 'user')
    backend = SimpleBackend(dsp)
    dsp.register_pluggable_backend('simple', backend)
    dsp.use_backend('simple')
    def faulty_serializer(data):
        raise NonRecoverableError("bad")
    dsp.register_serializer('faulty', faulty_serializer)
    task_id = dsp.api_enqueue_image_task('user1', {'format': 'faulty'})
    # after run, should be in dead letter
    assert task_id in dsp.dead_letter
    status = dsp.query_task(task_id)
    assert status == 'failed'
