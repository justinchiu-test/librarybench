import pytest
from unified.src.data_engineer.dataschema.profile import ProfileRuleSet

def test_profile_rules():
    prs = ProfileRuleSet()
    prs.add_rule('signup', 'len_check', lambda x: len(x) > 3)
    prs.add_rule('signup', 'has_at', lambda x: '@' in x)
    result = prs.validate('signup', 'user@')
    assert result['len_check'] is True
    assert result['has_at'] is True
    assert prs.get_rules('nonexistent') == {}
