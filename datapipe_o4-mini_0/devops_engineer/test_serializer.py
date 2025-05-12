from pipeline.serializer import register_serializer, get_serializer

class Dummy:
    pass

def test_register_and_get_serializer():
    register_serializer('dummy', Dummy)
    assert get_serializer('dummy') is Dummy
