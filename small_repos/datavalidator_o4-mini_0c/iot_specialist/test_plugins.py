from telemetry.plugins import Plugin

class NoopPlugin(Plugin):
    pass

def test_default_process():
    p = Plugin()
    rec = {'x': 1}
    assert p.process(rec) == rec
