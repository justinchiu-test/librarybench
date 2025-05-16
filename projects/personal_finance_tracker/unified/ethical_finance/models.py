"""Common data models for the ethical finance package."""

from typing import Dict, List, Optional, Any, Union
from datetime import date, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from common.core.models.investment import (
    Investment as CommonInvestment,
    ESGRating as CommonESGRating,
    InvestmentHolding as BaseInvestmentHolding,
    Portfolio as BasePortfolio,
    EthicalCriteria as CommonEthicalCriteria,
    ImpactMetric as CommonImpactMetric,
    ImpactData as CommonImpactData
)
from common.core.models.transaction import BaseTransaction


class Investment(CommonInvestment):
    """Model representing an investment opportunity with ESG attributes."""
    
    # We're inheriting all fields from CommonInvestment:
    # id: Union[str, UUID] = Field(default_factory=uuid4)
    # name: str
    # sector: str
    # industry: str
    # market_cap: float
    # price: float
    # esg_ratings: ESGRating
    # carbon_footprint: float 
    # renewable_energy_use: float
    # diversity_score: float
    # board_independence: float
    # controversies: List[str] = Field(default_factory=list)
    # positive_practices: List[str] = Field(default_factory=list)
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class InvestmentHolding(BaseInvestmentHolding):
    """A specific holding of an investment in a portfolio."""
    
    # These fields come from BaseInvestmentHolding:
    # investment_id: str
    # shares: float
    # purchase_price: float
    # purchase_date: Union[date, datetime]
    # current_price: float
    # current_value: float
    
    # No additional fields needed
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class Portfolio(BasePortfolio):
    """A collection of investment holdings."""
    
    # These fields come from BasePortfolio:
    # id: Union[str, UUID] = Field(default_factory=uuid4)
    # name: str
    # holdings: List[InvestmentHolding] = Field(default_factory=list)
    # total_value: float
    # cash_balance: float
    # creation_date: Union[date, datetime]
    # last_updated: Union[date, datetime] = Field(default_factory=datetime.now)
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class ShareholderResolution(BaseModel):
    """Model representing a shareholder resolution with voting results."""
    
    company_id: str
    resolution_id: str
    year: int
    title: str
    category: str
    subcategory: str
    proposed_by: str
    status: str
    votes_for: Optional[float] = None
    votes_against: Optional[float] = None
    abstentions: Optional[float] = None
    company_recommendation: Optional[str] = None
    outcome: Optional[str] = None
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class Transaction(BaseTransaction):
    """Model representing a personal financial transaction."""
    
    # These fields come from BaseTransaction:
    # id: Union[str, UUID] = Field(default_factory=uuid4)
    # date: Union[date, datetime]
    # amount: float
    # description: str
    # transaction_type: Optional[str] = None
    # tags: List[str] = Field(default_factory=list)
    
    # Add ethical-specific fields
    vendor: str
    category: str
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class EthicalCriteria(CommonEthicalCriteria):
    """Customizable ethical screening criteria for investments."""
    
    # Converting from criteria_id to id (common model uses id)
    criteria_id: Optional[str] = None
    
    @classmethod
    def from_common_criteria(cls, common_criteria: CommonEthicalCriteria) -> "EthicalCriteria":
        """Convert from common model to specialized model."""
        return cls(
            id=common_criteria.id,
            criteria_id=str(common_criteria.id),  # For backward compatibility
            name=common_criteria.name,
            environmental=common_criteria.environmental,
            social=common_criteria.social,
            governance=common_criteria.governance,
            min_overall_score=common_criteria.min_overall_score,
            exclusions=common_criteria.exclusions,
            inclusions=common_criteria.inclusions
        )
    
    def to_common_criteria(self) -> CommonEthicalCriteria:
        """Convert to common model."""
        return CommonEthicalCriteria(
            id=self.id,
            name=self.name,
            environmental=self.environmental,
            social=self.social,
            governance=self.governance,
            min_overall_score=self.min_overall_score,
            exclusions=self.exclusions,
            inclusions=self.inclusions
        )
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class ImpactMetric(CommonImpactMetric):
    """Model for defining and tracking impact metrics."""
    
    # All fields come from CommonImpactMetric
    
    @classmethod
    def from_common_metric(cls, common_metric: CommonImpactMetric) -> "ImpactMetric":
        """Convert from common model to specialized model."""
        return cls(
            id=common_metric.id,
            name=common_metric.name,
            category=common_metric.category,
            unit=common_metric.unit,
            description=common_metric.description,
            higher_is_better=common_metric.higher_is_better,
            data_source=common_metric.data_source
        )
    
    def to_common_metric(self) -> CommonImpactMetric:
        """Convert to common model."""
        return CommonImpactMetric(
            id=self.id,
            name=self.name,
            category=self.category,
            unit=self.unit,
            description=self.description,
            higher_is_better=self.higher_is_better,
            data_source=self.data_source
        )
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class ImpactData(CommonImpactData):
    """Impact data for a specific investment in a specific year."""
    
    # All fields come from CommonImpactData
    
    @classmethod
    def from_common_data(cls, common_data: CommonImpactData) -> "ImpactData":
        """Convert from common model to specialized model."""
        return cls(
            investment_id=common_data.investment_id,
            year=common_data.year,
            metrics=common_data.metrics
        )
    
    def to_common_data(self) -> CommonImpactData:
        """Convert to common model."""
        return CommonImpactData(
            investment_id=self.investment_id,
            year=self.year,
            metrics=self.metrics
        )
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True