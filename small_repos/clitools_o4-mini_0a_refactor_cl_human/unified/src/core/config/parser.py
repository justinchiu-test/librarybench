"""
Core configuration parser module for all CLI tools.
Provides parsers for JSON, INI, YAML, and TOML formats with uniform interface.
"""
import json
import os
import configparser
from typing import Any, Dict, List, Optional, Union, TextIO

# Optional dependencies for YAML and TOML
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    import toml
    TOML_AVAILABLE = True
except ImportError:
    TOML_AVAILABLE = False


class ConfigParser:
    """Unified configuration parser supporting multiple file formats."""

    @staticmethod
    def parse_file(file_path: str) -> Dict[str, Any]:
        """
        Parse configuration from a file based on its extension.
        
        Args:
            file_path: Path to the configuration file
            
        Returns:
            Dict containing the parsed configuration
        
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file format is not supported
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        with open(file_path, 'r') as file:
            if ext == '.json':
                return ConfigParser.parse_json(file)
            elif ext == '.ini':
                return ConfigParser.parse_ini(file)
            elif ext in ('.yaml', '.yml'):
                return ConfigParser.parse_yaml(file)
            elif ext == '.toml':
                return ConfigParser.parse_toml(file)
            else:
                raise ValueError(f"Unsupported configuration format: {ext}")
    
    @staticmethod
    def parse_json(file: Union[str, TextIO]) -> Dict[str, Any]:
        """Parse JSON configuration."""
        if isinstance(file, str):
            with open(file, 'r') as f:
                return json.load(f)
        return json.load(file)
    
    @staticmethod
    def parse_ini(file: Union[str, TextIO], section: Optional[str] = None, 
                  preserve_sections: bool = False) -> Dict[str, Any]:
        """
        Parse INI configuration.
        
        Args:
            file: File path or file object
            section: Specific section to extract (default: None = all sections)
            preserve_sections: If True, maintain section hierarchy in the result
            
        Returns:
            Dict containing the parsed configuration
        """
        parser = configparser.ConfigParser()
        
        if isinstance(file, str):
            parser.read(file)
        else:
            parser.read_file(file)
        
        # Convert to dictionary
        if section:
            if section not in parser:
                return {}
            return ConfigParser._section_to_dict(parser[section])
        
        if preserve_sections:
            return {s: ConfigParser._section_to_dict(parser[s]) for s in parser.sections()}
        
        # Flatten all sections into a single dictionary, with 'DEFAULT' having the lowest priority
        result = {}
        if 'DEFAULT' in parser:
            result.update(ConfigParser._section_to_dict(parser['DEFAULT']))
        
        for sect in parser.sections():
            result.update(ConfigParser._section_to_dict(parser[sect]))
        
        return result
    
    @staticmethod
    def _section_to_dict(section: configparser.SectionProxy) -> Dict[str, Any]:
        """Convert a ConfigParser section to a dictionary with type inference."""
        result = {}
        for key, value in section.items():
            # Try to infer types (bool, int, float)
            if value.lower() in ('true', 'yes', 'on', '1'):
                result[key] = True
            elif value.lower() in ('false', 'no', 'off', '0'):
                result[key] = False
            else:
                try:
                    # Try int first, then float
                    result[key] = int(value)
                except ValueError:
                    try:
                        result[key] = float(value)
                    except ValueError:
                        # If not a number, keep as string
                        result[key] = value
        return result
    
    @staticmethod
    def parse_yaml(file: Union[str, TextIO]) -> Dict[str, Any]:
        """Parse YAML configuration."""
        if not YAML_AVAILABLE:
            raise ImportError("YAML parsing requires the PyYAML package. "
                             "Install it with: pip install PyYAML")
        
        if isinstance(file, str):
            with open(file, 'r') as f:
                return yaml.safe_load(f)
        return yaml.safe_load(file)
    
    @staticmethod
    def parse_toml(file: Union[str, TextIO]) -> Dict[str, Any]:
        """Parse TOML configuration."""
        if not TOML_AVAILABLE:
            raise ImportError("TOML parsing requires the toml package. "
                             "Install it with: pip install toml")
        
        if isinstance(file, str):
            with open(file, 'r') as f:
                return toml.load(f)
        return toml.load(file)
    
    @staticmethod
    def merge_configs(*configs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge multiple configuration dictionaries.
        Later configs override earlier ones for top-level keys.
        For nested dictionaries, they are merged recursively.
        
        Args:
            configs: Configuration dictionaries to merge
            
        Returns:
            Merged configuration dictionary
        """
        result = {}
        
        for config in configs:
            ConfigParser._deep_merge(result, config)
            
        return result
    
    @staticmethod
    def _deep_merge(target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Recursively merge nested dictionaries.
        
        Args:
            target: The target dictionary to merge into
            source: The source dictionary to merge from
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                ConfigParser._deep_merge(target[key], value)
            else:
                target[key] = value