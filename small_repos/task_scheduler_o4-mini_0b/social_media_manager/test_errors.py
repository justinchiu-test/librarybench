from postscheduler.errors import register_error_handler, trigger_error

def test_register_and_trigger_error():
    called = []
    def handler(err):
        called.append(err)
    register_error_handler(handler)
    trigger_error("fail")
    assert called == ["fail"]
