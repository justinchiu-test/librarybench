"""Common transaction models shared across implementations."""

from datetime import date, datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class TransactionType(str, Enum):
    """Transaction type enum for all financial transactions."""

    INCOME = "income"
    EXPENSE = "expense"
    TAX_PAYMENT = "tax_payment"
    TRANSFER = "transfer"
    INVESTMENT = "investment"
    DIVIDEND = "dividend"
    INTEREST = "interest"


class AccountType(str, Enum):
    """Account type enum for all financial accounts."""

    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT_CARD = "credit_card"
    INVESTMENT = "investment"
    RETIREMENT = "retirement"
    CASH = "cash"
    OTHER = "other"


class BaseTransaction(BaseModel):
    """
    Base transaction model for all financial transactions.
    
    This abstract base class provides common fields for tracking
    financial transactions across different persona implementations.
    """

    id: Union[str, UUID] = Field(default_factory=uuid4)
    date: Union[date, datetime]
    amount: float
    description: str
    transaction_type: TransactionType
    
    # Optional fields
    account_id: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    
    @validator("amount")
    def validate_amount(cls, v):
        """Validate that amount is a valid number."""
        if not isinstance(v, (int, float)):
            raise ValueError("Amount must be a number")
        return v


class BusinessTransaction(BaseTransaction):
    """
    Transaction model for business transactions with additional fields.
    
    Extends the base transaction model with business-specific fields.
    """

    business_use_percentage: Optional[float] = None
    project_id: Optional[str] = None
    client_id: Optional[str] = None
    invoice_id: Optional[str] = None
    receipt_path: Optional[str] = None
    
    @validator("business_use_percentage")
    def validate_business_percentage(cls, v):
        """Validate that business use percentage is between 0 and 100."""
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Business use percentage must be between 0 and 100")
        return v


class InvestmentTransaction(BaseTransaction):
    """
    Transaction model for investment transactions with additional fields.
    
    Extends the base transaction model with investment-specific fields.
    """

    investment_id: Optional[str] = None
    shares: Optional[float] = None
    price_per_share: Optional[float] = None
    exchange_id: Optional[str] = None
    fees: Optional[float] = None
    
    @validator("shares")
    def validate_shares(cls, v):
        """Validate that shares is a positive number."""
        if v is not None and v < 0:
            raise ValueError("Shares must be a positive number")
        return v
    
    @validator("price_per_share")
    def validate_price(cls, v):
        """Validate that price is a positive number."""
        if v is not None and v < 0:
            raise ValueError("Price per share must be a positive number")
        return v


class Account(BaseModel):
    """Account model for all financial accounts."""

    id: str
    name: str
    account_type: AccountType
    balance: float
    currency: str = "USD"
    institution: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True


class AccountBalance(BaseModel):
    """Account balance at a specific point in time."""

    account_id: str
    account_name: str
    account_type: AccountType
    balance: float
    as_of_date: datetime