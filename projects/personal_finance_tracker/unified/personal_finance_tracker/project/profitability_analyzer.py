"""Project profitability analyzer for freelancers."""

from datetime import datetime
from typing import List, Optional

# Import directly from common library
from common.core.models.project import Project, Client, TimeEntry, Invoice
from common.core.models.transaction import BusinessTransaction as Transaction
from common.core.models.transaction import TransactionType
from common.core.models.project_metrics import (
    ProjectMetricType,
    ProjectProfitability,
    ClientProfitability,
    TrendAnalysis,
)
from common.core.analysis.project_analyzer import ProjectAnalyzer


class ProjectProfiler(ProjectAnalyzer[Transaction]):
    """
    Project profitability analyzer for tracking project performance for freelancers.
    
    Extends the common ProjectAnalyzer with freelancer-specific functionality.
    """
    
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
        project_ids: set, 
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
        # Validate transaction is an expense
        if transaction.transaction_type != TransactionType.EXPENSE:
            raise ValueError("Transaction must be an expense")

        # Update transaction project
        transaction.project_id = project_id

        # In a real implementation, this would update the transaction in a database
        # Clear cache to ensure recalculation
        self._profitability_cache.clear()

        return transaction