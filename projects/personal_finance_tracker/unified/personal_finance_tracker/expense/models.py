"""Expense categorization models."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Pattern, Set, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator

from common.core.categorization.categorizer import AuditRecord as CommonAuditRecord
from common.core.categorization.categorizer import CategorizationResult as CommonCategorizationResult
from common.core.models.transaction import BaseTransaction

from personal_finance_tracker.models.common import ExpenseCategory, Transaction


# For backwards compatibility with existing code
CategorizationRule = None  # Will be imported from rules.py


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

    @classmethod
    def from_common_result(cls, result: CommonCategorizationResult, transaction_id: UUID = None) -> "CategorizationResult":
        """
        Convert a common CategorizationResult to our specialized version.
        
        Args:
            result: The common result to convert
            transaction_id: Optional transaction ID override
            
        Returns:
            Our specialized CategorizationResult
        """
        return cls(
            transaction_id=transaction_id or result.item_id,
            original_transaction=result.original_item,
            matched_rule=result.matched_rule,
            assigned_category=result.assigned_category,
            business_use_percentage=result.metadata.get("business_use_percentage"),
            confidence_score=result.confidence_score,
            is_mixed_use=result.metadata.get("is_mixed_use", False),
            notes=result.notes,
        )


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
    
    @classmethod
    def from_common_audit(cls, record: CommonAuditRecord) -> "AuditRecord":
        """
        Convert a common AuditRecord to our specialized version.
        
        Args:
            record: The common audit record to convert
            
        Returns:
            Our specialized AuditRecord
        """
        return cls(
            id=record.id,
            transaction_id=record.item_id,
            timestamp=record.timestamp,
            action=record.action,
            previous_state=record.previous_state,
            new_state=record.new_state,
            user_id=record.user_id,
            notes=record.notes,
        )


# Import after defining to avoid circular import issues
from personal_finance_tracker.expense.rules import ExpenseRule as CategorizationRule