import re
from data_tools import document_api

def test_document_api_content():
    doc = document_api()
    # Should contain function names and signatures
    assert 'encode' in doc
    assert 'decode' in doc
    assert 'validate' in doc
    assert 'document_api' in doc
    # simple check of signature patterns
    assert re.search(r'encode\(data, config=None\)', doc)
    assert re.search(r'decode\(encoded_data\)', doc)
    assert re.search(r'validate\(data, schema\)', doc)
    assert re.search(r'document_api\(\)', doc)
    # check docstrings are present
    assert 'Generate documentation for the API functions.' in doc
