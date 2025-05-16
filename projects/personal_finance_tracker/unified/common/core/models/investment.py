"""Investment and portfolio models shared across implementations."""

from datetime import date, datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator, root_validator


class ESGRating(BaseModel):
    """Environmental, Social, and Governance ratings for an investment."""
    
    environmental: int
    social: int
    governance: int
    overall: int
    
    @root_validator(skip_on_failure=True)
    def validate_overall_score(cls, values):
        """Validate that the overall score is consistent with component scores."""
        env = values.get("environmental", 0)
        soc = values.get("social", 0) 
        gov = values.get("governance", 0)
        overall = values.get("overall", 0)
        
        # Check if overall is within a reasonable range of the average
        component_avg = (env + soc + gov) / 3
        if abs(overall - component_avg) > 15:  # Allow some variation in methodology
            raise ValueError(
                f"Overall score {overall} is too different from component average {component_avg:.1f}"
            )
        return values


class Investment(BaseModel):
    """
    Investment model representing an investment opportunity.
    
    Used for tracking investment options, ESG ratings, and performance.
    """

    id: Union[str, UUID] = Field(default_factory=uuid4)
    name: str
    sector: str
    industry: str
    market_cap: float
    price: float
    esg_ratings: ESGRating
    carbon_footprint: float
    renewable_energy_use: float
    diversity_score: float
    board_independence: float
    controversies: List[str] = Field(default_factory=list)
    positive_practices: List[str] = Field(default_factory=list)
    
    @property
    def has_major_controversies(self) -> bool:
        """Check if the investment has major controversies."""
        major_issues = ["human_rights", "fraud", "corruption", "environmental_disaster"]
        return any(issue in self.controversies for issue in major_issues)
    
    @validator("market_cap", "price", "carbon_footprint")
    def validate_positive_numbers(cls, v):
        """Validate that financial amounts are positive numbers."""
        if v < 0:
            raise ValueError("Value must be a positive number")
        return v
    
    @validator("renewable_energy_use", "diversity_score", "board_independence")
    def validate_percentage(cls, v):
        """Validate that percentages are between 0 and 1."""
        if v < 0 or v > 1:
            raise ValueError("Value must be between 0 and 1")
        return v


class InvestmentHolding(BaseModel):
    """
    Investment holding model for tracking specific holdings in a portfolio.
    
    Used for tracking portfolio composition, performance, and value.
    """

    investment_id: str
    shares: float
    purchase_price: float
    purchase_date: Union[date, datetime]
    current_price: float
    current_value: float
    
    @root_validator(skip_on_failure=True)
    def validate_current_value(cls, values):
        """Validate that current_value = shares * current_price."""
        shares = values.get("shares", 0)
        current_price = values.get("current_price", 0)
        current_value = values.get("current_value", 0)
        
        expected_value = shares * current_price
        if abs(current_value - expected_value) > 0.01:  # Allow for small rounding errors
            raise ValueError(
                f"Current value {current_value} does not match shares * price {expected_value}"
            )
        return values
    
    @property
    def return_percentage(self) -> float:
        """Calculate the percentage return on this holding."""
        return (self.current_price / self.purchase_price - 1) * 100


class Portfolio(BaseModel):
    """
    Portfolio model for tracking a collection of investment holdings.
    
    Used for portfolio analysis, performance tracking, and reporting.
    """

    id: Union[str, UUID] = Field(default_factory=uuid4)
    name: str
    holdings: List[InvestmentHolding] = Field(default_factory=list)
    total_value: float
    cash_balance: float
    creation_date: Union[date, datetime]
    last_updated: Union[date, datetime] = Field(default_factory=datetime.now)
    
    @root_validator(skip_on_failure=True)
    def validate_total_value(cls, values):
        """Validate that total_value equals the sum of all holdings' values."""
        holdings = values.get("holdings", [])
        total_value = values.get("total_value", 0)
        
        if not holdings:
            # If no holdings, total value should equal cash balance
            cash_balance = values.get("cash_balance", 0)
            if abs(total_value - cash_balance) > 0.01:  # Allow for small rounding errors
                raise ValueError(
                    f"Total value {total_value} does not match cash balance {cash_balance}"
                )
        else:
            # If there are holdings, validate total value
            holdings_sum = sum(holding.current_value for holding in holdings)
            if abs(total_value - holdings_sum) > 0.01:  # Allow for small rounding errors
                raise ValueError(
                    f"Total value {total_value} does not match holdings sum {holdings_sum}"
                )
        
        return values
    
    @property
    def total_assets(self) -> float:
        """Calculate total assets including cash."""
        return self.total_value + self.cash_balance
    
    def get_asset_allocation(self) -> Dict[str, float]:
        """Calculate the allocation percentage for each asset."""
        if not self.holdings:
            return {"cash": 100.0}
        
        allocation = {}
        total_assets = self.total_assets
        
        # Add cash allocation
        cash_percent = (self.cash_balance / total_assets) * 100
        allocation["cash"] = cash_percent
        
        # Add investment allocations
        for holding in self.holdings:
            holding_percent = (holding.current_value / total_assets) * 100
            allocation[holding.investment_id] = holding_percent
            
        return allocation


class EthicalCriteria(BaseModel):
    """
    Ethical screening criteria for investments.
    
    Used for evaluating investments against personalized ethical standards.
    """

    id: Union[str, UUID] = Field(default_factory=uuid4)
    name: str
    environmental: Dict[str, Any]
    social: Dict[str, Any]
    governance: Dict[str, Any]
    min_overall_score: float
    exclusions: List[str] = Field(default_factory=list)
    inclusions: List[str] = Field(default_factory=list)
    
    @root_validator(skip_on_failure=True)
    def validate_criteria_weights(cls, values):
        """Validate that criteria weights are included and sum approximately to 1."""
        for field_name in ['environmental', 'social', 'governance']:
            field_value = values.get(field_name, {})
            
            # Check that weight exists
            if 'weight' not in field_value:
                raise ValueError(f"{field_name} criteria must include a weight")
            
            # Ensure weight is between 0 and 1
            if field_value['weight'] < 0 or field_value['weight'] > 1:
                raise ValueError(f"{field_name} weight must be between 0 and 1")
        
        # Check that weights sum to approximately 1
        weights_sum = (
            values.get('environmental', {}).get('weight', 0) + 
            values.get('social', {}).get('weight', 0) + 
            values.get('governance', {}).get('weight', 0)
        )
        
        if abs(weights_sum - 1.0) > 0.01:  # Allow for small rounding errors
            raise ValueError(f"Criteria weights sum to {weights_sum}, expected 1.0")
            
        return values


class ImpactMetric(BaseModel):
    """
    Impact metric model for defining and tracking non-financial impacts.
    
    Used for measuring the social and environmental impact of investments.
    """

    id: Union[str, UUID] = Field(default_factory=uuid4)
    name: str
    category: str
    unit: str
    description: str
    higher_is_better: bool
    data_source: str


class ImpactData(BaseModel):
    """
    Impact data for a specific investment in a specific year.
    
    Used for tracking the actual impact of investments over time.
    """

    investment_id: str
    year: int
    metrics: Dict[str, float]
    
    @validator("year")
    def validate_year(cls, v):
        """Validate that year is reasonable."""
        current_year = datetime.now().year
        if v < 1900 or v > current_year + 1:
            raise ValueError(f"Year {v} is outside reasonable range")
        return v