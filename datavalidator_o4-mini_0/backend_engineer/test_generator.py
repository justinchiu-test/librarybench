from validation import Schema, Field
from validation.generator import TestDataGenerator

def test_generate_basic_types():
    fields = [
        Field("a", int),
        Field("b", float),
        Field("c", bool),
        Field("d", str),
    ]
    schema = Schema(fields)
    data = TestDataGenerator.generate(schema)
    assert isinstance(data["a"], int)
    assert isinstance(data["b"], float)
    assert isinstance(data["c"], bool)
    assert isinstance(data["d"], str)
