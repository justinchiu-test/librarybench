"""
Backend developer config parser adapter.

Provides backward compatibility for backend_dev.microcli.config_parser.
"""

from typing import Dict, List, Any

from ....cli_core.config import parse_config_files as core_parse_config_files


def parse_config_files(file_paths: List[str]) -> Dict[str, Any]:
    """
    Parse multiple configuration files and merge them.
    
    Args:
        file_paths (List[str]): List of configuration file paths.
        
    Returns:
        Dict[str, Any]: Merged configuration.
    """
    return core_parse_config_files(file_paths)