"""Personalization engine for dynamic content with nested data access."""

import re
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class PersonalizationConfig(BaseModel):
    """Configuration for personalization behavior."""

    token_pattern: str = Field(
        default=r"\{\{(\s*[\w\.]+\s*(?:\|\s*default\s*:\s*[^}]*)?)\}\}",
        description="Regex pattern for matching tokens",
    )
    allow_nested_access: bool = Field(
        default=True, description="Allow dot notation for nested data"
    )
    strict_mode: bool = Field(
        default=False, description="Raise errors on missing data in strict mode"
    )
    escape_html: bool = Field(
        default=True, description="HTML escape personalized content"
    )


class PersonalizationEngine:
    """Engine for handling personalization tokens with nested data access and fallbacks."""

    def __init__(self, config: Optional[PersonalizationConfig] = None) -> None:
        self.config = config or PersonalizationConfig()
        self.token_regex = re.compile(self.config.token_pattern)

    def personalize(self, template: str, data: Dict[str, Any]) -> str:
        """
        Replace personalization tokens with data values.

        Args:
            template: Template string with tokens like {{name}} or {{user.email|default:guest@email.com}}
            data: Dictionary containing personalization data

        Returns:
            Personalized content with tokens replaced
        """

        def replace_token(match: re.Match) -> str:
            token_content = match.group(1).strip()

            # Parse token and default value
            if "|" in token_content:
                token_path, default_part = token_content.split("|", 1)
                token_path = token_path.strip()

                # Extract default value
                default_match = re.match(r"default\s*:\s*(.*)", default_part.strip())
                default_value = default_match.group(1).strip() if default_match else ""
            else:
                token_path = token_content
                default_value = ""

            # Get value from data
            try:
                value = self._get_nested_value(data, token_path)

                if value is None:
                    if self.config.strict_mode and not default_value:
                        raise ValueError(f"Missing data for token '{token_path}'")
                    value = default_value
                else:
                    value = str(value)

                # HTML escape if configured
                if self.config.escape_html:
                    value = self._html_escape(value)

                return value

            except (KeyError, TypeError, AttributeError) as e:
                if self.config.strict_mode and not default_value:
                    raise ValueError(f"Missing data for token '{token_path}'") from e
                return default_value

        return self.token_regex.sub(replace_token, template)

    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get value from nested data structure using dot notation."""
        if not self.config.allow_nested_access or "." not in path:
            return data.get(path)

        keys = path.split(".")
        value = data

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            elif isinstance(value, list):
                # Handle list indexing
                try:
                    index = int(key)
                    if 0 <= index < len(value):
                        value = value[index]
                    else:
                        return None
                except (ValueError, IndexError):
                    return None
            else:
                return None

            if value is None:
                return None

        return value

    def _html_escape(self, text: str) -> str:
        """HTML escape text for safe rendering."""
        escape_map = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#x27;",
        }

        for char, escaped in escape_map.items():
            text = text.replace(char, escaped)

        return text

    def extract_tokens(self, template: str) -> Dict[str, Optional[str]]:
        """
        Extract all personalization tokens from a template.

        Returns:
            Dictionary mapping token paths to their default values
        """
        tokens = {}

        for match in self.token_regex.finditer(template):
            token_content = match.group(1).strip()

            if "|" in token_content:
                token_path, default_part = token_content.split("|", 1)
                token_path = token_path.strip()

                default_match = re.match(r"default\s*:\s*(.*)", default_part.strip())
                default_value = (
                    default_match.group(1).strip() if default_match else None
                )
            else:
                token_path = token_content
                default_value = None

            tokens[token_path] = default_value

        return tokens

    def validate_data(self, template: str, data: Dict[str, Any]) -> Dict[str, bool]:
        """
        Validate that all required tokens have data available.

        Returns:
            Dictionary mapping token paths to availability status
        """
        tokens = self.extract_tokens(template)
        validation_results = {}

        for token_path, default_value in tokens.items():
            try:
                value = self._get_nested_value(data, token_path)
                # Token is valid if value exists or has default
                validation_results[token_path] = (
                    value is not None or default_value is not None
                )
            except Exception:
                validation_results[token_path] = default_value is not None

        return validation_results
