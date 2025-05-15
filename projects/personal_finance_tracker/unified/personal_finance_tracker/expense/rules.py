"""Expense categorization rules."""

import re
from datetime import datetime
from typing import List, Optional, Set, Union
from uuid import UUID, uuid4

from pydantic import Field, validator

from common.core.categorization.rule import Rule, TransactionRule
from common.core.models.transaction import BaseTransaction

from personal_finance_tracker.models.common import (
    ExpenseCategory,
    Transaction,
)


class ExpenseRule(TransactionRule):
    """Rule for expense categorization."""

    id: UUID = Field(default_factory=uuid4)
    category: ExpenseCategory
    
    # Rule conditions (at least one must be provided)
    keyword_patterns: List[str] = Field(default_factory=list)
    merchant_patterns: List[str] = Field(default_factory=list)
    amount_min: Optional[float] = None
    amount_max: Optional[float] = None
    
    # Business use percentage
    business_use_percentage: float = 100.0
    
    @validator("business_use_percentage")
    def validate_percentage(cls, v):
        """Validate business use percentage is between 0 and 100."""
        if v < 0 or v > 100:
            raise ValueError("Business use percentage must be between 0 and 100")
        return v
    
    def matches(self, transaction: Union[Transaction, BaseTransaction]) -> bool:
        """
        Check if transaction matches this rule.
        
        Args:
            transaction: The transaction to check
            
        Returns:
            True if the rule matches, False otherwise
        """
        # Skip if rule is inactive
        if not self.is_active:
            return False
        
        # Check amount range if specified
        if self.amount_min is not None and transaction.amount < self.amount_min:
            return False
        
        if self.amount_max is not None and transaction.amount > self.amount_max:
            return False
        
        # Check description against keyword patterns
        description_match = False
        if not self.keyword_patterns:
            description_match = True  # No patterns means automatic match
        else:
            for pattern in self.keyword_patterns:
                if re.search(pattern, transaction.description, re.IGNORECASE):
                    description_match = True
                    break
        
        if not description_match:
            return False
        
        # Check merchant name if available (assumed to be in tags)
        merchant_match = False
        if not self.merchant_patterns:
            merchant_match = True  # No patterns means automatic match
        else:
            for tag in transaction.tags:
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
    
    def apply(self, transaction: Union[Transaction, BaseTransaction]) -> dict:
        """
        Apply this rule to a transaction by returning fields to update.
        
        Args:
            transaction: The transaction to categorize
            
        Returns:
            Dictionary with category and business use percentage
        """
        return {
            "category": self.category,
            "business_use_percentage": self.business_use_percentage
        }