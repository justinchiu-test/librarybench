import pytest
from pipeline.processor import Processor

class DummyProcessor(Processor):
    def process(self, data):
        return data * 2

def test_processor_base_not_implemented():
    p = Processor()
    with pytest.raises(NotImplementedError):
        p.process(1)

def test_dummy_processor():
    dp = DummyProcessor()
    assert dp.process(3) == 6
