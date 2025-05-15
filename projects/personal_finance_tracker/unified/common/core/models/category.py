"""Category models for financial data categorization."""

from enum import Enum
from typing import Dict, List, Optional, Union, Any, ClassVar
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, root_validator


class CategoryType(str, Enum):
    """Type of category for organizing and filtering."""

    INCOME = "income"
    EXPENSE = "expense"
    TAX = "tax"
    INVESTMENT = "investment"
    MIXED = "mixed"
    OTHER = "other"


class BaseCategory(BaseModel):
    """
    Base category model for all categorization systems.
    
    This abstract base class provides common fields for categorizing
    financial data across different persona implementations.
    """
    
    id: Union[str, UUID] = Field(default_factory=uuid4)
    name: str
    type: CategoryType
    description: Optional[str] = None
    parent_id: Optional[Union[str, UUID]] = None
    is_active: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the category to a dictionary."""
        return self.dict()


class ExpenseCategory(BaseCategory):
    """
    Expense category model for business vs. personal expenses.
    
    Specialized category model for expense categorization with
    business-specific attributes.
    """
    
    is_business: bool = False
    is_tax_deductible: bool = False
    default_business_percentage: Optional[float] = None
    
    @root_validator(skip_on_failure=True)
    def validate_business_category(cls, values):
        """Validate that business categories have proper attributes."""
        is_business = values.get("is_business", False)
        is_tax_deductible = values.get("is_tax_deductible", False)
        
        # If it's a business expense, it should be tax deductible by default
        if is_business and not is_tax_deductible:
            values["is_tax_deductible"] = True
            
        # If it has a business percentage, it should be a business expense
        if values.get("default_business_percentage") is not None and not is_business:
            values["is_business"] = True
            
        return values
    
    @classmethod
    def create_standard_categories(cls) -> List["ExpenseCategory"]:
        """Create a standard set of expense categories."""
        return [
            cls(name="Business Supplies", type=CategoryType.EXPENSE, 
                is_business=True, is_tax_deductible=True),
            cls(name="Software", type=CategoryType.EXPENSE, 
                is_business=True, is_tax_deductible=True),
            cls(name="Marketing", type=CategoryType.EXPENSE, 
                is_business=True, is_tax_deductible=True),
            cls(name="Office Rent", type=CategoryType.EXPENSE, 
                is_business=True, is_tax_deductible=True),
            cls(name="Utilities", type=CategoryType.EXPENSE, 
                is_business=True, is_tax_deductible=True, 
                default_business_percentage=50.0),
            cls(name="Travel", type=CategoryType.EXPENSE, 
                is_business=True, is_tax_deductible=True),
            cls(name="Meals", type=CategoryType.EXPENSE, 
                is_business=True, is_tax_deductible=True, 
                default_business_percentage=50.0),
            cls(name="Equipment", type=CategoryType.EXPENSE, 
                is_business=True, is_tax_deductible=True),
            cls(name="Professional Development", type=CategoryType.EXPENSE, 
                is_business=True, is_tax_deductible=True),
            cls(name="Professional Services", type=CategoryType.EXPENSE, 
                is_business=True, is_tax_deductible=True),
            cls(name="Health Insurance", type=CategoryType.EXPENSE, 
                is_business=True, is_tax_deductible=True),
            cls(name="Retirement", type=CategoryType.EXPENSE, 
                is_business=False, is_tax_deductible=True),
            cls(name="Phone", type=CategoryType.EXPENSE, 
                is_business=True, is_tax_deductible=True, 
                default_business_percentage=50.0),
            cls(name="Internet", type=CategoryType.EXPENSE, 
                is_business=True, is_tax_deductible=True, 
                default_business_percentage=50.0),
            cls(name="Car", type=CategoryType.EXPENSE, 
                is_business=True, is_tax_deductible=True, 
                default_business_percentage=50.0),
            cls(name="Home Office", type=CategoryType.EXPENSE, 
                is_business=True, is_tax_deductible=True, 
                default_business_percentage=25.0),
            cls(name="Personal", type=CategoryType.EXPENSE, 
                is_business=False, is_tax_deductible=False),
            cls(name="Other", type=CategoryType.EXPENSE, 
                is_business=False, is_tax_deductible=False),
        ]


class EthicalCategory(BaseCategory):
    """
    Ethical category model for values-based categorization.
    
    Specialized category model for ethical categorization with
    ESG (Environmental, Social, Governance) attributes.
    """
    
    dimension: str  # e.g., "environmental", "social", "governance"
    positive_impact: bool = True
    score_weight: float = 1.0
    exclusion_flag: bool = False
    inclusion_flag: bool = False
    
    @root_validator(skip_on_failure=True)
    def validate_ethical_category(cls, values):
        """Validate that ethical categories have proper attributes."""
        # Ensure dimension is one of the allowed values
        dimension = values.get("dimension", "").lower()
        if dimension not in ["environmental", "social", "governance", "other"]:
            raise ValueError("Dimension must be one of: environmental, social, governance, other")
        
        # Ensure weight is between 0 and 1
        weight = values.get("score_weight", 1.0)
        if weight < 0 or weight > 1:
            raise ValueError("Score weight must be between 0 and 1")
            
        # Cannot be both inclusion and exclusion
        if values.get("exclusion_flag") and values.get("inclusion_flag"):
            raise ValueError("Category cannot be both an inclusion and exclusion criteria")
            
        return values
    
    @classmethod
    def create_standard_categories(cls) -> List["EthicalCategory"]:
        """Create a standard set of ethical categories."""
        return [
            # Environmental categories
            cls(name="Renewable Energy", type=CategoryType.INVESTMENT, 
                dimension="environmental", positive_impact=True, 
                inclusion_flag=True, score_weight=0.8),
            cls(name="Carbon Emissions", type=CategoryType.INVESTMENT, 
                dimension="environmental", positive_impact=False, 
                score_weight=0.7),
            cls(name="Fossil Fuels", type=CategoryType.INVESTMENT, 
                dimension="environmental", positive_impact=False, 
                exclusion_flag=True, score_weight=0.9),
            cls(name="Water Usage", type=CategoryType.INVESTMENT, 
                dimension="environmental", positive_impact=False, 
                score_weight=0.6),
            
            # Social categories
            cls(name="Diversity & Inclusion", type=CategoryType.INVESTMENT, 
                dimension="social", positive_impact=True, 
                inclusion_flag=True, score_weight=0.7),
            cls(name="Human Rights", type=CategoryType.INVESTMENT, 
                dimension="social", positive_impact=True, 
                score_weight=0.8),
            cls(name="Labor Practices", type=CategoryType.INVESTMENT, 
                dimension="social", positive_impact=True, 
                score_weight=0.6),
            cls(name="Weapons Manufacturing", type=CategoryType.INVESTMENT, 
                dimension="social", positive_impact=False, 
                exclusion_flag=True, score_weight=0.9),
            
            # Governance categories
            cls(name="Board Independence", type=CategoryType.INVESTMENT, 
                dimension="governance", positive_impact=True, 
                score_weight=0.7),
            cls(name="Executive Compensation", type=CategoryType.INVESTMENT, 
                dimension="governance", positive_impact=False, 
                score_weight=0.6),
            cls(name="Corporate Ethics", type=CategoryType.INVESTMENT, 
                dimension="governance", positive_impact=True, 
                score_weight=0.8),
            cls(name="Transparency", type=CategoryType.INVESTMENT, 
                dimension="governance", positive_impact=True, 
                score_weight=0.7),
        ]