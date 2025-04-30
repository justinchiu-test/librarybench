import pytest
import json
import base64
import tutorial_tools

def test_example_use_cases_structure():
    uses = tutorial_tools.example_use_cases()
    # Should return a list of three examples
    assert isinstance(uses, list)
    assert len(uses) == 3
    names = {u['name'] for u in uses}
    assert names == {'base64', 'hex', 'json'}
    for u in uses:
        # Each example should have input, encoded, decoded
        assert set(u.keys()) == {'name', 'input', 'encoded', 'decoded'}
        # Decoded should match the original input
        assert u['decoded'] == u['input']

def test_tutorials_content():
    tuts = tutorial_tools.tutorials()
    assert isinstance(tuts, list)
    # Check minimum steps are present
    assert any("Step 1" in s for s in tuts)
    assert any("example_use_cases" in s for s in tuts)
    assert len(tuts) >= 5

def test_support_for_sets_valid():
    data = {1, 2, 3}
    result = tutorial_tools.support_for_sets(data)
    # Validate structure
    assert set(result.keys()) == {'original', 'encoded', 'decoded'}
    assert result['original'] == data
    # Encoded must be valid JSON list
    decoded_list = json.loads(result['encoded'])
    assert set(decoded_list) == data
    # Decoded back to set
    assert isinstance(result['decoded'], set)
    assert result['decoded'] == data

def test_support_for_sets_invalid_type():
    with pytest.raises(TypeError):
        tutorial_tools.support_for_sets([1, 2, 3])

def test_nested_structure_handling_simple():
    data = {'a': 1, 'b': {1, 2}, 'c': [3, 4]}
    result = tutorial_tools.nested_structure_handling(data)
    assert set(result.keys()) == {'original', 'encoded', 'decoded'}
    assert result['original'] == data
    # Check encoded is valid JSON
    decoded = json.loads(result['encoded'])
    # 'b' should have been converted to a list
    assert isinstance(decoded['b'], list)
    assert set(decoded['b']) == {1, 2}
    # 'c' remains a list
    assert decoded['c'] == [3, 4]
    # decoded in the result matches the JSON load
    assert result['decoded'] == decoded

def test_nested_structure_handling_deep():
    data = {
        'x': [{1, 2}, {'y': {3, 4}}],
        'z': "end"
    }
    result = tutorial_tools.nested_structure_handling(data)
    decoded = result['decoded']
    # Top-level must be dict
    assert isinstance(decoded, dict)
    # 'z' unchanged
    assert decoded['z'] == "end"
    # 'x' is a list
    assert isinstance(decoded['x'], list)
    # First element in x was a set -> list
    first = decoded['x'][0]
    assert isinstance(first, list)
    assert set(first) == {1, 2}
    # Second element is dict containing set -> list
    second = decoded['x'][1]
    assert isinstance(second, dict)
    assert isinstance(second['y'], list)
    assert set(second['y']) == {3, 4}
