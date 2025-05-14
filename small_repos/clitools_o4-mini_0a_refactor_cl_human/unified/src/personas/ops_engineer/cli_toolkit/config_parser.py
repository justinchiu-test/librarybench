"""
Configuration parser for ops engineer CLI toolkit.
Extends core config parser with infrastructure-specific functionality.
"""

import os
from typing import Any, Dict, List, Optional, Tuple, Union

from ....core.config.parser import ConfigParser


class InfraConfigParser:
    """
    Configuration parser for infrastructure tools.
    Extends the core ConfigParser with infrastructure-specific functionality.
    """
    
    def __init__(self, 
                config_dir: Optional[str] = None,
                default_config: Optional[Dict[str, Any]] = None,
                env_prefix: str = "INFRA_"):
        """
        Initialize a new infrastructure configuration parser.
        
        Args:
            config_dir: Directory to search for config files
            default_config: Default configuration values
            env_prefix: Prefix for environment variables
        """
        self.config_dir = config_dir or os.path.join(os.getcwd(), "config")
        self.default_config = default_config or {}
        self.env_prefix = env_prefix
        self.config: Dict[str, Any] = {}
        self.override_vars: Dict[str, Any] = {}
    
    def load_config(self, 
                  project_name: str,
                  environment: str = "development",
                  profiles: List[str] = None,
                  search_paths: List[str] = None) -> Dict[str, Any]:
        """
        Load configuration for an infrastructure project.
        
        Args:
            project_name: Name of the infrastructure project
            environment: Deployment environment (e.g., development, production)
            profiles: Additional configuration profiles to load
            search_paths: Additional paths to search for config files
            
        Returns:
            Merged configuration dictionary
        """
        profiles = profiles or []
        configs = []
        
        # Add default config
        configs.append(self.default_config)
        
        # Determine search paths
        if search_paths is None:
            search_paths = [
                self.config_dir,
                os.path.join(self.config_dir, project_name),
                os.path.join(os.getcwd(), "config"),
                os.path.join(os.getcwd(), "config", project_name),
                os.path.join(os.path.expanduser("~"), ".config", project_name),
            ]
        
        # Define file formats to try
        formats = ["yaml", "yml", "json", "toml"]
        
        # Load base configuration
        base_config = self._find_and_load_config(search_paths, project_name, formats)
        if base_config:
            configs.append(base_config)
        
        # Load environment-specific configuration
        env_config = self._find_and_load_config(search_paths, f"{project_name}-{environment}", formats)
        if env_config:
            configs.append(env_config)
        
        # Load profile-specific configurations
        for profile in profiles:
            profile_config = self._find_and_load_config(search_paths, f"{project_name}-{profile}", formats)
            if profile_config:
                configs.append(profile_config)
        
        # Merge configurations
        self.config = ConfigParser.merge_configs(*configs)
        
        # Apply environment variable overrides
        self._apply_env_overrides()
        
        # Apply programmatic overrides
        if self.override_vars:
            self.config = ConfigParser.merge_configs(self.config, self.override_vars)
        
        return self.config
    
    def set_override(self, key: str, value: Any) -> None:
        """
        Set a programmatic override for a configuration value.
        
        Args:
            key: Key to override
            value: Override value
        """
        # Support nested keys with dot notation
        if '.' in key:
            parts = key.split('.')
            current = self.override_vars
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value
        else:
            self.override_vars[key] = value
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.
        
        Args:
            key: Key to get value for (supports dot notation)
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
    
    def get_resource_config(self, resource_type: str, name: str) -> Dict[str, Any]:
        """
        Get configuration for an infrastructure resource.
        
        Args:
            resource_type: Type of resource (e.g., "servers", "databases")
            name: Resource name
            
        Returns:
            Resource configuration
        """
        resources = self.config.get(resource_type, {})
        return resources.get(name, {})
    
    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """
        Get configuration for a cloud provider.
        
        Args:
            provider: Provider name (e.g., "aws", "gcp", "azure")
            
        Returns:
            Provider configuration
        """
        providers = self.config.get("providers", {})
        return providers.get(provider, {})
    
    def get_deployment_config(self, deployment: str) -> Dict[str, Any]:
        """
        Get configuration for a deployment.
        
        Args:
            deployment: Deployment name
            
        Returns:
            Deployment configuration
        """
        deployments = self.config.get("deployments", {})
        return deployments.get(deployment, {})
    
    def _find_and_load_config(self, 
                             search_paths: List[str], 
                             base_name: str,
                             formats: List[str]) -> Optional[Dict[str, Any]]:
        """
        Find and load a configuration file.
        
        Args:
            search_paths: Paths to search for config files
            base_name: Base name of the config file (without extension)
            formats: File formats to try
            
        Returns:
            Loaded configuration or None if not found
        """
        for path in search_paths:
            for fmt in formats:
                file_path = os.path.join(path, f"{base_name}.{fmt}")
                if os.path.exists(file_path):
                    try:
                        return ConfigParser.parse_file(file_path)
                    except Exception as e:
                        print(f"Warning: Failed to parse {file_path}: {e}")
        
        return None
    
    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides to configuration."""
        env_vars = {}
        
        # Find environment variables with the prefix
        for key, value in os.environ.items():
            if key.startswith(self.env_prefix):
                # Remove prefix
                clean_key = key[len(self.env_prefix):]
                
                # Replace double underscore with dot for nested keys
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
                # List values (comma-separated)
                if ',' in value:
                    return [self._parse_env_value(v.strip()) for v in value.split(',')]
                
                # Keep as string if not numeric
                return value