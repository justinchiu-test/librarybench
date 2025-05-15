"""Income management system for freelancers."""

import calendar
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
import time

import numpy as np
import pandas as pd
from pydantic import BaseModel

from common.core.analysis.time_series import (
    TimeSeriesData,
    TimeSeriesAnalyzer,
    TimeSeriesGranularity,
)
from common.core.models.project import Invoice
from common.core.utils.date_utils import (
    get_first_day_of_month,
    get_last_day_of_month,
    month_range,
)
from common.core.utils.performance import Timer

from personal_finance_tracker.models.common import Transaction, TransactionType
from personal_finance_tracker.income.models import (
    SmoothingConfig,
    SmoothingMethod,
    SmoothedIncome,
    RevenueForecast,
)


class IncomeManager:
    """Income management system for normalizing variable freelance income."""

    def __init__(self, smoothing_config: Optional[SmoothingConfig] = None):
        """Initialize with optional configuration."""
        self.config = smoothing_config or SmoothingConfig()
        self._income_cache = {}
        self._ts_analyzer = TimeSeriesAnalyzer()

    def record_income(
        self, transactions: List[Transaction], force_recalculation: bool = False
    ) -> None:
        """
        Record income transactions and update income calculations.

        Args:
            transactions: List of income transactions to record
            force_recalculation: Whether to force recalculation of smoothed income
        """
        # Clear cache if forced
        if force_recalculation:
            self._income_cache = {}

        # Only process income transactions
        income_transactions = [
            t for t in transactions if t.transaction_type == TransactionType.INCOME
        ]

        if not income_transactions:
            return

    def calculate_monthly_income(
        self, transactions: List[Transaction], start_date: datetime, end_date: datetime
    ) -> Dict[str, float]:
        """
        Calculate monthly income from transactions within date range.

        Args:
            transactions: List of income transactions
            start_date: Start date for calculation
            end_date: End date for calculation

        Returns:
            Dictionary mapping month (YYYY-MM format) to income amount
        """
        # Filter transactions to income within date range
        income_transactions = [
            t
            for t in transactions
            if (
                t.transaction_type == TransactionType.INCOME
                and start_date <= t.date <= end_date
            )
        ]

        # Group by month and sum
        monthly_income = {}
        for transaction in income_transactions:
            month_key = transaction.date.strftime("%Y-%m")
            if month_key not in monthly_income:
                monthly_income[month_key] = 0
            monthly_income[month_key] += transaction.amount

        return monthly_income

    def smooth_income(
        self,
        transactions: List[Transaction],
        method: Optional[SmoothingMethod] = None,
        config: Optional[SmoothingConfig] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[SmoothedIncome]:
        """
        Apply income smoothing algorithm to normalize variable income.

        Args:
            transactions: List of income transactions
            method: Smoothing method to use (defaults to config method)
            config: Smoothing configuration (defaults to instance config)
            start_date: Start date for calculation (defaults to earliest transaction)
            end_date: End date for calculation (defaults to latest transaction)

        Returns:
            List of SmoothedIncome objects with monthly smoothed income values
        """
        # Use Timer for performance measurement
        with Timer("income_smoothing") as timer:
            # Use provided or default config
            smoothing_config = config or self.config
            smoothing_method = method or smoothing_config.method

            # Filter to income transactions
            income_transactions = [
                t for t in transactions if t.transaction_type == TransactionType.INCOME
            ]

            if not income_transactions:
                return []

            # Determine date range if not provided
            if not start_date:
                start_date = min(t.date for t in income_transactions)
            if not end_date:
                end_date = max(t.date for t in income_transactions)

            # Ensure start_date is beginning of month and end_date is end of month
            start_date = get_first_day_of_month(start_date)
            end_date = get_last_day_of_month(end_date)

            # Create monthly income dictionary
            monthly_income = self.calculate_monthly_income(
                income_transactions, start_date, end_date
            )

            # Create dates and values for TimeSeriesData
            dates = []
            values = []

            # Build time series data
            for month_date in month_range(start_date, end_date):
                month_key = month_date.strftime("%Y-%m")
                dates.append(month_date)
                values.append(monthly_income.get(month_key, 0))

            # Create time series data object
            income_ts = TimeSeriesData(
                dates=dates,
                values=values,
                metadata={"method": smoothing_method}
            )

            # Apply appropriate smoothing algorithm using TimeSeriesAnalyzer
            if smoothing_method == SmoothingMethod.MOVING_AVERAGE:
                smoothed_ts = self._ts_analyzer.moving_average(
                    income_ts, window_size=smoothing_config.window_size
                )
            elif smoothing_method == SmoothingMethod.EXPONENTIAL_SMOOTHING:
                smoothed_ts = self._ts_analyzer.exponential_smoothing(
                    income_ts, alpha=smoothing_config.alpha
                )
            elif smoothing_method == SmoothingMethod.SEASONAL_ADJUSTMENT:
                smoothed_ts = self._ts_analyzer.seasonal_adjustment(
                    income_ts, period=smoothing_config.seasonal_periods
                )
            elif smoothing_method == SmoothingMethod.PERCENTILE_BASED:
                # Implement percentile-based smoothing
                smoothed_ts = self._percentile_based_smoothing(
                    income_ts, smoothing_config.percentile
                )
            elif smoothing_method == SmoothingMethod.ROLLING_MEDIAN:
                # Implement rolling median smoothing
                smoothed_ts = self._rolling_median_smoothing(
                    income_ts, smoothing_config.window_size
                )
            else:
                raise ValueError(f"Unsupported smoothing method: {smoothing_method}")

            # If target income is provided, use it instead
            if smoothing_config.target_monthly_income is not None:
                smoothed_values = [
                    smoothing_config.target_monthly_income
                    for _ in range(len(income_ts.values))
                ]
                smoothed_ts = TimeSeriesData(
                    dates=income_ts.dates,
                    values=smoothed_values,
                    metadata=income_ts.metadata
                )

            # Create smoothed income results
            results = []
            for i, date in enumerate(smoothed_ts.dates):
                if isinstance(date, datetime):
                    month_date = date
                    month_end = get_last_day_of_month(date)
                else:
                    # Convert date to datetime
                    month_date = datetime.combine(date, datetime.min.time())
                    month_end = datetime.combine(
                        get_last_day_of_month(date), datetime.min.time()
                    )

                actual = income_ts.values[i]
                smoothed = smoothed_ts.values[i]

                # Calculate surplus/deficit
                deficit = max(0, smoothed - actual)
                surplus = max(0, actual - smoothed)

                result = SmoothedIncome(
                    period_start=month_date,
                    period_end=month_end,
                    actual_income=float(actual),
                    smoothed_income=float(smoothed),
                    method=smoothing_method,
                    configuration=smoothing_config,
                    income_deficit=float(deficit),
                    income_surplus=float(surplus),
                )
                results.append(result)

        # Verify performance requirement
        if timer.elapsed_time > 3.0:
            print(
                f"Warning: Income smoothing took {timer.elapsed_time:.2f} seconds, which exceeds the 3 second requirement"
            )

        return results

    def _percentile_based_smoothing(
        self, income_ts: TimeSeriesData, percentile: float
    ) -> TimeSeriesData:
        """
        Apply percentile-based smoothing.

        This method sets a baseline income at a specified percentile of historical income,
        providing a conservative estimate that can be sustained in lean months.
        """
        if not income_ts.values or len(income_ts.values) < 3:
            # Not enough data for percentile calculation
            return income_ts

        # Calculate percentile of all non-zero income values
        non_zero_values = [v for v in income_ts.values if v > 0]
        if not non_zero_values:
            return income_ts

        baseline = np.percentile(non_zero_values, percentile)

        # Create series with baseline value
        smoothed_values = [baseline] * len(income_ts.values)

        # Return new time series data
        return TimeSeriesData(
            dates=income_ts.dates,
            values=smoothed_values,
            metadata={
                **income_ts.metadata,
                "smoothing_method": "percentile_based",
                "percentile": percentile,
            },
        )

    def _rolling_median_smoothing(
        self, income_ts: TimeSeriesData, window_size: int
    ) -> TimeSeriesData:
        """
        Apply rolling median smoothing.

        This method is more robust to outliers than moving average.
        """
        if not income_ts.values:
            return income_ts

        # Convert to pandas series for rolling median
        values_series = pd.Series(income_ts.values)
        
        # Calculate rolling median
        smoothed_series = values_series.rolling(
            window=window_size, min_periods=1, center=False
        ).median()
        
        # Handle NaN values
        for i in range(len(smoothed_series)):
            if pd.isna(smoothed_series.iloc[i]):
                # Use median of available data
                smoothed_series.iloc[i] = values_series.iloc[:i+1].median()
        
        # Convert back to list
        smoothed_values = smoothed_series.tolist()
        
        # Return new time series data
        return TimeSeriesData(
            dates=income_ts.dates,
            values=smoothed_values,
            metadata={
                **income_ts.metadata,
                "smoothing_method": "rolling_median",
                "window_size": window_size,
            },
        )

    def forecast_revenue(
        self,
        transactions: List[Transaction],
        invoices: List[Invoice],
        forecast_months: int = 6,
        confidence_interval: Optional[float] = None,
    ) -> List[RevenueForecast]:
        """
        Forecast future revenue based on historical patterns and pending invoices.

        Args:
            transactions: Historical income transactions
            invoices: Pending invoices (issued but not paid)
            forecast_months: Number of months to forecast
            confidence_interval: Confidence interval for prediction (0-1)

        Returns:
            List of monthly revenue forecasts
        """
        # Use Timer for performance measurement
        with Timer("revenue_forecast"):
            # Use configured or provided confidence interval
            ci = confidence_interval or self.config.confidence_interval

            # Filter to income transactions
            income_transactions = [
                t for t in transactions if t.transaction_type == TransactionType.INCOME
            ]

            if not income_transactions:
                # No historical data, can't make forecast
                return []

            # Get latest transaction date and create forecast start date
            latest_date = max(t.date for t in income_transactions)
            forecast_start = get_first_day_of_month(latest_date)
            # Move to next month
            if isinstance(forecast_start, datetime):
                next_month = forecast_start.month + 1
                next_year = forecast_start.year + (next_month > 12)
                if next_month > 12:
                    next_month -= 12
                forecast_start = forecast_start.replace(year=next_year, month=next_month)
            else:
                # Handle date objects
                next_month = forecast_start.month + 1
                next_year = forecast_start.year + (next_month > 12)
                if next_month > 12:
                    next_month -= 12
                forecast_start = forecast_start.replace(year=next_year, month=next_month)

            # Calculate monthly historical income
            end_date = latest_date
            start_date = end_date - timedelta(days=365 * 2)  # 2 years of history
            
            # Create time series data for historical income
            monthly_income = self.calculate_monthly_income(
                income_transactions, start_date, end_date
            )
            
            # Build dates and values arrays
            dates = []
            values = []
            for month_date in month_range(start_date, end_date):
                month_key = month_date.strftime("%Y-%m")
                dates.append(month_date)
                values.append(monthly_income.get(month_key, 0))
            
            # Create TimeSeriesData
            historical_ts = TimeSeriesData(dates=dates, values=values)

            # Calculate basic statistics for forecast
            mean_income = np.mean(historical_ts.values) if historical_ts.values else 0
            std_income = np.std(historical_ts.values) if len(historical_ts.values) > 1 else mean_income * 0.2

            # Calculate bounds based on confidence interval
            from scipy import stats
            z_score = stats.norm.ppf((1 + ci) / 2)

            # Process pending invoices
            pending_by_month = {}
            for invoice in invoices:
                if invoice.status in ["draft", "sent", "overdue"]:
                    # For unpaid invoices, use due date for estimation
                    month_key = invoice.due_date.strftime("%Y-%m")
                    if month_key not in pending_by_month:
                        pending_by_month[month_key] = 0
                    pending_by_month[month_key] += invoice.amount

            # Create forecasts
            forecasts = []
            current_date = forecast_start
            for i in range(forecast_months):
                # Base forecast on historical average
                expected_income = mean_income

                # Add pending invoice amounts if available
                month_key = current_date.strftime("%Y-%m")
                if month_key in pending_by_month:
                    expected_income += pending_by_month[month_key]

                # Calculate bounds
                lower_bound = max(0, expected_income - z_score * std_income)
                upper_bound = expected_income + z_score * std_income

                # Create forecast entry
                forecast = RevenueForecast(
                    month=current_date,
                    expected_income=float(expected_income),
                    lower_bound=float(lower_bound),
                    upper_bound=float(upper_bound),
                    confidence_interval=ci,
                    sources={
                        "historical": float(mean_income),
                        "pending": pending_by_month.get(month_key, 0.0),
                    },
                )
                forecasts.append(forecast)
                
                # Move to next month
                if isinstance(current_date, datetime):
                    next_month = current_date.month + 1
                    next_year = current_date.year + (next_month > 12)
                    if next_month > 12:
                        next_month -= 12
                    current_date = current_date.replace(year=next_year, month=next_month)
                else:
                    # Handle date objects
                    next_month = current_date.month + 1
                    next_year = current_date.year + (next_month > 12)
                    if next_month > 12:
                        next_month -= 12
                    current_date = current_date.replace(year=next_year, month=next_month)

        return forecasts

    def track_invoice(self, invoice: Invoice, update_existing: bool = True) -> Invoice:
        """
        Track a new invoice or update an existing one.

        Args:
            invoice: The invoice to track
            update_existing: Whether to update an existing invoice with the same ID

        Returns:
            The tracked invoice
        """
        # In a real implementation, this would store the invoice in a database
        # For this example, we just return the invoice
        return invoice

    def get_invoice_status(self, invoice_id: str) -> Optional[str]:
        """Get the status of an invoice by ID."""
        # In a real implementation, this would look up the invoice in a database
        return None

    def update_invoice_status(
        self, invoice_id: str, new_status: str, payment_date: Optional[datetime] = None
    ) -> bool:
        """
        Update the status of an invoice.

        Args:
            invoice_id: ID of the invoice to update
            new_status: New status value
            payment_date: Date of payment if status is 'paid'

        Returns:
            True if the update was successful
        """
        # In a real implementation, this would update the invoice in a database
        return True