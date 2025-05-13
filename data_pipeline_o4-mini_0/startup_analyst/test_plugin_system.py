import pytest
from etllib.plugin_system import PluginSystem
from etllib.stages import InMemorySource, InMemorySink, MapperStage
from etllib.serializers import JSONSerialization, YAMLSerialization

def test_register_and_get_source():
    cls = PluginSystem.get('source', 'memory')
    assert cls is InMemorySource

def test_register_and_get_sink():
    cls = PluginSystem.get('sink', 'memory')
    assert cls is InMemorySink

def test_register_and_get_transform():
    cls = PluginSystem.get('transform', 'mapper')
    assert cls is MapperStage

def test_register_and_get_serializer_json():
    cls = PluginSystem.get('serializer', 'json')
    assert cls is JSONSerialization

def test_register_and_get_serializer_yaml():
    cls = PluginSystem.get('serializer', 'yaml')
    assert cls is YAMLSerialization

def test_get_nonexistent_plugin():
    assert PluginSystem.get('unknown', 'none') is None
