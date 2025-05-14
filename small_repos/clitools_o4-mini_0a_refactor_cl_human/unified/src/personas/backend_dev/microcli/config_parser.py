"""
Configuration parser for backend developer microservice CLIs.
Extends core config parser with microservice-specific functionality.
"""

import os
from typing import Any, Dict, List, Optional, Tuple, Union

from ....core.config.parser import ConfigParser


class MicroserviceConfigParser:
    """
    Configuration parser for microservices.
    Extends the core ConfigParser with microservice-specific functionality.
    """
    
    def __init__(self, 
                config_dir: Optional[str] = None,
                default_config: Optional[Dict[str, Any]] = None,
                env_prefix: str = "MS_"):
        """
        Initialize a new microservice configuration parser.
        
        Args:
            config_dir: Directory to search for config files
            default_config: Default configuration values
            env_prefix: Prefix for environment variables
        """
        self.config_dir = config_dir or os.path.join(os.getcwd(), "config")
        self.default_config = default_config or {}
        self.env_prefix = env_prefix
        self.config: Dict[str, Any] = {}
    
    def load_config(self, 
                  service_name: str,
                  environment: str = "development",
                  profiles: List[str] = None) -> Dict[str, Any]:
        """
        Load configuration for a microservice.
        
        Args:
            service_name: Name of the microservice
            environment: Deployment environment (e.g., development, production)
            profiles: Additional configuration profiles to load
            
        Returns:
            Merged configuration dictionary
        """
        profiles = profiles or []
        configs = []
        
        # Add default config
        configs.append(self.default_config)
        
        # Load base configuration
        base_config_file = os.path.join(self.config_dir, f"{service_name}.json")
        if os.path.exists(base_config_file):
            configs.append(ConfigParser.parse_file(base_config_file))
        
        # Load environment-specific configuration
        env_config_file = os.path.join(self.config_dir, f"{service_name}-{environment}.json")
        if os.path.exists(env_config_file):
            configs.append(ConfigParser.parse_file(env_config_file))
        
        # Load profile-specific configurations
        for profile in profiles:
            profile_config_file = os.path.join(self.config_dir, f"{service_name}-{profile}.json")
            if os.path.exists(profile_config_file):
                configs.append(ConfigParser.parse_file(profile_config_file))
        
        # Merge configurations
        self.config = ConfigParser.merge_configs(*configs)
        
        # Apply environment variable overrides
        self._apply_env_overrides()
        
        return self.config
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.
        
        Args:
            key: Key to get value for
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        # Support nested keys with dot notation
        parts = key.split('.')
        
        # Navigate to the nested value
        current = self.config
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        
        return current
    
    def get_endpoint(self, service: str, default: str = "") -> str:
        """
        Get an endpoint for a service from configuration.
        
        Args:
            service: Service to get endpoint for
            default: Default endpoint if not configured
            
        Returns:
            Endpoint URL
        """
        return self.get_value(f"endpoints.{service}", default)
    
    def get_db_config(self) -> Dict[str, str]:
        """
        Get database configuration.
        
        Returns:
            Database configuration dictionary
        """
        return self.get_value("database", {})
    
    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides to configuration."""
        env_vars = {}
        
        # Find environment variables with the prefix
        for key, value in os.environ.items():
            if key.startswith(self.env_prefix):
                # Remove prefix and convert to lowercase
                clean_key = key[len(self.env_prefix):].lower()
                
                # Replace underscore with dot for nested keys
                clean_key = clean_key.replace('__', '.')
                
                # Try to convert to appropriate type
                typed_value = self._parse_env_value(value)
                
                env_vars[clean_key] = typed_value
        
        # Apply overrides to config
        for key, value in env_vars.items():
            self._set_nested_value(key, value)
    
    def _set_nested_value(self, key: str, value: Any) -> None:
        """Set a nested value in the configuration."""
        parts = key.split('.')
        current = self.config
        
        # Navigate to the parent of the value to set
        for i, part in enumerate(parts[:-1]):
            if part not in current or not isinstance(current[part], dict):
                current[part] = {}
            current = current[part]
        
        # Set the value
        current[parts[-1]] = value
    
    def _parse_env_value(self, value: str) -> Any:
        """Parse an environment variable value to appropriate type."""
        # Boolean values
        if value.lower() in ('true', 'yes', 'on', '1'):
            return True
        if value.lower() in ('false', 'no', 'off', '0'):
            return False
        
        # Numeric values
        try:
            # Try as integer first
            return int(value)
        except ValueError:
            try:
                # Then as float
                return float(value)
            except ValueError:
                # Keep as string if not numeric
                return value