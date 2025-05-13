import pytest
from pipeline.plugins import PluginSystem

def test_register_and_get():
    ps = PluginSystem()
    ps.register('foo', object())
    assert ps.get('foo') is not None

def test_load_module():
    ps = PluginSystem()
    mod = ps.load_module('json')
    import json
    assert mod is json
