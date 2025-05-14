"""Expense categorization models."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Pattern, Set, Union
from uuid import UUID, uuid4
import re

from pydantic import BaseModel, Field, validator

from personal_finance_tracker.models.common import ExpenseCategory, Transaction


class CategorizationRule(BaseModel):
    """Rule for expense categorization."""

    id: UUID = Field(default_factory=uuid4)
    name: str
    category: ExpenseCategory
    description: Optional[str] = None

    # Rule conditions (at least one must be provided)
    keyword_patterns: List[str] = Field(default_factory=list)
    merchant_patterns: List[str] = Field(default_factory=list)
    amount_min: Optional[float] = None
    amount_max: Optional[float] = None

    # Business use percentage
    business_use_percentage: float = 100.0

    # Rule priority (higher has precedence)
    priority: int = 0

    # Rule activation
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    @validator("business_use_percentage")
    def validate_percentage(cls, v):
        """Validate business use percentage is between 0 and 100."""
        if v < 0 or v > 100:
            raise ValueError("Business use percentage must be between 0 and 100")
        return v

    def matches(self, transaction: Transaction) -> bool:
        """Check if transaction matches this rule."""
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


class MixedUseItem(BaseModel):
    """Item with mixed business and personal use."""

    id: UUID = Field(default_factory=uuid4)
    name: str
    category: ExpenseCategory
    description: Optional[str] = None
    business_use_percentage: float
    documentation: Optional[str] = None

    @validator("business_use_percentage")
    def validate_percentage(cls, v):
        """Validate business use percentage is between 0 and 100."""
        if v < 0 or v > 100:
            raise ValueError("Business use percentage must be between 0 and 100")
        return v


class CategorizationResult(BaseModel):
    """Result of an expense categorization."""

    transaction_id: UUID
    original_transaction: Transaction
    matched_rule: Optional[CategorizationRule] = None
    assigned_category: Optional[ExpenseCategory] = None
    business_use_percentage: Optional[float] = None
    confidence_score: float = 0.0  # 0-1 confidence in categorization
    is_mixed_use: bool = False
    categorization_date: datetime = Field(default_factory=datetime.now)
    notes: Optional[str] = None

    @validator("confidence_score")
    def validate_confidence(cls, v):
        """Validate confidence score is between 0 and 1."""
        if v < 0 or v > 1:
            raise ValueError("Confidence score must be between 0 and 1")
        return v

    @validator("business_use_percentage")
    def validate_percentage(cls, v):
        """Validate business use percentage is between 0 and 100."""
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Business use percentage must be between 0 and 100")
        return v


class ExpenseSummary(BaseModel):
    """Summary of expenses by category."""

    period_start: datetime
    period_end: datetime
    total_expenses: float
    business_expenses: float
    personal_expenses: float
    by_category: Dict[ExpenseCategory, float] = Field(default_factory=dict)
    generation_date: datetime = Field(default_factory=datetime.now)


class AuditRecord(BaseModel):
    """Audit record for expense categorization."""

    id: UUID = Field(default_factory=uuid4)
    transaction_id: UUID
    timestamp: datetime = Field(default_factory=datetime.now)
    action: str  # e.g., "categorize", "recategorize", "mark_business", "mark_personal"
    previous_state: Optional[Dict] = None
    new_state: Dict
    user_id: Optional[str] = None
    notes: Optional[str] = None
