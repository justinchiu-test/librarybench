"""Common data models for the personal finance tracker."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class TransactionType(str, Enum):
    """Transaction type enum."""

    INCOME = "income"
    EXPENSE = "expense"
    TAX_PAYMENT = "tax_payment"
    TRANSFER = "transfer"


class AccountType(str, Enum):
    """Account type enum."""

    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT_CARD = "credit_card"
    INVESTMENT = "investment"
    CASH = "cash"


class ExpenseCategory(str, Enum):
    """Expense category enum."""

    BUSINESS_SUPPLIES = "business_supplies"
    SOFTWARE = "software"
    MARKETING = "marketing"
    OFFICE_RENT = "office_rent"
    UTILITIES = "utilities"
    TRAVEL = "travel"
    MEALS = "meals"
    EQUIPMENT = "equipment"
    PROFESSIONAL_DEVELOPMENT = "professional_development"
    PROFESSIONAL_SERVICES = "professional_services"
    HEALTH_INSURANCE = "health_insurance"
    RETIREMENT = "retirement"
    PHONE = "phone"
    INTERNET = "internet"
    CAR = "car"
    HOME_OFFICE = "home_office"
    PERSONAL = "personal"
    OTHER = "other"


class AccountBalance(BaseModel):
    """Account balance model."""

    account_id: str
    account_name: str
    account_type: AccountType
    balance: float
    as_of_date: datetime


class Transaction(BaseModel):
    """Transaction model."""

    id: UUID = Field(default_factory=uuid4)
    date: datetime
    amount: float
    description: str
    transaction_type: TransactionType
    account_id: str
    category: Optional[ExpenseCategory] = None
    business_use_percentage: Optional[float] = None
    project_id: Optional[str] = None
    client_id: Optional[str] = None
    invoice_id: Optional[str] = None
    receipt_path: Optional[str] = None
    notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    @validator("business_use_percentage")
    def validate_business_percentage(cls, v):
        """Validate that business use percentage is between 0 and 100."""
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Business use percentage must be between 0 and 100")
        return v


class Client(BaseModel):
    """Client model."""

    id: str
    name: str
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    active: bool = True


class Project(BaseModel):
    """Project model."""

    id: str
    name: str
    client_id: str
    start_date: datetime
    end_date: Optional[datetime] = None
    status: str  # e.g., "active", "completed", "on_hold"
    hourly_rate: Optional[float] = None
    fixed_price: Optional[float] = None
    estimated_hours: Optional[float] = None
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class TimeEntry(BaseModel):
    """Time entry model for tracking hours worked on projects."""

    id: UUID = Field(default_factory=uuid4)
    project_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[float] = None
    description: str
    billable: bool = True
    tags: List[str] = Field(default_factory=list)

    @validator("duration_minutes", always=True)
    def calculate_duration(cls, v, values):
        """Calculate duration from start and end time if not provided."""
        if v is not None:
            return v
        if (
            "start_time" in values
            and "end_time" in values
            and values["end_time"] is not None
        ):
            delta = values["end_time"] - values["start_time"]
            return delta.total_seconds() / 60
        return None


class Invoice(BaseModel):
    """Invoice model."""

    id: str
    client_id: str
    project_id: Optional[str] = None
    issue_date: datetime
    due_date: datetime
    amount: float
    status: str  # e.g., "draft", "sent", "paid", "overdue"
    payment_date: Optional[datetime] = None
    description: Optional[str] = None
    line_items: List[Dict] = Field(default_factory=list)


class TaxPayment(BaseModel):
    """Tax payment model."""

    id: UUID = Field(default_factory=uuid4)
    date: datetime
    amount: float
    tax_year: int
    quarter: int
    payment_method: str
    confirmation_number: Optional[str] = None
    notes: Optional[str] = None


class TaxRate(BaseModel):
    """Tax rate for a specific income bracket."""

    bracket_min: float
    bracket_max: Optional[float] = None
    rate: float  # Percentage (0-100)
    tax_year: int
    jurisdiction: str = "federal"  # e.g., "federal", "state", "local"


class TaxDeduction(BaseModel):
    """Tax deduction model."""

    id: UUID = Field(default_factory=uuid4)
    name: str
    amount: float
    tax_year: int
    category: str
    description: Optional[str] = None
    receipt_path: Optional[str] = None
