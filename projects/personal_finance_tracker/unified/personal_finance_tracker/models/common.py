"""Common data models for the personal finance tracker."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator

# Import from common library
from common.core.models.transaction import (
    TransactionType as CommonTransactionType, 
    AccountType as CommonAccountType,
    BusinessTransaction
)
from common.core.models.tax import (
    TaxPayment as CommonTaxPayment,
    TaxRate as CommonTaxRate,
    TaxDeduction as CommonTaxDeduction,
    TaxLiability as CommonTaxLiability
)


# Use the TransactionType from common library
TransactionType = CommonTransactionType

# Use the AccountType from common library
AccountType = CommonAccountType


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


# Use BusinessTransaction from common library but adapt it to our specific needs
class Transaction(BusinessTransaction):
    """
    Transaction model for the Personal Finance Tracker.
    
    Extends the BusinessTransaction from the common library with
    freelancer-specific fields and behaviors.
    """

    # Override category field to use our specific ExpenseCategory enum
    category: Optional[ExpenseCategory] = None
    
    # Make sure the account_id is required
    account_id: str

    class Config:
        """Pydantic configuration."""
        # This is necessary to allow field overrides
        extra = "allow"


from common.core.models.project import Client as CommonClient
from common.core.models.project import Project as CommonProject
from common.core.models.project import TimeEntry as CommonTimeEntry
from common.core.models.project import Invoice as CommonInvoice
from common.core.models.project import ProjectStatus


class Client(CommonClient):
    """
    Client model for Personal Finance Tracker.
    
    Extends the Client model from the common library.
    """
    pass


class Project(CommonProject):
    """
    Project model for Personal Finance Tracker.
    
    Extends the Project model from the common library.
    """
    # Override status field to be more flexible for backward compatibility
    status: Union[str, ProjectStatus] = ProjectStatus.ACTIVE
    
    # Make client_id required
    client_id: str


class TimeEntry(CommonTimeEntry):
    """
    Time entry model for tracking hours worked on projects.
    
    Extends the TimeEntry model from the common library.
    """
    pass


class Invoice(CommonInvoice):
    """
    Invoice model for Personal Finance Tracker.
    
    Extends the Invoice model from the common library.
    """
    # Make client_id required
    client_id: str


# Extend tax models from the common library
class TaxPayment(CommonTaxPayment):
    """
    Tax payment model for Personal Finance Tracker.
    
    Extends the TaxPayment model from the common library.
    """
    quarter: int  # Make quarter required for our implementation


class TaxRate(CommonTaxRate):
    """
    Tax rate model for Personal Finance Tracker.
    
    Extends the TaxRate model from the common library.
    """
    pass


class TaxDeduction(CommonTaxDeduction):
    """
    Tax deduction model for Personal Finance Tracker.
    
    Extends the TaxDeduction model from the common library.
    """
    pass
