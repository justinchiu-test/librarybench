"""
Configuration parser for data scientist datapipeline CLIs.
Extends core config parser with datapipeline-specific functionality.
"""

import os
import configparser
from typing import Any, Dict, List, Optional, Union

from ....core.config.parser import ConfigParser


class DataPipelineConfigParser:
    """
    Configuration parser for data pipelines.
    Extends the core ConfigParser with data pipeline-specific functionality.
    """
    
    def __init__(self, 
                config_dir: Optional[str] = None,
                default_config: Optional[Dict[str, Any]] = None,
                env_prefix: str = "DP_"):
        """
        Initialize a new data pipeline configuration parser.
        
        Args:
            config_dir: Directory to search for config files
            default_config: Default configuration values
            env_prefix: Prefix for environment variables
        """
        self.config_dir = config_dir or os.path.join(os.getcwd(), "configs")
        self.default_config = default_config or {}
        self.env_prefix = env_prefix
        self.config: Dict[str, Any] = {}
    
    def load_config(self, 
                  pipeline_name: str,
                  environment: str = "development") -> Dict[str, Any]:
        """
        Load configuration for a data pipeline.
        
        Args:
            pipeline_name: Name of the data pipeline
            environment: Deployment environment (e.g., development, production)
            
        Returns:
            Merged configuration dictionary
        """
        configs = []
        
        # Add default config
        configs.append(self.default_config)
        
        # Define possible config file paths with different formats
        config_files = [
            # INI format (preferred for data scientists)
            os.path.join(self.config_dir, f"{pipeline_name}.ini"),
            os.path.join(self.config_dir, f"{pipeline_name}-{environment}.ini"),
            # JSON format (alternative)
            os.path.join(self.config_dir, f"{pipeline_name}.json"),
            os.path.join(self.config_dir, f"{pipeline_name}-{environment}.json"),
            # YAML format (for complex configurations)
            os.path.join(self.config_dir, f"{pipeline_name}.yaml"),
            os.path.join(self.config_dir, f"{pipeline_name}-{environment}.yaml"),
        ]
        
        # Load all existing config files
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    configs.append(ConfigParser.parse_file(config_file))
                except Exception as e:
                    print(f"Warning: Failed to parse {config_file}: {e}")
        
        # Merge configurations
        self.config = ConfigParser.merge_configs(*configs)
        
        # Apply environment variable overrides
        self._apply_env_overrides()
        
        return self.config
    
    def get_dataset_config(self, name: str) -> Dict[str, Any]:
        """
        Get configuration for a dataset.
        
        Args:
            name: Dataset name
            
        Returns:
            Dataset configuration
        """
        datasets = self.config.get("datasets", {})
        return datasets.get(name, {})
    
    def get_connector_config(self, name: str) -> Dict[str, Any]:
        """
        Get configuration for a data connector.
        
        Args:
            name: Connector name
            
        Returns:
            Connector configuration
        """
        connectors = self.config.get("connectors", {})
        return connectors.get(name, {})
    
    def get_transform_config(self, name: str) -> Dict[str, Any]:
        """
        Get configuration for a data transformation.
        
        Args:
            name: Transformation name
            
        Returns:
            Transformation configuration
        """
        transforms = self.config.get("transforms", {})
        return transforms.get(name, {})
    
    def get_pipeline_config(self) -> Dict[str, Any]:
        """
        Get pipeline-specific configuration.
        
        Returns:
            Pipeline configuration
        """
        return self.config.get("pipeline", {})
    
    def get_resource_config(self, resource_type: str, name: str) -> Dict[str, Any]:
        """
        Get configuration for any resource type.
        
        Args:
            resource_type: Type of resource (e.g., "datasets", "connectors")
            name: Resource name
            
        Returns:
            Resource configuration
        """
        resources = self.config.get(resource_type, {})
        return resources.get(name, {})
    
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
                # Keep as string if not numeric
                return value
    
    def parse_ini(self, file_path: str) -> Dict[str, Any]:
        """
        Parse an INI file with data pipeline-specific handling.
        
        Args:
            file_path: Path to INI file
            
        Returns:
            Parsed configuration dictionary
        """
        config = configparser.ConfigParser()
        config.read(file_path)
        
        result = {}
        
        # Process each section
        for section in config.sections():
            # Check if this is a special section format for nested configs
            if '.' in section:
                # Handle nested sections (e.g., "datasets.customers")
                parts = section.split('.')
                parent_key = parts[0]
                child_key = '.'.join(parts[1:])
                
                # Ensure parent exists
                if parent_key not in result:
                    result[parent_key] = {}
                
                # Add child section
                if isinstance(result[parent_key], dict):
                    result[parent_key][child_key] = dict(config[section])
            else:
                # Regular section
                result[section] = dict(config[section])
        
        # Convert values to appropriate types
        self._convert_types(result)
        
        return result
    
    def _convert_types(self, config: Dict[str, Any]) -> None:
        """
        Convert string values to appropriate types recursively.
        
        Args:
            config: Configuration dictionary to convert
        """
        for key, value in config.items():
            if isinstance(value, dict):
                self._convert_types(value)
            elif isinstance(value, str):
                # Convert value if it looks like a number or boolean
                config[key] = self._parse_env_value(value)