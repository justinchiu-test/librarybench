import json

def encode(data):
    """
    Encode a Python data structure into a JSON string.
    Supports primitives, lists, dicts, and nested structures.
    """
    return json.dumps(data)

def decode(data_str):
    """
    Decode a JSON string back into a Python data structure.
    Raises ValueError (JSONDecodeError) on invalid input.
    """
    return json.loads(data_str)

def nested_structure_support(data):
    """
    Demonstrate support for nested data structures by performing
    a round-trip encode and decode, returning the resulting data.
    """
    return decode(encode(data))
