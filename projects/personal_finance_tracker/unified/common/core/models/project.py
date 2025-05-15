"""Project and time tracking models shared across implementations."""

from datetime import datetime, date
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class ProjectStatus(str, Enum):
    """Status of a project throughout its lifecycle."""

    PLANNED = "planned"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Project(BaseModel):
    """
    Project model for tracking client projects.
    
    Used for organizing work, time tracking, and financial analysis
    across multiple persona implementations.
    """

    id: Union[str, UUID] = Field(default_factory=uuid4)
    name: str
    client_id: Optional[str] = None
    start_date: Union[date, datetime]
    end_date: Optional[Union[date, datetime]] = None
    status: ProjectStatus = ProjectStatus.ACTIVE
    hourly_rate: Optional[float] = None
    fixed_price: Optional[float] = None
    estimated_hours: Optional[float] = None
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator("end_date")
    def validate_end_date(cls, v, values):
        """Validate that end_date is after start_date if both are provided."""
        if v is not None and "start_date" in values:
            start = values["start_date"]
            if start > v:
                raise ValueError("End date must be after start date")
        return v
    
    @validator("hourly_rate", "fixed_price", "estimated_hours")
    def validate_positive_numbers(cls, v):
        """Validate that financial amounts are positive numbers."""
        if v is not None and v < 0:
            raise ValueError("Value must be a positive number")
        return v


class Client(BaseModel):
    """
    Client model for tracking information about clients.
    
    Used for organizing projects and managing client relationships.
    """

    id: Union[str, UUID] = Field(default_factory=uuid4)
    name: str
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    active: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)
    

class TimeEntry(BaseModel):
    """
    Time entry model for tracking hours worked on projects.
    
    Used for billing, project profitability analysis, and reporting.
    """

    id: Union[str, UUID] = Field(default_factory=uuid4)
    project_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[float] = None
    description: str
    billable: bool = True
    tags: List[str] = Field(default_factory=list)
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
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
    
    @validator("end_time")
    def validate_end_time(cls, v, values):
        """Validate that end_time is after start_time if both are provided."""
        if v is not None and "start_time" in values:
            if values["start_time"] > v:
                raise ValueError("End time must be after start time")
        return v


class Invoice(BaseModel):
    """
    Invoice model for tracking client billing.
    
    Used for revenue tracking, client relationship management, and tax reporting.
    """

    id: Union[str, UUID] = Field(default_factory=uuid4)
    client_id: str
    project_id: Optional[str] = None
    issue_date: Union[date, datetime]
    due_date: Union[date, datetime]
    amount: float
    status: str  # e.g., "draft", "sent", "paid", "overdue"
    payment_date: Optional[Union[date, datetime]] = None
    description: Optional[str] = None
    line_items: List[Dict[str, Any]] = Field(default_factory=list)
    
    @validator("due_date")
    def validate_due_date(cls, v, values):
        """Validate that due_date is after issue_date."""
        if "issue_date" in values:
            if v < values["issue_date"]:
                raise ValueError("Due date must be after issue date")
        return v
    
    @validator("amount")
    def validate_amount(cls, v):
        """Validate that amount is a positive number."""
        if v < 0:
            raise ValueError("Invoice amount must be a positive number")
        return v