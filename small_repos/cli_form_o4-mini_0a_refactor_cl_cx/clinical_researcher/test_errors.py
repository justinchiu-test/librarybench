from form_system.errors import format_error

def test_format_error_highlight():
    msg = format_error('field1', 'oops', highlight=True)
    assert msg.startswith('**ERROR**')
    assert 'field1' in msg
    assert 'oops' in msg

def test_format_error_no_highlight():
    msg = format_error('f2', 'bad', highlight=False)
    assert msg.startswith('ERROR f2:')
