from data_engineer.etl.payload import BinaryPayloadSupport

def test_binary_payload_store_and_retrieve():
    b = BinaryPayloadSupport()
    data = {"a": 1, "b": [2,3]}
    b.store_payload("key1", data)
    out = b.retrieve_payload("key1")
    assert out == data
    assert b.retrieve_payload("nonexistent") is None
