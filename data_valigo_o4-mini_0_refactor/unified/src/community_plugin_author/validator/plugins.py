"""
Facade for plugin registration and retrieval for Community Plugin Author.
"""
from community_plugin_author.validator.plugins import (
    register_rule,
    get_rule,
    register_transformer,
    get_transformer,
)
__all__ = [
    'register_rule',
    'get_rule',
    'register_transformer',
    'get_transformer',
]