import pytest
from pipeline import Processor

class AddProcessor(Processor):
    def process(self, record):
        return record + 10

def test_processor_base_not_implemented():
    p = Processor()
    with pytest.raises(NotImplementedError):
        p.process(5)

def test_processor_subclass():
    p = AddProcessor()
    assert p.process(5) == 15
