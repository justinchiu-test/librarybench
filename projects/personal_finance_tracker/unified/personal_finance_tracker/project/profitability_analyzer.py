"""Project profitability analyzer for freelancers."""

from datetime import datetime
from typing import List, Optional, Dict, Any, Set, Union

# Import directly from common library
from common.core.models.project import Project, Client, TimeEntry, Invoice
from common.core.models.transaction import BusinessTransaction as Transaction
from common.core.models.transaction import TransactionType
from common.core.models.project_metrics import (
    ProjectMetricType,
    ProjectProfitability,
    ClientProfitability,
    TrendAnalysis,
    TrendPoint,
)
from common.core.analysis.project_analyzer import ProjectAnalyzer
from common.core.utils.performance import Timer


class ProjectProfiler(ProjectAnalyzer[Transaction]):
    """
    Project profitability analyzer for tracking project performance for freelancers.
    
    Extends the common ProjectAnalyzer with freelancer-specific functionality.
    """
    
    def __init__(self):
        """Initialize the project profiler."""
        super().__init__()
        # The Timer is already initialized in the parent class
        
    def _filter_project_expenses(self, transactions: List[Transaction], project_id: str) -> List[Transaction]:
        """
        Filter transactions to find project expenses.
        
        Overrides the parent method to implement freelancer-specific filtering logic.
        
        Args:
            transactions: List of transactions to filter
            project_id: Project ID to filter by
            
        Returns:
            List of expense transactions for the project
        """
        project_expenses = [
            t
            for t in transactions
            if (
                t.transaction_type == TransactionType.EXPENSE
                and t.project_id == str(project_id)
            )
        ]
        return project_expenses
    
    def _filter_period_transactions(
        self, 
        transactions: List[Transaction], 
        project_ids: Set[str], 
        period_start: datetime, 
        period_end: datetime
    ) -> List[Transaction]:
        """
        Filter transactions for a specific period and projects.
        
        Overrides the parent method to implement freelancer-specific filtering logic.
        
        Args:
            transactions: List of transactions to filter
            project_ids: Set of project IDs to include
            period_start: Start date for the period
            period_end: End date for the period
            
        Returns:
            List of transactions for the period and projects
        """
        period_transactions = [
            t
            for t in transactions
            if (
                t.project_id in project_ids
                and t.date >= period_start
                and t.date <= period_end
            )
        ]
        return period_transactions
    
    def allocate_expense(
        self, transaction: Transaction, project_id: str, amount: Optional[float] = None
    ) -> Transaction:
        """
        Allocate an expense to a project.

        Args:
            transaction: Transaction to allocate
            project_id: Project ID to allocate to
            amount: Optional amount to allocate (defaults to full amount)

        Returns:
            The updated transaction
        """
        # Start timer
        self.timer.start()
        
        # Validate transaction is an expense
        if transaction.transaction_type != TransactionType.EXPENSE:
            raise ValueError("Transaction must be an expense")

        # Update transaction project
        transaction.project_id = project_id

        # Handle partial allocation if amount is specified
        if amount is not None and amount != transaction.amount:
            # In a real implementation, this might create a split transaction
            # or track the allocation percentage
            transaction.allocation = {
                "project_id": project_id,
                "amount": amount,
                "percentage": (amount / transaction.amount) * 100,
            }

        # In a real implementation, this would update the transaction in a database
        # Clear cache to ensure recalculation
        self._profitability_cache.clear()
        
        # Stop timer
        self.timer.stop()

        return transaction
    
    def analyze_project_performance(
        self, 
        project: Project, 
        transactions: List[Transaction], 
        time_entries: List[TimeEntry],
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Analyze the performance of a specific project with extended metrics.
        
        Args:
            project: The project to analyze
            transactions: List of all transactions
            time_entries: List of time entries for the project
            period_start: Optional start date for analysis period
            period_end: Optional end date for analysis period
            
        Returns:
            Dictionary with extended project performance metrics
        """
        # Start timer
        self.timer.start()
        
        # Calculate core profitability using the parent method
        profitability = self.calculate_project_profitability(
            project, transactions, time_entries, period_start, period_end
        )
        
        # Extract key metrics for the result
        result = {
            "project_id": str(project.id),
            "project_name": project.name,
            "revenue": profitability.revenue,
            "expenses": profitability.expenses,
            "profit": profitability.profit,
            "margin": profitability.margin,
            "period_start": period_start or min(e.date for e in time_entries) if time_entries else None,
            "period_end": period_end or max(e.date for e in time_entries) if time_entries else None,
        }
        
        # Add freelancer-specific metrics
        
        # Calculate hours worked
        total_hours = sum(entry.hours for entry in time_entries)
        result["total_hours"] = total_hours
        
        # Calculate effective hourly rate
        if total_hours > 0:
            result["effective_hourly_rate"] = profitability.revenue / total_hours
            result["profit_per_hour"] = profitability.profit / total_hours
        else:
            result["effective_hourly_rate"] = 0
            result["profit_per_hour"] = 0
        
        # Calculate billable ratio if target hours available
        if hasattr(project, 'target_hours') and project.target_hours:
            result["billable_ratio"] = total_hours / project.target_hours
            result["hours_variance"] = total_hours - project.target_hours
        
        # Calculate tax efficiency
        tax_deductible_expenses = sum(
            t.amount for t in self._filter_project_expenses(transactions, str(project.id))
            if hasattr(t, 'tax_deductible') and t.tax_deductible
        )
        result["tax_deductible_expenses"] = tax_deductible_expenses
        
        # Stop timer
        elapsed_ms = self.timer.stop()
        result["analysis_time_ms"] = elapsed_ms
        
        return result