from audit_watcher.handlers import HandlerRegistry
from audit_watcher.watcher import Event

def test_handler_dispatch():
    registry = HandlerRegistry()
    calls = []
    def handler(evt):
        calls.append(evt.src_path)
    registry.register("delete", "/etc/", handler)
    e1 = Event("delete", "/etc/passwd")
    e2 = Event("create", "/etc/hosts")
    registry.dispatch(e1)
    registry.dispatch(e2)
    assert calls == ["/etc/passwd"]
