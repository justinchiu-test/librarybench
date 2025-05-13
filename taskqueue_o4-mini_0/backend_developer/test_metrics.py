from background_dispatcher import Dispatcher, SimpleBackend
import re

def test_emit_service_metrics():
    dsp = Dispatcher()
    dsp.set_role('alice', 'user')
    backend = SimpleBackend(dsp)
    dsp.register_pluggable_backend('simple', backend)
    dsp.use_backend('simple')
    # enqueue few tasks
    for _ in range(3):
        dsp.api_enqueue_image_task('alice', {'format': 'none'})
    metrics = dsp.emit_service_metrics()
    # check fields present
    assert re.search(r"jobs_total \d+", metrics)
    assert re.search(r"jobs_completed \d+", metrics)
    assert re.search(r"total_latency [0-9\.]+", metrics)
    assert re.search(r"errors \d+", metrics)
