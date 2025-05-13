import protocol_dsl
import pytest

def test_run_tests_invoke_pytest(monkeypatch):
    # monkeypatch pytest.main to capture calls
    called = {}
    def fake_main(args):
        called['args'] = args
        return 0
    monkeypatch.setattr(pytest, 'main', fake_main)
    protocol_dsl.run_tests()
    assert called['args'] == []
