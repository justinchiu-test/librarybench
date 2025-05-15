"""Financial projection utilities shared across implementations."""

import time
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID

import numpy as np
from pydantic import BaseModel, Field

from common.core.analysis.analyzer import BaseAnalyzer, AnalysisResult, AnalysisParameters
from common.core.analysis.time_series import TimeSeriesData, TimeSeriesAnalyzer


class ProjectionScenario(str, Enum):
    """Scenario types for financial projections."""
    
    OPTIMISTIC = "optimistic"
    BASELINE = "baseline"
    CONSERVATIVE = "conservative"
    STRESS_TEST = "stress_test"


class ProjectionParameters(AnalysisParameters):
    """
    Parameters for financial projections.
    
    Used to configure projection options and settings.
    """
    
    projection_length: int = 12  # months
    scenario: ProjectionScenario = ProjectionScenario.BASELINE
    include_income: bool = True
    include_expenses: bool = True
    include_investments: bool = True
    income_growth_rate: float = 0.0
    expense_growth_rate: float = 0.0
    investment_return_rate: float = 0.05
    emergency_fund_months: int = 6
    tax_rate: float = 0.25


class CashFlow(BaseModel):
    """
    Model for cash flow data.
    
    Used for tracking income, expenses, and net cash flow over time.
    """
    
    date: Union[date, datetime]
    income: float = 0.0
    expenses: float = 0.0
    net: float = 0.0
    cumulative: float = 0.0
    
    def __init__(self, **data):
        """Initialize with automatic net and cumulative calculation."""
        super().__init__(**data)
        if "net" not in data:
            self.net = self.income - self.expenses


class Projection(BaseModel):
    """
    Financial projection model.
    
    Used for forecasting future financial states based on different scenarios.
    """
    
    scenario: ProjectionScenario
    start_date: Union[date, datetime]
    end_date: Union[date, datetime]
    starting_balance: float
    cash_flows: List[CashFlow] = Field(default_factory=list)
    final_balance: float
    lowest_balance: float
    highest_balance: float
    runway_months: Optional[float] = None
    emergency_fund_status: str = "insufficient"
    tax_liability: Dict[str, float] = Field(default_factory=dict)
    confidence_level: float = 0.8
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProjectionResult(AnalysisResult):
    """
    Result of a financial projection analysis.
    
    Provides projected financial states across different scenarios.
    """
    
    baseline: Projection
    optimistic: Optional[Projection] = None
    conservative: Optional[Projection] = None
    stress_test: Optional[Projection] = None
    recommended_actions: List[str] = Field(default_factory=list)


class FinancialProjector(BaseAnalyzer[TimeSeriesData, ProjectionResult]):
    """
    Analyzer for financial projections.
    
    Used for forecasting future financial states and scenario analysis.
    """
    
    def analyze(
        self, historical_data: TimeSeriesData, parameters: Optional[ProjectionParameters] = None
    ) -> ProjectionResult:
        """
        Project future financial states based on historical data.
        
        Args:
            historical_data: Historical financial data
            parameters: Optional parameters to configure the projection
            
        Returns:
            ProjectionResult with different scenario projections
        """
        # Start timing for performance benchmarking
        start_time = time.time()
        
        # Set default parameters if not provided
        if parameters is None:
            parameters = ProjectionParameters()
        
        # Check cache
        cached_result = self._get_from_cache(UUID(), parameters)
        if cached_result:
            return cached_result
        
        # Calculate starting balance (last cumulative value)
        starting_balance = (
            historical_data.values[-1] if historical_data.values else 0.0
        )
        
        # Generate projections for baseline scenario
        baseline = self._generate_projection(
            historical_data,
            ProjectionScenario.BASELINE,
            parameters,
            income_factor=1.0,
            expense_factor=1.0,
            investment_factor=1.0,
        )
        
        # Generate projections for optimistic scenario
        optimistic = self._generate_projection(
            historical_data,
            ProjectionScenario.OPTIMISTIC,
            parameters,
            income_factor=1.1,
            expense_factor=0.9,
            investment_factor=1.2,
        )
        
        # Generate projections for conservative scenario
        conservative = self._generate_projection(
            historical_data,
            ProjectionScenario.CONSERVATIVE,
            parameters,
            income_factor=0.9,
            expense_factor=1.1,
            investment_factor=0.8,
        )
        
        # Generate projections for stress test scenario
        stress_test = self._generate_projection(
            historical_data,
            ProjectionScenario.STRESS_TEST,
            parameters,
            income_factor=0.7,
            expense_factor=1.2,
            investment_factor=0.5,
        )
        
        # Generate recommended actions
        recommended_actions = self._generate_recommendations(
            baseline, conservative, stress_test, parameters
        )
        
        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Create the result
        result = ProjectionResult(
            id=UUID(),
            subject_id=UUID(),
            subject_type="financial_data",
            analysis_type="projection",
            analysis_date=datetime.now(),
            processing_time_ms=processing_time_ms,
            result_summary={
                "starting_balance": starting_balance,
                "baseline_final_balance": baseline.final_balance,
                "runway_months": baseline.runway_months,
                "emergency_fund_status": baseline.emergency_fund_status,
            },
            detailed_results={
                "projection_length": parameters.projection_length,
                "scenarios": [s.value for s in ProjectionScenario],
                "historical_data_points": len(historical_data.values),
            },
            baseline=baseline,
            optimistic=optimistic,
            conservative=conservative,
            stress_test=stress_test,
            recommended_actions=recommended_actions,
        )
        
        # Save to cache
        self._save_to_cache(UUID(), result, parameters)
        
        return result
    
    def _generate_projection(
        self,
        historical_data: TimeSeriesData,
        scenario: ProjectionScenario,
        parameters: ProjectionParameters,
        income_factor: float = 1.0,
        expense_factor: float = 1.0,
        investment_factor: float = 1.0,
    ) -> Projection:
        """
        Generate a financial projection for a specific scenario.
        
        Args:
            historical_data: Historical financial data
            scenario: The projection scenario
            parameters: Projection parameters
            income_factor: Adjustment factor for income
            expense_factor: Adjustment factor for expenses
            investment_factor: Adjustment factor for investment returns
            
        Returns:
            Projection for the specified scenario
        """
        # Calculate starting balance (last cumulative value)
        starting_balance = (
            historical_data.values[-1] if historical_data.values else 0.0
        )
        
        # Determine start and end dates
        if historical_data.dates:
            start_date = historical_data.dates[-1]
            # Add 1 month to avoid overlap with historical data
            if isinstance(start_date, datetime):
                start_date = start_date.replace(
                    day=1, hour=0, minute=0, second=0, microsecond=0
                )
                start_date = (start_date.replace(day=28) + timedelta(days=4)).replace(day=1)
            else:
                # For date objects
                year = start_date.year + ((start_date.month) // 12)
                month = (start_date.month % 12) + 1
                start_date = date(year, month, 1)
        else:
            start_date = datetime.now().replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
        
        # Generate projection dates (monthly)
        projection_dates = []
        current_date = start_date
        for _ in range(parameters.projection_length):
            projection_dates.append(current_date)
            if isinstance(current_date, datetime):
                current_date = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1)
            else:
                # For date objects
                year = current_date.year + ((current_date.month) // 12)
                month = (current_date.month % 12) + 1
                current_date = date(year, month, 1)
        
        end_date = projection_dates[-1]
        
        # Adjust rates based on scenario
        income_growth = parameters.income_growth_rate * income_factor
        expense_growth = parameters.expense_growth_rate * expense_factor
        investment_return = parameters.investment_return_rate * investment_factor
        
        # Calculate historical averages
        avg_income, avg_expenses = self._calculate_historical_averages(historical_data)
        
        # Generate cash flows
        cash_flows = []
        cumulative_balance = starting_balance
        lowest_balance = starting_balance
        highest_balance = starting_balance
        
        for i, projection_date in enumerate(projection_dates):
            # Calculate projected income with growth
            income = avg_income * (1 + income_growth) ** (i / 12) if parameters.include_income else 0
            
            # Calculate projected expenses with growth
            expenses = avg_expenses * (1 + expense_growth) ** (i / 12) if parameters.include_expenses else 0
            
            # Calculate investment returns (monthly)
            investment_income = (
                cumulative_balance * (investment_return / 12)
                if parameters.include_investments and cumulative_balance > 0
                else 0
            )
            
            # Add investment income to total income
            income += investment_income
            
            # Calculate net and update cumulative
            net = income - expenses
            cumulative_balance += net
            
            # Track lowest and highest balances
            lowest_balance = min(lowest_balance, cumulative_balance)
            highest_balance = max(highest_balance, cumulative_balance)
            
            # Create cash flow record
            cash_flow = CashFlow(
                date=projection_date,
                income=income,
                expenses=expenses,
                net=net,
                cumulative=cumulative_balance,
            )
            
            cash_flows.append(cash_flow)
        
        # Calculate runway months (how long until funds are depleted)
        runway_months = None
        if avg_expenses > 0:
            for i, cf in enumerate(cash_flows):
                if cf.cumulative <= 0:
                    runway_months = i
                    break
            
            if runway_months is None and lowest_balance > 0:
                # If we didn't go negative, estimate based on final balance and burn rate
                if cash_flows[-1].net < 0:
                    runway_months = parameters.projection_length + (cash_flows[-1].cumulative / -cash_flows[-1].net)
                else:
                    runway_months = float('inf')  # Sustainable cash flow
        
        # Determine emergency fund status
        emergency_fund_status = "insufficient"
        if lowest_balance >= avg_expenses * parameters.emergency_fund_months:
            emergency_fund_status = "adequate"
        elif lowest_balance >= avg_expenses * (parameters.emergency_fund_months / 2):
            emergency_fund_status = "partial"
        
        # Calculate projected tax liability
        tax_liability = self._calculate_tax_liability(cash_flows, parameters.tax_rate)
        
        # Create the projection
        return Projection(
            scenario=scenario,
            start_date=start_date,
            end_date=end_date,
            starting_balance=starting_balance,
            cash_flows=cash_flows,
            final_balance=cash_flows[-1].cumulative if cash_flows else starting_balance,
            lowest_balance=lowest_balance,
            highest_balance=highest_balance,
            runway_months=runway_months,
            emergency_fund_status=emergency_fund_status,
            tax_liability=tax_liability,
            confidence_level=self._calculate_confidence_level(scenario),
            metadata={
                "income_growth_rate": income_growth,
                "expense_growth_rate": expense_growth,
                "investment_return_rate": investment_return,
                "avg_monthly_income": avg_income,
                "avg_monthly_expenses": avg_expenses,
            },
        )
    
    def _calculate_historical_averages(
        self, historical_data: TimeSeriesData
    ) -> Tuple[float, float]:
        """
        Calculate average monthly income and expenses from historical data.
        
        Args:
            historical_data: Historical financial data
            
        Returns:
            Tuple of (avg_income, avg_expenses)
        """
        # In a real implementation, the historical data would likely contain
        # separate income and expense data. Here we'll simulate it.
        
        # If we don't have historical data, use reasonable defaults
        if not historical_data.values:
            return 5000.0, 4000.0  # Default monthly income and expenses
        
        # Normally we would split the historical cash flows into income and expenses
        # For now, we'll use a heuristic based on the net cash flow
        
        # Assuming the TimeSeriesData values are net cash flows
        avg_net = np.mean(historical_data.values[-6:]) if len(historical_data.values) >= 6 else np.mean(historical_data.values)
        
        # Assuming expenses are about 80% of income on average
        avg_income = max(avg_net * 1.8, 0)
        avg_expenses = max(avg_income - avg_net, 0)
        
        return avg_income, avg_expenses
    
    def _calculate_tax_liability(
        self, cash_flows: List[CashFlow], tax_rate: float
    ) -> Dict[str, float]:
        """
        Calculate projected tax liability.
        
        Args:
            cash_flows: List of projected cash flows
            tax_rate: The effective tax rate
            
        Returns:
            Dictionary with tax liability information
        """
        # Group by year
        yearly_income = {}
        
        for cf in cash_flows:
            year = cf.date.year
            if year not in yearly_income:
                yearly_income[year] = 0
            
            yearly_income[year] += cf.income
        
        # Calculate tax for each year
        yearly_tax = {year: income * tax_rate for year, income in yearly_income.items()}
        
        # Calculate total and average
        total_tax = sum(yearly_tax.values())
        avg_monthly_tax = total_tax / len(cash_flows) if cash_flows else 0
        
        return {
            "yearly": yearly_tax,
            "total": total_tax,
            "avg_monthly": avg_monthly_tax,
            "effective_rate": tax_rate,
        }
    
    def _calculate_confidence_level(self, scenario: ProjectionScenario) -> float:
        """
        Calculate confidence level for a scenario.
        
        Args:
            scenario: The projection scenario
            
        Returns:
            Confidence level between 0 and 1
        """
        # Assign confidence levels based on the scenario
        if scenario == ProjectionScenario.BASELINE:
            return 0.8
        elif scenario == ProjectionScenario.OPTIMISTIC:
            return 0.2
        elif scenario == ProjectionScenario.CONSERVATIVE:
            return 0.6
        elif scenario == ProjectionScenario.STRESS_TEST:
            return 0.1
        
        return 0.5  # Default
    
    def _generate_recommendations(
        self,
        baseline: Projection,
        conservative: Projection,
        stress_test: Projection,
        parameters: ProjectionParameters,
    ) -> List[str]:
        """
        Generate financial recommendations based on projections.
        
        Args:
            baseline: Baseline scenario projection
            conservative: Conservative scenario projection
            stress_test: Stress test scenario projection
            parameters: Projection parameters
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Emergency fund recommendations
        if baseline.emergency_fund_status == "insufficient":
            recommendations.append(
                f"Build an emergency fund of {parameters.emergency_fund_months} months of expenses "
                f"(approximately ${parameters.emergency_fund_months * baseline.metadata['avg_monthly_expenses']:,.2f})."
            )
        elif baseline.emergency_fund_status == "partial":
            months_needed = parameters.emergency_fund_months
            current_months = baseline.lowest_balance / baseline.metadata["avg_monthly_expenses"]
            recommendations.append(
                f"Increase your emergency fund from {current_months:.1f} months to {months_needed} months "
                f"(add approximately ${(months_needed - current_months) * baseline.metadata['avg_monthly_expenses']:,.2f})."
            )
        
        # Cash flow recommendations
        if baseline.cash_flows and baseline.cash_flows[-1].net < 0:
            recommendations.append(
                "Your expenses exceed your income. Consider reducing expenses or increasing income "
                f"to close the monthly gap of ${-baseline.cash_flows[-1].net:,.2f}."
            )
        
        # Runway concerns
        if baseline.runway_months is not None and baseline.runway_months < parameters.projection_length:
            recommendations.append(
                f"Based on current projections, your funds will be depleted in approximately {baseline.runway_months:.1f} months. "
                "Take immediate action to increase income or reduce expenses."
            )
        elif conservative.runway_months is not None and conservative.runway_months < parameters.projection_length:
            recommendations.append(
                f"In a conservative scenario, your funds could be depleted in approximately {conservative.runway_months:.1f} months. "
                "Consider building additional reserves or reducing discretionary expenses."
            )
        
        # Investment recommendations
        if parameters.include_investments and baseline.metadata["avg_monthly_expenses"] > 0:
            # Calculate months of expenses covered by investments
            investment_coverage = baseline.final_balance / baseline.metadata["avg_monthly_expenses"]
            if investment_coverage > 24:
                recommendations.append(
                    f"Your projected balance exceeds 24 months of expenses. Consider investing a portion for long-term growth."
                )
        
        # Tax planning
        if baseline.tax_liability["total"] > 0:
            recommendations.append(
                f"Set aside approximately ${baseline.tax_liability['avg_monthly']:,.2f} monthly for taxes, "
                f"with an estimated annual liability of ${baseline.tax_liability['yearly'].get(datetime.now().year, 0):,.2f}."
            )
        
        # Stress test preparedness
        if stress_test.lowest_balance < 0:
            recommendations.append(
                "Your financial position is vulnerable to economic stress. Consider building additional reserves "
                f"of at least ${-stress_test.lowest_balance:,.2f} to withstand worst-case scenarios."
            )
        
        return recommendations