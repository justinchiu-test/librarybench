from backend_developer.background_dispatcher import Dispatcher

def test_hot_reload_updates_config():
    dsp = Dispatcher()
    assert dsp.config['retry_count'] == 3
    dsp.hot_reload(retry_count=5, timeout=60, log_level='DEBUG')
    assert dsp.config['retry_count'] == 5
    assert dsp.config['timeout'] == 60
    assert dsp.config['log_level'] == 'DEBUG'
