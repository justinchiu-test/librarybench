"""Rule-based categorization engine shared across implementations."""

import re
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Pattern, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from common.core.models.transaction import BaseTransaction


class Rule(BaseModel, ABC):
    """
    Abstract base class for categorization rules.
    
    Defines the interface for all rules used in categorization
    across different persona implementations.
    """
    
    id: Union[str, UUID] = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    priority: int = 0  # Higher numbers have higher priority
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True
    
    @abstractmethod
    def matches(self, item: Any) -> bool:
        """
        Check if this rule matches the given item.
        
        Args:
            item: The item to check against this rule
            
        Returns:
            True if the rule matches, False otherwise
        """
        pass
    
    @abstractmethod
    def apply(self, item: Any) -> Any:
        """
        Apply this rule to the given item.
        
        Args:
            item: The item to apply this rule to
            
        Returns:
            The result of applying the rule
        """
        pass
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class TextMatchRule(Rule):
    """
    Rule that matches based on text patterns in a field.
    
    Used for simple substring or regex matching against text fields.
    """
    
    field_name: str
    pattern: str
    pattern_type: str = "contains"  # "contains", "starts_with", "ends_with", "regex", "exact"
    case_sensitive: bool = False
    
    _compiled_regex: Optional[Pattern] = None
    
    def matches(self, item: Any) -> bool:
        """
        Check if the item matches this rule based on text patterns.
        
        Args:
            item: The item to check against this rule
            
        Returns:
            True if the rule matches, False otherwise
        """
        # Extract the field value
        if not hasattr(item, self.field_name) and not isinstance(item, dict):
            return False
        
        field_value = getattr(item, self.field_name) if hasattr(item, self.field_name) else item.get(self.field_name)
        
        # Skip if field doesn't exist or is None
        if field_value is None:
            return False
        
        # Convert to string if needed
        if not isinstance(field_value, str):
            field_value = str(field_value)
        
        # Apply case sensitivity
        pattern = self.pattern
        if not self.case_sensitive:
            field_value = field_value.lower()
            pattern = pattern.lower()
        
        # Match based on pattern type
        if self.pattern_type == "contains":
            return pattern in field_value
        elif self.pattern_type == "starts_with":
            return field_value.startswith(pattern)
        elif self.pattern_type == "ends_with":
            return field_value.endswith(pattern)
        elif self.pattern_type == "exact":
            return field_value == pattern
        elif self.pattern_type == "regex":
            if self._compiled_regex is None:
                self._compiled_regex = re.compile(pattern, 0 if self.case_sensitive else re.IGNORECASE)
            return bool(self._compiled_regex.search(field_value))
        
        return False
    
    def apply(self, item: Any) -> Dict[str, Any]:
        """
        Apply this rule by returning a dictionary of fields to update.
        
        Args:
            item: The item to apply this rule to
            
        Returns:
            Dictionary of fields to update on the item
        """
        return {}  # Override in subclasses


class TransactionRule(TextMatchRule):
    """
    Rule for categorizing financial transactions.
    
    Used for both expense categorization and ethical transaction analysis.
    """
    
    category: str
    business_use_percentage: Optional[float] = None
    
    def apply(self, transaction: BaseTransaction) -> Dict[str, Any]:
        """
        Apply this rule to a transaction by returning fields to update.
        
        Args:
            transaction: The transaction to categorize
            
        Returns:
            Dictionary with category and optional business use percentage
        """
        result = {"category": self.category}
        
        if self.business_use_percentage is not None:
            result["business_use_percentage"] = self.business_use_percentage
            
        return result


class CompositeRule(Rule):
    """
    Rule that combines multiple other rules with logical operators.
    
    Allows for complex rule conditions using AND, OR, and NOT operators.
    """
    
    operator: str = "and"  # "and", "or", "not"
    rules: List[Rule]
    
    def matches(self, item: Any) -> bool:
        """
        Check if the item matches this composite rule.
        
        Args:
            item: The item to check against this rule
            
        Returns:
            True if the rule matches, False otherwise
        """
        if not self.rules:
            return False
        
        if self.operator == "and":
            return all(rule.matches(item) for rule in self.rules)
        elif self.operator == "or":
            return any(rule.matches(item) for rule in self.rules)
        elif self.operator == "not":
            # For NOT, we only consider the first rule
            return not self.rules[0].matches(item)
        
        return False
    
    def apply(self, item: Any) -> Dict[str, Any]:
        """
        Apply the highest priority matching rule to the item.
        
        Args:
            item: The item to apply this rule to
            
        Returns:
            Result of applying the highest priority matching rule
        """
        matching_rules = [rule for rule in self.rules if rule.matches(item)]
        
        if not matching_rules:
            return {}
        
        # Get the highest priority rule (highest priority value)
        highest_priority_rule = max(matching_rules, key=lambda r: r.priority)
        
        return highest_priority_rule.apply(item)


class ValueThresholdRule(Rule):
    """
    Rule that matches based on numeric value comparisons.
    
    Used for matching based on thresholds like amount, score, or percentage.
    """
    
    field_name: str
    operator: str  # "eq", "ne", "gt", "lt", "ge", "le", "between"
    value: float
    max_value: Optional[float] = None  # Used for "between" operator
    
    def matches(self, item: Any) -> bool:
        """
        Check if the item matches based on numeric comparison.
        
        Args:
            item: The item to check against this rule
            
        Returns:
            True if the rule matches, False otherwise
        """
        # Extract the field value
        if not hasattr(item, self.field_name) and not isinstance(item, dict):
            return False
        
        field_value = getattr(item, self.field_name) if hasattr(item, self.field_name) else item.get(self.field_name)
        
        # Skip if field doesn't exist or is None
        if field_value is None:
            return False
        
        # Ensure numeric value
        try:
            field_value = float(field_value)
        except (ValueError, TypeError):
            return False
        
        # Compare based on operator
        if self.operator == "eq":
            return field_value == self.value
        elif self.operator == "ne":
            return field_value != self.value
        elif self.operator == "gt":
            return field_value > self.value
        elif self.operator == "lt":
            return field_value < self.value
        elif self.operator == "ge":
            return field_value >= self.value
        elif self.operator == "le":
            return field_value <= self.value
        elif self.operator == "between" and self.max_value is not None:
            return self.value <= field_value <= self.max_value
        
        return False
    
    def apply(self, item: Any) -> Dict[str, Any]:
        """
        Apply this rule by returning a dictionary of fields to update.
        
        Args:
            item: The item to apply this rule to
            
        Returns:
            Dictionary of fields to update on the item
        """
        return {}  # Override in subclasses