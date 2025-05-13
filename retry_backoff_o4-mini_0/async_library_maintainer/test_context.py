import pytest
from retry_lib.context import set_context, get_context, clear_context, get_all_context

def test_set_get_clear_context():
    clear_context()
    assert get_context('key') is None
    set_context('key','value')
    assert get_context('key') == 'value'
    all_ctx = get_all_context()
    assert all_ctx['key'] == 'value'
    clear_context()
    assert get_all_context() == {}
