"""
Configuration parsing utilities for ops engineers.
"""
from core.config.loader import parse_config_string
from core.utils import merge_dicts

# Expose functions
parse_config_string = parse_config_string
merge_dicts = merge_dicts