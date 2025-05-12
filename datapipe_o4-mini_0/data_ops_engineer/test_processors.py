import pytest
import time
from pipeline.processors import Processor, validate_schema, retry_on_error, halt_on_error

class UpperCaseProcessor(Processor):
    def process(self, record):
        return str(record).upper()

def test_processor_subclass():
    p = UpperCaseProcessor()
    assert p.process("abc") == "ABC"

def test_validate_schema_success():
    record = {'a': 1, 'b': 2}
    schema = {'required': ['a', 'b']}
    assert validate_schema(record, schema) is True

def test_validate_schema_failure():
    record = {'a': 1}
    schema = {'required': ['a', 'b']}
    assert validate_schema(record, schema) is False

def test_retry_on_error_success_after_retry():
    calls = []
    class T:
        def __init__(self):
            self.count = 0
        @retry_on_error(times=2, backoff=0)
        def may_fail(self):
            self.count += 1
            calls.append(self.count)
            if self.count < 2:
                raise ValueError("fail")
            return "ok"
    t = T()
    result = t.may_fail()
    assert result == "ok"
    assert calls == [1, 2]

def test_retry_on_error_exhausts_and_raises():
    class T:
        def __init__(self):
            self.count = 0
        @retry_on_error(times=1, backoff=0)
        def always_fail(self):
            self.count += 1
            raise RuntimeError("always")
    t = T()
    with pytest.raises(RuntimeError):
        t.always_fail()

def test_halt_on_error_propagates():
    @halt_on_error
    def fn():
        raise Exception("halt")
    with pytest.raises(Exception):
        fn()
