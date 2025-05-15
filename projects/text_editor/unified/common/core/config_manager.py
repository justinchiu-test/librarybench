"""
Configuration management module for text editors.

This module provides functionality for managing configuration settings,
including loading, saving, and validating configuration values.
"""

import json
import os
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Union,
    TypeVar,
    Generic,
    Callable,
)
from pydantic import BaseModel, Field, ValidationError

T = TypeVar("T")


class ConfigValue(BaseModel, Generic[T]):
    """
    A configuration value with validation and metadata.

    This class wraps a configuration value with additional metadata,
    such as a description, default value, and validation function.
    """

    name: str
    value: T
    default: T
    description: str = ""
    category: str = "general"
    validator: Optional[Callable[[T], bool]] = None

    def validate(self) -> bool:
        """
        Validate the current value.

        Returns:
            True if the value is valid, False otherwise
        """
        if self.validator is None:
            return True

        try:
            return self.validator(self.value)
        except Exception:
            return False

    def reset(self) -> None:
        """Reset the value to its default."""
        self.value = self.default


class ConfigManager(BaseModel):
    """
    Manages configuration settings for text editors.

    This class provides functionality for managing configuration settings,
    including loading, saving, and validating configuration values.
    """

    config_path: Optional[str] = None
    values: Dict[str, ConfigValue] = Field(default_factory=dict)

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True
        json_encoders = {
            ConfigValue: lambda v: {
                "value": v.value,
                "default": v.default,
                "description": v.description,
                "category": v.category,
            }
        }

    def register(
        self,
        name: str,
        default: Any,
        description: str = "",
        category: str = "general",
        validator: Optional[Callable[[Any], bool]] = None,
    ) -> None:
        """
        Register a configuration value.

        Args:
            name: The name of the configuration value
            default: The default value
            description: A description of the configuration value
            category: The category of the configuration value
            validator: A function to validate the value
        """
        if name in self.values:
            raise ValueError(f"Configuration value '{name}' already exists")

        config_value = ConfigValue(
            name=name,
            value=default,
            default=default,
            description=description,
            category=category,
            validator=validator,
        )

        self.values[name] = config_value

    def get(self, name: str, default: Optional[Any] = None) -> Any:
        """
        Get a configuration value.

        Args:
            name: The name of the configuration value
            default: The default value to return if the value is not found

        Returns:
            The configuration value, or the default if not found
        """
        if name in self.values:
            return self.values[name].value
        return default

    def set(self, name: str, value: Any) -> bool:
        """
        Set a configuration value.

        Args:
            name: The name of the configuration value
            value: The new value

        Returns:
            True if the value was set, False otherwise
        """
        if name not in self.values:
            return False

        config_value = self.values[name]
        config_value.value = value

        return config_value.validate()

    def reset(self, name: str) -> bool:
        """
        Reset a configuration value to its default.

        Args:
            name: The name of the configuration value

        Returns:
            True if the value was reset, False otherwise
        """
        if name not in self.values:
            return False

        self.values[name].reset()
        return True

    def reset_all(self) -> None:
        """Reset all configuration values to their defaults."""
        for config_value in self.values.values():
            config_value.reset()

    def get_categories(self) -> List[str]:
        """
        Get all configuration categories.

        Returns:
            A list of category names
        """
        return list(set(config_value.category for config_value in self.values.values()))

    def get_values_by_category(self, category: str) -> Dict[str, ConfigValue]:
        """
        Get all configuration values in a category.

        Args:
            category: The category name

        Returns:
            A dictionary of configuration values in the category
        """
        return {
            name: config_value
            for name, config_value in self.values.items()
            if config_value.category == category
        }

    def load(self, config_path: Optional[str] = None) -> bool:
        """
        Load configuration from a file.

        Args:
            config_path: The path to the configuration file (if None, uses self.config_path)

        Returns:
            True if the configuration was loaded successfully, False otherwise
        """
        path = config_path or self.config_path

        if not path:
            return False

        if not os.path.exists(path):
            return False

        try:
            with open(path, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            # Update existing values with loaded data
            for name, value in config_data.items():
                if name in self.values:
                    if isinstance(value, dict) and "value" in value:
                        self.values[name].value = value["value"]
                    else:
                        self.values[name].value = value

            self.config_path = path
            return True

        except (json.JSONDecodeError, IOError):
            return False

    def save(self, config_path: Optional[str] = None) -> bool:
        """
        Save configuration to a file.

        Args:
            config_path: The path to the configuration file (if None, uses self.config_path)

        Returns:
            True if the configuration was saved successfully, False otherwise
        """
        path = config_path or self.config_path

        if not path:
            return False

        try:
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(path), exist_ok=True)

            # Save as a simple dictionary with just the values
            config_data = {
                name: {"value": config_value.value, "category": config_value.category}
                for name, config_value in self.values.items()
            }

            with open(path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2)

            self.config_path = path
            return True

        except IOError:
            return False

    def validate_all(self) -> Dict[str, bool]:
        """
        Validate all configuration values.

        Returns:
            A dictionary mapping configuration value names to validation results
        """
        return {
            name: config_value.validate() for name, config_value in self.values.items()
        }
