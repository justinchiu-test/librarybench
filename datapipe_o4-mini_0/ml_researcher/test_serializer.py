import pytest
from feature_pipeline.serializer import registry, SerializerRegistry

def test_register_and_serialize():
    local = SerializerRegistry()
    local.register("fmt", lambda data: f"out:{data}")
    assert local.serialize("fmt", 10) == "out:10"

def test_registry_global():
    registry.register("f", lambda d: d*2)
    assert registry.serialize("f", 3) == 6

def test_serialize_unknown():
    with pytest.raises(ValueError):
        registry.serialize("unknown", None)
