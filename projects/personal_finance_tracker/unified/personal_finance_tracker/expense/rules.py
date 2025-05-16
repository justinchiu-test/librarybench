"""Expense categorization rules."""

import re
from datetime import datetime
from typing import List, Optional, Set, Union, Dict, Any
from uuid import UUID, uuid4

from pydantic import Field, validator

from common.core.categorization.rule import Rule
from common.core.models.transaction import BaseTransaction

from personal_finance_tracker.models.common import (
    ExpenseCategory,
    Transaction,
)


class ExpenseRule(Rule):
    """Rule for expense categorization."""

    id: UUID = Field(default_factory=uuid4)
    name: str
    category: ExpenseCategory
    match_field: str = "description"  # Field that matches pattern
    pattern: str = ""
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    is_active: bool = True
    priority: int = 0
    
    # Rule conditions (at least one must be provided)
    keyword_patterns: List[str] = Field(default_factory=list)
    merchant_patterns: List[str] = Field(default_factory=list)
    amount_min: Optional[float] = None
    amount_max: Optional[float] = None
    
    # Business use percentage
    business_use_percentage: float = 100.0
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
    
    @validator("business_use_percentage")
    def validate_percentage(cls, v):
        """Validate business use percentage is between 0 and 100."""
        if v < 0 or v > 100:
            raise ValueError("Business use percentage must be between 0 and 100")
        return v
    
    def matches(self, item: Union[Transaction, BaseTransaction]) -> bool:
        """
        Check if transaction matches this rule.
        
        Args:
            item: The transaction to check
            
        Returns:
            True if the rule matches, False otherwise
        """
        # Skip if rule is inactive
        if not self.is_active:
            return False
        
        # Check amount range if specified
        if self.amount_min is not None and item.amount < self.amount_min:
            return False
        
        if self.amount_max is not None and item.amount > self.amount_max:
            return False
        
        # Check description against keyword patterns
        description_match = False
        if not self.keyword_patterns:
            description_match = True  # No patterns means automatic match
        else:
            for pattern in self.keyword_patterns:
                if re.search(pattern, item.description, re.IGNORECASE):
                    description_match = True
                    break
        
        if not description_match:
            return False
        
        # Check merchant name if available (assumed to be in tags)
        merchant_match = False
        if not self.merchant_patterns:
            merchant_match = True  # No patterns means automatic match
        else:
            for tag in item.tags:
                for pattern in self.merchant_patterns:
                    if re.search(pattern, tag, re.IGNORECASE):
                        merchant_match = True
                        break
                if merchant_match:
                    break
        
        if not merchant_match:
            return False
        
        # All conditions matched
        return True
    
    def apply(self, item: Union[Transaction, BaseTransaction]) -> Dict[str, Any]:
        """
        Apply this rule to a transaction by returning fields to update.
        
        Args:
            item: The transaction to categorize
            
        Returns:
            Dictionary with category and business use percentage
        """
        return {
            "category": self.category,
            "business_use_percentage": self.business_use_percentage,
            "metadata": {
                "rule_name": self.name,
                "is_mixed_use": self.business_use_percentage < 100.0,
            }
        }
    
    def get_match_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about this rule for matching purposes.
        
        Returns:
            Dictionary with rule metadata
        """
        return {
            "keyword_patterns": self.keyword_patterns,
            "merchant_patterns": self.merchant_patterns,
            "amount_min": self.amount_min,
            "amount_max": self.amount_max,
            "business_use_percentage": self.business_use_percentage
        }