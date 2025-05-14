"""Project profitability analyzer for freelancers."""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union, Set

import pandas as pd
from pydantic import BaseModel

from personal_finance_tracker.models.common import (
    Client,
    Project,
    TimeEntry,
    Transaction,
    Invoice,
    TransactionType,
)
from personal_finance_tracker.project.models import (
    ProjectMetricType,
    ProfitabilityMetric,
    ProjectProfitability,
    ClientProfitability,
    TrendPoint,
    TrendAnalysis,
)


class ProjectProfiler:
    """
    Project profitability analyzer for tracking project performance.

    This class analyzes project profitability based on time tracking, expenses,
    and revenue data to help freelancers make informed business decisions.
    """

    def __init__(self):
        """Initialize the project profiler."""
        self._profitability_cache = {}

    def analyze_project_profitability(
        self,
        project: Project,
        time_entries: List[TimeEntry],
        transactions: List[Transaction],
        invoices: List[Invoice],
        force_recalculation: bool = False,
    ) -> ProjectProfitability:
        """
        Analyze the profitability of a single project.

        Args:
            project: Project to analyze
            time_entries: Time entries associated with the project
            transactions: Transactions associated with the project
            invoices: Invoices associated with the project
            force_recalculation: Whether to force recalculation

        Returns:
            ProjectProfitability analysis result
        """
        # Performance measurement
        start_time = time.time()

        # Check cache unless forced
        cache_key = f"project_{project.id}"
        if not force_recalculation and cache_key in self._profitability_cache:
            return self._profitability_cache[cache_key]

        # Filter to entries for this project
        project_time_entries = [e for e in time_entries if e.project_id == project.id]

        # Calculate total hours
        total_hours = sum(
            entry.duration_minutes / 60
            for entry in project_time_entries
            if entry.duration_minutes is not None
        )

        # Calculate total revenue from invoices
        project_invoices = [i for i in invoices if i.project_id == project.id]
        paid_invoices = [i for i in project_invoices if i.status == "paid"]
        total_revenue = sum(invoice.amount for invoice in paid_invoices)

        # Calculate total expenses
        project_expenses = [
            t
            for t in transactions
            if (
                t.transaction_type == TransactionType.EXPENSE
                and t.project_id == project.id
            )
        ]
        total_expenses = sum(t.amount for t in project_expenses)

        # Calculate profitability metrics
        total_profit = total_revenue - total_expenses

        # Avoid division by zero
        effective_hourly_rate = total_revenue / max(total_hours, 0.01)
        profit_margin = 100 * total_profit / max(total_revenue, 0.01)
        roi = total_profit / max(total_expenses, 0.01)

        # Determine if project is completed
        is_completed = (
            project.end_date is not None and project.end_date <= datetime.now()
        )

        # Create project profitability result
        result = ProjectProfitability(
            project_id=project.id,
            project_name=project.name,
            client_id=project.client_id,
            start_date=project.start_date,
            end_date=project.end_date,
            total_hours=total_hours,
            total_revenue=total_revenue,
            total_expenses=total_expenses,
            total_profit=total_profit,
            effective_hourly_rate=effective_hourly_rate,
            profit_margin=profit_margin,
            roi=roi,
            is_completed=is_completed,
            calculation_date=datetime.now(),
            metrics=[
                ProfitabilityMetric(
                    project_id=project.id,
                    metric_type=ProjectMetricType.HOURLY_RATE,
                    value=effective_hourly_rate,
                ),
                ProfitabilityMetric(
                    project_id=project.id,
                    metric_type=ProjectMetricType.TOTAL_PROFIT,
                    value=total_profit,
                ),
                ProfitabilityMetric(
                    project_id=project.id,
                    metric_type=ProjectMetricType.PROFIT_MARGIN,
                    value=profit_margin,
                ),
                ProfitabilityMetric(
                    project_id=project.id, metric_type=ProjectMetricType.ROI, value=roi
                ),
            ],
        )

        # Cache the result
        self._profitability_cache[cache_key] = result

        # Verify performance
        elapsed_time = time.time() - start_time

        return result

    def analyze_client_profitability(
        self,
        client: Client,
        projects: List[Project],
        time_entries: List[TimeEntry],
        transactions: List[Transaction],
        invoices: List[Invoice],
        force_recalculation: bool = False,
    ) -> ClientProfitability:
        """
        Analyze the profitability of all projects for a client.

        Args:
            client: Client to analyze
            projects: All projects for the client
            time_entries: All time entries
            transactions: All transactions
            invoices: All invoices
            force_recalculation: Whether to force recalculation

        Returns:
            ClientProfitability analysis result
        """
        # Performance measurement
        start_time = time.time()

        # Check cache unless forced
        cache_key = f"client_{client.id}"
        if not force_recalculation and cache_key in self._profitability_cache:
            return self._profitability_cache[cache_key]

        # Filter to client's projects
        client_projects = [p for p in projects if p.client_id == client.id]

        if not client_projects:
            return ClientProfitability(
                client_id=client.id,
                client_name=client.name,
                number_of_projects=0,
                total_hours=0.0,
                total_revenue=0.0,
                total_expenses=0.0,
                total_profit=0.0,
                average_hourly_rate=0.0,
                average_profit_margin=0.0,
            )

        # Analyze each project
        project_analyses = []
        for project in client_projects:
            analysis = self.analyze_project_profitability(
                project, time_entries, transactions, invoices, force_recalculation
            )
            project_analyses.append(analysis)

        # Calculate client-level metrics
        total_hours = sum(p.total_hours for p in project_analyses)
        total_revenue = sum(p.total_revenue for p in project_analyses)
        total_expenses = sum(p.total_expenses for p in project_analyses)
        total_profit = sum(p.total_profit for p in project_analyses)

        # Calculate averages
        avg_hourly_rate = total_revenue / max(total_hours, 0.01)
        avg_profit_margin = 100 * total_profit / max(total_revenue, 0.01)

        # Calculate average invoice payment time
        client_invoices = [
            i for i in invoices if i.client_id == client.id and i.status == "paid"
        ]
        payment_days = []

        for invoice in client_invoices:
            if invoice.payment_date and invoice.issue_date:
                days = (invoice.payment_date - invoice.issue_date).days
                payment_days.append(days)

        avg_payment_days = None
        if payment_days:
            avg_payment_days = sum(payment_days) / len(payment_days)

        # Create client profitability result
        result = ClientProfitability(
            client_id=client.id,
            client_name=client.name,
            number_of_projects=len(client_projects),
            total_hours=total_hours,
            total_revenue=total_revenue,
            total_expenses=total_expenses,
            total_profit=total_profit,
            average_hourly_rate=avg_hourly_rate,
            average_profit_margin=avg_profit_margin,
            average_invoice_payment_days=avg_payment_days,
            projects=project_analyses,
        )

        # Cache the result
        self._profitability_cache[cache_key] = result

        # Verify performance
        elapsed_time = time.time() - start_time

        return result

    def analyze_all_projects(
        self,
        projects: List[Project],
        time_entries: List[TimeEntry],
        transactions: List[Transaction],
        invoices: List[Invoice],
        force_recalculation: bool = False,
    ) -> List[ProjectProfitability]:
        """
        Analyze profitability for all projects.

        Args:
            projects: All projects to analyze
            time_entries: All time entries
            transactions: All transactions
            invoices: All invoices
            force_recalculation: Whether to force recalculation

        Returns:
            List of ProjectProfitability analysis results
        """
        # Performance measurement
        start_time = time.time()

        # Analyze each project
        results = []
        for project in projects:
            analysis = self.analyze_project_profitability(
                project, time_entries, transactions, invoices, force_recalculation
            )
            results.append(analysis)

        # Sort by profitability (highest first)
        results.sort(key=lambda x: x.total_profit, reverse=True)

        # Verify performance - should handle 100+ projects efficiently
        elapsed_time = time.time() - start_time
        if len(projects) > 100 and elapsed_time > 3.0:
            print(
                f"Warning: Project analysis took {elapsed_time:.2f} seconds for {len(projects)} projects"
            )

        return results

    def generate_trend_analysis(
        self,
        metric_type: ProjectMetricType,
        start_date: datetime,
        end_date: datetime,
        period: str = "monthly",
        project_id: Optional[str] = None,
        client_id: Optional[str] = None,
        projects: Optional[List[Project]] = None,
        time_entries: Optional[List[TimeEntry]] = None,
        transactions: Optional[List[Transaction]] = None,
        invoices: Optional[List[Invoice]] = None,
    ) -> TrendAnalysis:
        """
        Generate trend analysis for project metrics over time.

        Args:
            metric_type: Type of metric to analyze
            start_date: Start date for analysis
            end_date: End date for analysis
            period: Period for grouping ("weekly", "monthly", "quarterly", "yearly")
            project_id: Optional project ID to filter
            client_id: Optional client ID to filter
            projects: Optional list of projects
            time_entries: Optional list of time entries
            transactions: Optional list of transactions
            invoices: Optional list of invoices

        Returns:
            TrendAnalysis result
        """
        if not projects or not time_entries or not transactions or not invoices:
            return TrendAnalysis(
                metric_type=metric_type,
                project_id=project_id,
                client_id=client_id,
                period=period,
                start_date=start_date,
                end_date=end_date,
                data_points=[],
            )

        # Filter projects
        filtered_projects = projects
        if project_id:
            filtered_projects = [p for p in projects if p.id == project_id]
        elif client_id:
            filtered_projects = [p for p in projects if p.client_id == client_id]

        if not filtered_projects:
            return TrendAnalysis(
                metric_type=metric_type,
                project_id=project_id,
                client_id=client_id,
                period=period,
                start_date=start_date,
                end_date=end_date,
                data_points=[],
            )

        # Get project IDs for filtering
        project_ids = {p.id for p in filtered_projects}

        # Prepare time periods based on specified period
        if period == "weekly":
            freq = "W-MON"
            period_name = "Weekly"
        elif period == "monthly":
            freq = "MS"
            period_name = "Monthly"
        elif period == "quarterly":
            freq = "QS"
            period_name = "Quarterly"
        elif period == "yearly":
            freq = "AS"
            period_name = "Yearly"
        else:
            freq = "MS"  # Default to monthly
            period_name = "Monthly"

        # Generate time periods
        periods = pd.date_range(start=start_date, end=end_date, freq=freq)

        # Calculate metric for each period
        data_points = []

        for i in range(len(periods) - 1):
            period_start = periods[i]
            period_end = periods[i + 1] - timedelta(days=1)

            # Filter data for this period
            period_time_entries = [
                e
                for e in time_entries
                if (
                    e.project_id in project_ids
                    and e.start_time >= period_start
                    and e.start_time <= period_end
                )
            ]

            period_transactions = [
                t
                for t in transactions
                if (
                    t.project_id in project_ids
                    and t.date >= period_start
                    and t.date <= period_end
                )
            ]

            period_invoices = [
                i
                for i in invoices
                if (
                    i.project_id in project_ids
                    and i.issue_date >= period_start
                    and i.issue_date <= period_end
                    and i.status == "paid"
                )
            ]

            # Calculate metrics for this period
            total_hours = sum(
                entry.duration_minutes / 60
                for entry in period_time_entries
                if entry.duration_minutes is not None
            )

            total_revenue = sum(invoice.amount for invoice in period_invoices)

            total_expenses = sum(
                t.amount
                for t in period_transactions
                if t.transaction_type == TransactionType.EXPENSE
            )

            total_profit = total_revenue - total_expenses

            # Determine metric value based on type
            metric_value = 0.0

            if metric_type == ProjectMetricType.HOURLY_RATE:
                metric_value = total_revenue / max(total_hours, 0.01)
            elif metric_type == ProjectMetricType.TOTAL_PROFIT:
                metric_value = total_profit
            elif metric_type == ProjectMetricType.PROFIT_MARGIN:
                metric_value = 100 * total_profit / max(total_revenue, 0.01)
            elif metric_type == ProjectMetricType.ROI:
                metric_value = total_profit / max(total_expenses, 0.01)

            # Add data point
            data_point = TrendPoint(
                date=period_start.to_pydatetime(), value=metric_value
            )
            data_points.append(data_point)

        # Create trend analysis
        trend = TrendAnalysis(
            metric_type=metric_type,
            project_id=project_id,
            client_id=client_id,
            period=period,
            start_date=start_date,
            end_date=end_date,
            data_points=data_points,
            description=f"{period_name} trend of {metric_type.value} from {start_date.date()} to {end_date.date()}",
        )

        return trend

    def record_time_entry(self, time_entry: TimeEntry) -> TimeEntry:
        """
        Record a new time entry for a project.

        Args:
            time_entry: Time entry to record

        Returns:
            The recorded time entry
        """
        # In a real implementation, this would store the time entry in a database
        # For this example, we just return the time entry and clear the cache
        self._profitability_cache = {}
        return time_entry

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
        self._profitability_cache = {}

        return transaction
