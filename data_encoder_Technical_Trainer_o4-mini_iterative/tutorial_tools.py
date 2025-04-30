import json
import base64

def example_use_cases():
    """
    Returns a list of example use cases demonstrating encoding and decoding.
    Each example is a dict with 'name', 'input', 'encoded', and 'decoded' keys.
    """
    uses = []

    # Example 1: Base64 encoding/decoding
    input_str = "Hello World!"
    encoded_b64 = base64.b64encode(input_str.encode('utf-8')).decode('utf-8')
    decoded_b64 = base64.b64decode(encoded_b64.encode('utf-8')).decode('utf-8')
    uses.append({
        'name': 'base64',
        'input': input_str,
        'encoded': encoded_b64,
        'decoded': decoded_b64
    })

    # Example 2: Hex encoding/decoding
    encoded_hex = input_str.encode('utf-8').hex()
    decoded_hex = bytes.fromhex(encoded_hex).decode('utf-8')
    uses.append({
        'name': 'hex',
        'input': input_str,
        'encoded': encoded_hex,
        'decoded': decoded_hex
    })

    # Example 3: JSON serialization/deserialization
    obj = {'message': 'Hello', 'value': 123}
    encoded_json = json.dumps(obj)
    decoded_json = json.loads(encoded_json)
    uses.append({
        'name': 'json',
        'input': obj,
        'encoded': encoded_json,
        'decoded': decoded_json
    })

    return uses

def tutorials():
    """
    Returns a list of step-by-step tutorial strings
    guiding developers on how to use the encoding/decoding tools.
    """
    return [
        "Step 1: Install the library: pip install tutorial-tools",
        "Step 2: Import the functions:\n    from tutorial_tools import example_use_cases, support_for_sets, nested_structure_handling",
        "Step 3: Use example_use_cases() to see various encoding/decoding examples.",
        "Step 4: Use support_for_sets(your_set) to encode and decode homogeneous sets.",
        "Step 5: Use nested_structure_handling(your_nested_data) to handle nested structures."
    ]

def support_for_sets(data):
    """
    Demonstrates encoding and decoding of a homogeneous set.
    - data: a set of JSON-serializable items
    Returns a dict with 'original', 'encoded', and 'decoded' keys.
    """
    if not isinstance(data, set):
        raise TypeError("Input must be a set")

    # Convert set to list for JSON serialization
    list_data = list(data)
    encoded = json.dumps(list_data)
    decoded_list = json.loads(encoded)
    decoded_set = set(decoded_list)

    return {
        'original': data,
        'encoded': encoded,
        'decoded': decoded_set
    }

def nested_structure_handling(data):
    """
    Shows how to handle encoding and decoding of nested structures,
    converting sets to lists so they can be JSON-serialized.
    - data: nested structure (dict, list, set combinations)
    Returns a dict with 'original', 'encoded', and 'decoded' keys.
    """

    def convert(obj):
        if isinstance(obj, set):
            # Convert each element in the set
            return [convert(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: convert(val) for key, val in obj.items()}
        elif isinstance(obj, list):
            return [convert(item) for item in obj]
        else:
            return obj

    # Convert data to a JSON-serializable form
    converted = convert(data)
    encoded = json.dumps(converted)
    decoded = json.loads(encoded)

    return {
        'original': data,
        'encoded': encoded,
        'decoded': decoded
    }
