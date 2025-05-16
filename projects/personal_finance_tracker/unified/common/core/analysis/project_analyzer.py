"""Project profitability analyzer shared across implementations."""

from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Union, Any, Generic, TypeVar
from uuid import UUID

import pandas as pd

from common.core.analysis.analyzer import BaseAnalyzer
from common.core.models.project import Project, Client, TimeEntry, Invoice
from common.core.models.transaction import BaseTransaction
from common.core.models.project_metrics import (
    ProjectMetricType,
    ProfitabilityMetric,
    ProjectProfitability,
    ClientProfitability,
    TrendPoint,
    TrendAnalysis,
)
from common.core.utils.performance import Timer
from common.core.utils.cache_utils import Cache
from common.core.analysis.time_series import TimeSeriesData, TimeSeriesAnalyzer

# Type variable for transactions
T = TypeVar('T', bound=BaseTransaction)


class ProjectAnalyzer(BaseAnalyzer, Generic[T]):
    """
    Project profitability analyzer for tracking project performance.
    
    This class analyzes project profitability based on time tracking, expenses,
    and revenue data to help make informed business decisions.
    """
    
    def __init__(self):
        """Initialize the project analyzer."""
        super().__init__()
        self._profitability_cache = Cache(max_size=100, expiration_seconds=3600)
        
    def analyze(self, subject: Any, parameters: Optional[Any] = None) -> Any:
        """
        Analyze a subject based on parameters.
        
        This is a basic implementation of the abstract method from BaseAnalyzer.
        Derived classes should override this with specific implementation.
        
        Args:
            subject: The subject to analyze
            parameters: Optional parameters to configure the analysis
            
        Returns:
            Analysis result
        """
        if isinstance(subject, Project):
            # If no specific parameters and subject is a Project,
            # try to analyze project profitability with empty data
            return self.analyze_project_profitability(
                project=subject,
                time_entries=[],
                transactions=[],
                invoices=[],
                force_recalculation=True
            )
        
        # Default implementation just returns a simple analysis result
        return {
            "subject_id": str(getattr(subject, "id", "unknown")),
            "subject_type": type(subject).__name__,
            "analysis_type": "default",
            "result": "No specific analysis available"
        }
    
    def analyze_project_profitability(
        self,
        project: Project,
        time_entries: List[TimeEntry],
        transactions: List[T],
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
        with Timer("project_profitability_analysis"):
            # Check cache unless forced
            cache_key = f"project_{project.id}"
            if not force_recalculation:
                cached_result = self._profitability_cache.get(cache_key)
                if cached_result:
                    return cached_result
            
            # Filter to entries for this project
            project_time_entries = [e for e in time_entries if e.project_id == str(project.id)]
            
            # Calculate total hours
            total_hours = sum(
                entry.duration_minutes / 60
                for entry in project_time_entries
                if entry.duration_minutes is not None
            )
            
            # Calculate total revenue from invoices
            project_invoices = [i for i in invoices if i.project_id == str(project.id)]
            paid_invoices = [i for i in project_invoices if i.status == "paid"]
            total_revenue = sum(invoice.amount for invoice in paid_invoices)
            
            # Calculate total expenses - implementation-specific logic
            project_expenses = self._filter_project_expenses(transactions, project.id)
            total_expenses = sum(t.amount for t in project_expenses)
            
            # Calculate profitability metrics
            total_profit = total_revenue - total_expenses
            
            # Avoid division by zero
            effective_hourly_rate = total_revenue / max(total_hours, 0.01)
            profit_margin = 100 * total_profit / max(total_revenue, 0.01)
            roi = total_profit / max(total_expenses, 0.01)
            
            # Determine if project is completed
            is_completed = (
                project.end_date is not None and 
                (isinstance(project.end_date, datetime) and project.end_date <= datetime.now() or
                 not isinstance(project.end_date, datetime) and project.end_date <= datetime.now().date())
            )
            
            # Create project profitability result
            result = ProjectProfitability(
                project_id=str(project.id),
                project_name=project.name,
                client_id=str(project.client_id) if project.client_id else "",
                start_date=project.start_date if isinstance(project.start_date, datetime) else 
                           datetime.combine(project.start_date, datetime.min.time()),
                end_date=project.end_date if project.end_date is None or isinstance(project.end_date, datetime) else 
                         datetime.combine(project.end_date, datetime.min.time()),
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
                        project_id=str(project.id),
                        metric_type=ProjectMetricType.HOURLY_RATE,
                        value=effective_hourly_rate,
                    ),
                    ProfitabilityMetric(
                        project_id=str(project.id),
                        metric_type=ProjectMetricType.TOTAL_PROFIT,
                        value=total_profit,
                    ),
                    ProfitabilityMetric(
                        project_id=str(project.id),
                        metric_type=ProjectMetricType.PROFIT_MARGIN,
                        value=profit_margin,
                    ),
                    ProfitabilityMetric(
                        project_id=str(project.id), 
                        metric_type=ProjectMetricType.ROI, 
                        value=roi
                    ),
                ],
            )
            
            # Cache the result
            self._profitability_cache.set(cache_key, result)
        
        return result
    
    def analyze_client_profitability(
        self,
        client: Client,
        projects: List[Project],
        time_entries: List[TimeEntry],
        transactions: List[T],
        invoices: List[Invoice],
        force_recalculation: bool = False,
    ) -> ClientProfitability:
        """
        Analyze the profitability of all projects for a client.
        
        Args:
            client: Client to analyze
            projects: All projects
            time_entries: All time entries
            transactions: All transactions
            invoices: All invoices
            force_recalculation: Whether to force recalculation
            
        Returns:
            ClientProfitability analysis result
        """
        # Performance measurement
        with Timer("client_profitability_analysis"):
            # Check cache unless forced
            cache_key = f"client_{client.id}"
            if not force_recalculation:
                cached_result = self._profitability_cache.get(cache_key)
                if cached_result:
                    return cached_result
            
            # Filter to client's projects
            client_projects = [p for p in projects if p.client_id == str(client.id)]
            
            if not client_projects:
                return ClientProfitability(
                    client_id=str(client.id),
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
                i for i in invoices if i.client_id == str(client.id) and i.status == "paid"
            ]
            payment_days = []
            
            for invoice in client_invoices:
                if invoice.payment_date and invoice.issue_date:
                    # Convert to datetime if needed
                    issue_date = invoice.issue_date
                    if not isinstance(issue_date, datetime):
                        issue_date = datetime.combine(issue_date, datetime.min.time())
                    
                    payment_date = invoice.payment_date
                    if not isinstance(payment_date, datetime):
                        payment_date = datetime.combine(payment_date, datetime.min.time())
                    
                    days = (payment_date - issue_date).days
                    payment_days.append(days)
            
            avg_payment_days = None
            if payment_days:
                avg_payment_days = sum(payment_days) / len(payment_days)
            
            # Create client profitability result
            result = ClientProfitability(
                client_id=str(client.id),
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
            self._profitability_cache.set(cache_key, result)
        
        return result
    
    def analyze_all_projects(
        self,
        projects: List[Project],
        time_entries: List[TimeEntry],
        transactions: List[T],
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
        with Timer("all_projects_analysis"):
            # Analyze each project
            results = []
            for project in projects:
                analysis = self.analyze_project_profitability(
                    project, time_entries, transactions, invoices, force_recalculation
                )
                results.append(analysis)
            
            # Sort by profitability (highest first)
            results.sort(key=lambda x: x.total_profit, reverse=True)
        
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
        transactions: Optional[List[T]] = None,
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
        with Timer("project_trend_analysis"):
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
                filtered_projects = [p for p in projects if str(p.id) == project_id]
            elif client_id:
                filtered_projects = [p for p in projects if str(p.client_id) == client_id]
            
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
            project_ids = {str(p.id) for p in filtered_projects}
            
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
            period_dates = pd.date_range(start=start_date, end=end_date, freq=freq)
            periods = [d.to_pydatetime() for d in period_dates]
            
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
                
                period_transactions = self._filter_period_transactions(
                    transactions, project_ids, period_start, period_end
                )
                
                period_invoices = [
                    i
                    for i in invoices
                    if (
                        i.project_id in project_ids
                        and self._is_date_in_range(i.issue_date, period_start, period_end)
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
                
                total_expenses = sum(t.amount for t in period_transactions)
                
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
                    date=period_start,
                    value=metric_value
                )
                data_points.append(data_point)
            
            # Use TimeSeriesData and TimeSeriesAnalyzer for advanced trend analysis
            dates = [point.date for point in data_points]
            values = [point.value for point in data_points]
            
            # Only proceed with trend analysis if we have data points
            trend_direction = "none"
            trend_strength = 0.0
            
            if dates and values:
                # Create TimeSeriesData object
                time_series_data = TimeSeriesData(dates=dates, values=values)
                
                # Apply trend detection
                trend_info = TimeSeriesAnalyzer.detect_trend(time_series_data)
                trend_direction = trend_info["trend_direction"]
                trend_strength = trend_info["trend_strength"]
            
            # Create trend analysis
            trend = TrendAnalysis(
                metric_type=metric_type,
                project_id=project_id,
                client_id=client_id,
                period=period,
                start_date=start_date,
                end_date=end_date,
                data_points=data_points,
                description=(
                    f"{period_name} trend of {metric_type.value} from {start_date.date()} "
                    f"to {end_date.date()}. Trend direction: {trend_direction}, "
                    f"strength: {trend_strength:.2f}"
                ),
            )
        
        return trend
    
    def _filter_project_expenses(self, transactions: List[T], project_id: Union[str, UUID]) -> List[T]:
        """
        Filter transactions to find project expenses.
        This method should be overridden by derived classes to implement
        project-specific filtering logic.
        
        Args:
            transactions: List of transactions to filter
            project_id: Project ID to filter by
            
        Returns:
            List of expense transactions for the project
        """
        # Default implementation - derived classes should override
        # to provide specific transaction filtering logic
        project_expenses = [
            t for t in transactions
            if hasattr(t, "project_id") and str(t.project_id) == str(project_id)
        ]
        return project_expenses
    
    def _filter_period_transactions(
        self, 
        transactions: List[T], 
        project_ids: set, 
        period_start: datetime, 
        period_end: datetime
    ) -> List[T]:
        """
        Filter transactions for a specific period and projects.
        This method should be overridden by derived classes to implement
        specific filtering logic.
        
        Args:
            transactions: List of transactions to filter
            project_ids: Set of project IDs to include
            period_start: Start date for the period
            period_end: End date for the period
            
        Returns:
            List of transactions for the period and projects
        """
        # Default implementation - derived classes should override
        # to provide specific transaction filtering logic
        period_transactions = [
            t for t in transactions
            if (
                hasattr(t, "project_id") and str(t.project_id) in project_ids
                and hasattr(t, "date") and self._is_date_in_range(t.date, period_start, period_end)
            )
        ]
        return period_transactions
    
    def _is_date_in_range(
        self, 
        date_value: Union[datetime, date], 
        start_date: datetime, 
        end_date: datetime
    ) -> bool:
        """
        Check if a date is within a range.
        
        Args:
            date_value: Date to check
            start_date: Start of range
            end_date: End of range
            
        Returns:
            True if date is in range, False otherwise
        """
        # Convert to datetime if needed
        if not isinstance(date_value, datetime):
            date_value = datetime.combine(date_value, datetime.min.time())
        
        return start_date <= date_value <= end_date