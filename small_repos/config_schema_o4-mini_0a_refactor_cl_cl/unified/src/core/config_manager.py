"""Core configuration manager class."""
import os
import copy
import json
from typing import Dict, Any, List, Optional, Union, Type, TypeVar, Callable

from ..loaders import load_config_file
from ..utils.path_utils import get_value, set_value
from ..utils.type_converter import convert_value, infer_type
from ..validation.errors import ValidationError, ConfigurationError
from ..validation.validators import validate_types, validate_with_jsonschema
from ..validation.schema_generator import generate_schema, schema_to_json
from .cache import ConfigCache
from .env_expander import expand_env_vars

# Global cache for configuration files
_cache = ConfigCache()

T = TypeVar('T')


class ConfigManager:
    """Core configuration manager class."""
    
    # Class-level shared configuration for compatibility with static methods
    _config = {}
    
    def __init__(self, 
                config_path: Optional[str] = None,
                config_data: Optional[Dict[str, Any]] = None,
                prompt: bool = False):
        """Initialize a configuration manager.
        
        Args:
            config_path: Optional path to a configuration file
            config_data: Optional configuration data
            prompt: Whether to prompt for missing values
            
        Raises:
            FileNotFoundError: If the configuration file does not exist
            ConfigurationError: If the configuration cannot be loaded
        """
        self._file_path = config_path
        self._data = {}
        self._prompt = prompt
        
        if config_data is not None:
            self._data = copy.deepcopy(config_data)
        elif config_path is not None:
            self.load(config_path)
        
    def load(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from a file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            The loaded configuration
            
        Raises:
            FileNotFoundError: If the configuration file does not exist
            ConfigurationError: If the configuration cannot be loaded
        """
        # Check if the configuration is cached
        cached_config = _cache.get(config_path)
        if cached_config is not None:
            self._data = copy.deepcopy(cached_config)
            self._file_path = config_path
            return self._data
            
        try:
            config = load_config_file(config_path)
            
            # Expand environment variables
            self._data = expand_env_vars(config)
            
            # Cache the configuration
            _cache.set(config_path, self._data)
            
            self._file_path = config_path
            
            # Update the class-level configuration for static methods
            ConfigManager._config = self._data
            
            return self._data
        except Exception as e:
            raise ConfigurationError(str(e), file=config_path) from e
    
    def reload(self) -> Dict[str, Any]:
        """Reload the configuration from the original file.
        
        Returns:
            The reloaded configuration
            
        Raises:
            FileNotFoundError: If the configuration file does not exist
            ConfigurationError: If the configuration cannot be loaded
        """
        if self._file_path is None:
            raise ConfigurationError("No configuration file specified")
            
        # Invalidate the cache
        _cache.invalidate(self._file_path)
        
        return self.load(self._file_path)
        
    def get(self, 
           path: str, 
           default: Any = None, 
           prompt_missing: bool = False) -> Any:
        """Get a value from the configuration.
        
        Args:
            path: The path to the value using dot notation
            default: The default value to return if the path is not found
            prompt_missing: Whether to prompt for missing values
            
        Returns:
            The value at the specified path, or the default value if not found
        """
        try:
            value = get_value(self._data, path)
            return value
        except KeyError:
            if prompt_missing and self._prompt:
                from ..interactive.prompt import prompt_for_value
                value = prompt_for_value(path)
                self.set(path, value)
                return value
            
            if default is not None:
                return default
                
            raise KeyError(f"Path '{path}' not found in configuration")
            
    def set(self, path: str, value: Any) -> None:
        """Set a value in the configuration.
        
        Args:
            path: The path to the value using dot notation
            value: The value to set
        """
        # Check if we should try to maintain the same type
        try:
            current_value = get_value(self._data, path)
            current_type = type(current_value)
            
            # Try to convert the value to the current type
            if current_value is not None and not isinstance(value, current_type):
                try:
                    value = convert_value(value, current_type)
                except (ValueError, TypeError):
                    # If conversion fails, store the value as-is
                    pass
        except KeyError:
            # Path doesn't exist yet, no need to validate
            pass
            
        set_value(self._data, path, value)
        
        # Update the class-level configuration for static methods
        ConfigManager._config = self._data
        
        # Invalidate the cache if the configuration was loaded from a file
        if self._file_path is not None:
            _cache.invalidate(self._file_path)
            
    def validate_types(self, 
                      schema: Optional[Dict[str, Union[Type, str]]] = None) -> bool:
        """Validate the configuration against a type schema.
        
        Args:
            schema: Optional schema mapping keys to expected types
            
        Returns:
            True if the configuration is valid
            
        Raises:
            ValidationError: If the configuration is invalid
        """
        if schema is None:
            # Generate a schema based on the current values
            types_schema = {}
            for key, value in self._data.items():
                types_schema[key] = infer_type(value)
                
            schema = types_schema
            
        return validate_types(self._data, schema, filename=self._file_path)
        
    def export_json_schema(self, indent: Optional[int] = None) -> Union[Dict[str, Any], str]:
        """Export the configuration as a JSON schema.
        
        Args:
            indent: Optional indentation level for the JSON string
            
        Returns:
            A JSON schema object or string
        """
        schema = generate_schema(self._data)
        
        if indent is not None:
            return schema_to_json(schema, indent)
            
        return schema
        
    def expand_env_vars(self) -> None:
        """Expand environment variables in the configuration."""
        self._data = expand_env_vars(self._data)
        
        # Update the class-level configuration for static methods
        ConfigManager._config = self._data
        
    def prompt_missing(self, keys: Optional[List[str]] = None) -> None:
        """Prompt for missing values in the configuration.
        
        Args:
            keys: Optional list of keys to prompt for
        """
        if keys is None:
            # Find keys with None or empty string values
            keys = []
            
            def find_empty_values(data, prefix=""):
                for key, value in data.items():
                    path = f"{prefix}.{key}" if prefix else key
                    
                    if value is None or value == "":
                        keys.append(path)
                    elif isinstance(value, dict):
                        find_empty_values(value, path)
                        
            find_empty_values(self._data)
            
        # Prompt for each missing value
        from ..interactive.prompt import prompt_for_value
        
        for key in keys:
            value = prompt_for_value(key)
            self.set(key, value)
            
    def serialize(self) -> Dict[str, Any]:
        """Serialize the configuration to a dictionary.
        
        Returns:
            A deep copy of the configuration
        """
        return copy.deepcopy(self._data)
        
    def save(self, file_path: Optional[str] = None) -> None:
        """Save the configuration to a file.
        
        Args:
            file_path: Optional path to save the configuration to
            
        Raises:
            ConfigurationError: If the configuration cannot be saved
        """
        if file_path is None:
            if self._file_path is None:
                raise ConfigurationError("No file path specified")
            file_path = self._file_path
            
        # Determine the format based on the file extension
        ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if ext == '.json':
                with open(file_path, 'w') as f:
                    json.dump(self._data, f, indent=2)
            elif ext == '.yaml' or ext == '.yml':
                try:
                    import yaml
                except ImportError:
                    raise ConfigurationError("PyYAML is not installed")
                    
                with open(file_path, 'w') as f:
                    yaml.dump(self._data, f)
            elif ext == '.toml':
                try:
                    import toml
                except ImportError:
                    raise ConfigurationError("toml is not installed")
                    
                with open(file_path, 'w') as f:
                    toml.dump(self._data, f)
            else:
                raise ConfigurationError(f"Unsupported file format: {ext}")
                
            # Update the file path and cache
            self._file_path = file_path
            _cache.set(file_path, self._data)
        except Exception as e:
            raise ConfigurationError(f"Error saving configuration: {str(e)}")
            
    @classmethod
    def load(cls, config_path: str) -> Dict[str, Any]:
        """Load configuration from a file (class method).
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            The loaded configuration
            
        Raises:
            FileNotFoundError: If the configuration file does not exist
            ConfigurationError: If the configuration cannot be loaded
        """
        # Check if the configuration is cached
        cached_config = _cache.get(config_path)
        if cached_config is not None:
            cls._config = copy.deepcopy(cached_config)
            return cls._config
            
        try:
            config = load_config_file(config_path)
            
            # Expand environment variables
            cls._config = expand_env_vars(config)
            
            # Cache the configuration
            _cache.set(config_path, cls._config)
            
            return cls._config
        except Exception as e:
            raise ConfigurationError(str(e), file=config_path) from e
            
    @classmethod
    def get(cls, path: str, default: Any = None) -> Any:
        """Get a value from the configuration (class method).
        
        Args:
            path: The path to the value using dot notation
            default: The default value to return if the path is not found
            
        Returns:
            The value at the specified path, or the default value if not found
        """
        try:
            return get_value(cls._config, path, default)
        except KeyError:
            if default is not None:
                return default
                
            raise KeyError(f"Path '{path}' not found in configuration")
            
    @classmethod
    def set(cls, path: str, value: Any) -> None:
        """Set a value in the configuration (class method).
        
        Args:
            path: The path to the value using dot notation
            value: The value to set
        """
        set_value(cls._config, path, value)
        
    @classmethod
    def serialize(cls) -> Dict[str, Any]:
        """Serialize the configuration to a dictionary (class method).
        
        Returns:
            A deep copy of the configuration
        """
        return copy.deepcopy(cls._config)