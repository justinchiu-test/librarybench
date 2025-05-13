from config_manager.schema import compose_schema

def test_empty():
    assert compose_schema() == {}
