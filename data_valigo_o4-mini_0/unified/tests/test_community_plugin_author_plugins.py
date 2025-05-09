import pytest
from community_plugin_author.validator.plugins import register_rule, get_rule, register_transformer, get_transformer

def test_rule_registration_and_retrieval():
    @register_rule('r1')
    def rule1(v, ctx): return v == 1
    assert get_rule('r1') is rule1

def test_profile_based_rule():
    @register_rule('r2', profile='p1')
    def rule2(v, ctx): return ctx.get('profile') == 'p1' and v == 2
    # default profile returns no match
    assert get_rule('r2', profile=None) is None
    assert get_rule('r2', profile='p1') is rule2

def test_transformer_registration_and_retrieval():
    @register_transformer('t1')
    def t1(v): return v + 1
    assert get_transformer('t1')(5) == 6
