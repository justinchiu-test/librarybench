from audit_watcher.plugins import CICDPluginManager
from audit_watcher.watcher import Event

def test_plugin_trigger():
    manager = CICDPluginManager()
    called = []
    def plugin(evt):
        called.append(evt)
    manager.register(plugin)
    e = Event("delete", "/etc/passwd")
    manager.trigger(e)
    assert called == [e]
