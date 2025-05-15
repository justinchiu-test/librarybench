"""Tax models shared across implementations."""

from datetime import date, datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class TaxPayment(BaseModel):
    """
    Tax payment model for tracking payments to tax authorities.
    
    Used for tax planning, compliance, and financial projections.
    """

    id: Union[str, UUID] = Field(default_factory=uuid4)
    date: Union[date, datetime]
    amount: float
    tax_year: int
    quarter: Optional[int] = None
    payment_method: str
    jurisdiction: str = "federal"  # e.g., "federal", "state", "local"
    confirmation_number: Optional[str] = None
    notes: Optional[str] = None
    
    @validator("amount")
    def validate_amount(cls, v):
        """Validate that amount is a positive number."""
        if v < 0:
            raise ValueError("Tax payment amount must be a positive number")
        return v
    
    @validator("tax_year")
    def validate_tax_year(cls, v):
        """Validate that tax year is reasonable."""
        current_year = datetime.now().year
        if v < 1900 or v > current_year + 1:
            raise ValueError(f"Tax year {v} is outside reasonable range")
        return v
    
    @validator("quarter")
    def validate_quarter(cls, v):
        """Validate that quarter is 1-4."""
        if v is not None and (v < 1 or v > 4):
            raise ValueError("Quarter must be between 1 and 4")
        return v


class TaxRate(BaseModel):
    """
    Tax rate model for a specific income bracket.
    
    Used for calculating tax obligations and financial planning.
    """

    bracket_min: float
    bracket_max: Optional[float] = None
    rate: float  # Percentage (0-100)
    tax_year: int
    jurisdiction: str = "federal"  # e.g., "federal", "state", "local"
    
    @validator("rate")
    def validate_rate(cls, v):
        """Validate that rate is between 0 and 100."""
        if v < 0 or v > 100:
            raise ValueError("Tax rate must be between 0 and 100")
        return v
    
    @validator("tax_year")
    def validate_tax_year(cls, v):
        """Validate that tax year is reasonable."""
        current_year = datetime.now().year
        if v < 1900 or v > current_year + 1:
            raise ValueError(f"Tax year {v} is outside reasonable range")
        return v


class TaxDeduction(BaseModel):
    """
    Tax deduction model for tracking deductible expenses.
    
    Used for tax optimization and financial planning.
    """

    id: Union[str, UUID] = Field(default_factory=uuid4)
    name: str
    amount: float
    tax_year: int
    category: str
    description: Optional[str] = None
    jurisdiction: str = "federal"
    receipt_path: Optional[str] = None
    
    @validator("amount")
    def validate_amount(cls, v):
        """Validate that amount is a positive number."""
        if v < 0:
            raise ValueError("Deduction amount must be a positive number")
        return v
    
    @validator("tax_year")
    def validate_tax_year(cls, v):
        """Validate that tax year is reasonable."""
        current_year = datetime.now().year
        if v < 1900 or v > current_year + 1:
            raise ValueError(f"Tax year {v} is outside reasonable range")
        return v


class TaxLiability(BaseModel):
    """
    Tax liability model for tracking calculated tax obligations.
    
    Used for tax planning, compliance, and financial projections.
    """

    id: Union[str, UUID] = Field(default_factory=uuid4)
    tax_year: int
    jurisdiction: str = "federal"
    income: float
    deductions: float
    taxable_income: float
    tax_amount: float
    payments_made: float = 0.0
    remaining_balance: float
    calculation_date: Union[date, datetime] = Field(default_factory=datetime.now)
    
    @validator("income", "tax_amount", "payments_made")
    def validate_positive_numbers(cls, v):
        """Validate that financial amounts are positive numbers."""
        if v < 0:
            raise ValueError("Value must be a positive number")
        return v
    
    @validator("tax_year")
    def validate_tax_year(cls, v):
        """Validate that tax year is reasonable."""
        current_year = datetime.now().year
        if v < 1900 or v > current_year + 1:
            raise ValueError(f"Tax year {v} is outside reasonable range")
        return v
    
    @validator("remaining_balance", always=True)
    def calculate_remaining_balance(cls, v, values):
        """Calculate remaining balance if not provided."""
        if "tax_amount" in values and "payments_made" in values:
            return values["tax_amount"] - values["payments_made"]
        return v