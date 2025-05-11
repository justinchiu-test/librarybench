import pytest
from unified.src.community_plugin_author import register_rule, Validator

@register_rule('r', profile='pA')
def ruleA(v, ctx): return ctx.get('profile') == 'pA'

@register_rule('r')
def ruleDefault(v, ctx): return ctx.get('profile') is None

def test_profile_switching():
    v1 = Validator(profile='pA')
    assert v1.validate('r', None) is True
    v2 = Validator()
    assert v2.validate('r', None) is True
