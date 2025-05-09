import pytest
from data_handler import integration_test

def test_integration_test():
    assert integration_test() is True
