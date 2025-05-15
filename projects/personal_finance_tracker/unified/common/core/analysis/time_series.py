"""Time series analysis utilities shared across implementations."""

import time
from datetime import datetime, timedelta, date
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from uuid import UUID

import numpy as np
from pydantic import BaseModel, Field

from common.core.analysis.analyzer import BaseAnalyzer, AnalysisResult, AnalysisParameters


class TimeSeriesGranularity(str, Enum):
    """Granularity for time series data."""
    
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class TimeSeriesData(BaseModel):
    """
    Model for time series data.
    
    Used for storing and manipulating time series data for analysis.
    """
    
    dates: List[Union[date, datetime]]
    values: List[float]
    labels: Optional[List[str]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True


class TimeSeriesParameters(AnalysisParameters):
    """
    Parameters for time series analysis.
    
    Used to configure time series analysis options and settings.
    """
    
    granularity: TimeSeriesGranularity = TimeSeriesGranularity.MONTHLY
    smoothing_method: Optional[str] = None  # "moving_avg", "exponential", "seasonal"
    window_size: int = 3  # For moving average
    alpha: float = 0.3  # For exponential smoothing
    seasonal_period: int = 12  # For seasonal adjustment
    fill_missing: bool = True
    normalize: bool = False
    extrapolate: bool = False
    extrapolation_periods: int = 3


class TimeSeriesAnalyzer:
    """
    Utility class for analyzing time series data.
    
    Provides methods for smoothing, trend detection, and forecasting.
    """
    
    @staticmethod
    def moving_average(
        data: TimeSeriesData, window_size: int = 3
    ) -> TimeSeriesData:
        """
        Calculate the moving average of time series data.
        
        Args:
            data: The time series data
            window_size: The window size for the moving average
            
        Returns:
            New time series data with smoothed values
        """
        if not data.values:
            return TimeSeriesData(dates=[], values=[])
        
        # Convert to numpy array for efficient calculation
        values = np.array(data.values)
        
        # Calculate the cumulative sum of values
        cumsum = np.cumsum(values)
        
        # Calculate the moving average using the window
        smoothed = np.zeros_like(values)
        
        # Handle the start of the array (where we don't have a full window)
        for i in range(min(window_size, len(values))):
            smoothed[i] = cumsum[i] / (i + 1)
        
        # Handle the rest of the array
        for i in range(window_size, len(values)):
            smoothed[i] = (cumsum[i] - cumsum[i - window_size]) / window_size
        
        # Create new time series data with smoothed values
        return TimeSeriesData(
            dates=data.dates,
            values=smoothed.tolist(),
            labels=data.labels,
            metadata={
                **data.metadata,
                "smoothing_method": "moving_average",
                "window_size": window_size,
            },
        )
    
    @staticmethod
    def exponential_smoothing(
        data: TimeSeriesData, alpha: float = 0.3
    ) -> TimeSeriesData:
        """
        Apply exponential smoothing to time series data.
        
        Args:
            data: The time series data
            alpha: The smoothing factor (0 < alpha < 1)
            
        Returns:
            New time series data with smoothed values
        """
        if not data.values:
            return TimeSeriesData(dates=[], values=[])
        
        # Ensure alpha is between 0 and 1
        alpha = max(0.01, min(0.99, alpha))
        
        # Convert to numpy array for efficient calculation
        values = np.array(data.values)
        
        # Initialize the smoothed array with the first value
        smoothed = np.zeros_like(values)
        smoothed[0] = values[0]
        
        # Apply exponential smoothing
        for i in range(1, len(values)):
            smoothed[i] = alpha * values[i] + (1 - alpha) * smoothed[i - 1]
        
        # Create new time series data with smoothed values
        return TimeSeriesData(
            dates=data.dates,
            values=smoothed.tolist(),
            labels=data.labels,
            metadata={
                **data.metadata,
                "smoothing_method": "exponential",
                "alpha": alpha,
            },
        )
    
    @staticmethod
    def seasonal_adjustment(
        data: TimeSeriesData, period: int = 12
    ) -> TimeSeriesData:
        """
        Apply seasonal adjustment to time series data.
        
        Args:
            data: The time series data
            period: The seasonal period (e.g., 12 for monthly data with yearly seasonality)
            
        Returns:
            New time series data with seasonally adjusted values
        """
        if not data.values or len(data.values) < period * 2:
            # Not enough data for seasonal adjustment
            return data
        
        # Convert to numpy array for efficient calculation
        values = np.array(data.values)
        
        # Calculate the seasonal indices
        seasonal_indices = np.zeros(period)
        seasonal_data = []
        
        # Organize data by season
        for i in range(period):
            seasonal_data.append(values[i::period])
        
        # Calculate average for each season
        for i in range(period):
            if len(seasonal_data[i]) > 0:
                seasonal_indices[i] = np.mean(seasonal_data[i])
        
        # Normalize the seasonal indices
        if np.sum(seasonal_indices) > 0:
            seasonal_indices = seasonal_indices * period / np.sum(seasonal_indices)
        
        # Apply the seasonal adjustment
        adjusted = np.zeros_like(values)
        for i in range(len(values)):
            season_idx = i % period
            if seasonal_indices[season_idx] > 0:
                adjusted[i] = values[i] / seasonal_indices[season_idx]
            else:
                adjusted[i] = values[i]
        
        # Create new time series data with adjusted values
        return TimeSeriesData(
            dates=data.dates,
            values=adjusted.tolist(),
            labels=data.labels,
            metadata={
                **data.metadata,
                "smoothing_method": "seasonal",
                "period": period,
                "seasonal_indices": seasonal_indices.tolist(),
            },
        )
    
    @staticmethod
    def detect_trend(data: TimeSeriesData) -> Dict[str, Any]:
        """
        Detect trends in time series data.
        
        Args:
            data: The time series data
            
        Returns:
            Dictionary with trend information
        """
        if not data.values or len(data.values) < 2:
            return {
                "has_trend": False,
                "trend_direction": "none",
                "trend_strength": 0.0,
            }
        
        # Convert to numpy array for efficient calculation
        values = np.array(data.values)
        
        # Simple linear regression
        x = np.arange(len(values))
        A = np.vstack([x, np.ones(len(x))]).T
        
        # Solve for the best fit line
        try:
            slope, intercept = np.linalg.lstsq(A, values, rcond=None)[0]
        except:
            # Fallback if linear algebra fails
            slope = 0.0
            intercept = np.mean(values) if len(values) > 0 else 0.0
        
        # Calculate trend strength (R-squared)
        y_hat = slope * x + intercept
        ss_total = np.sum((values - np.mean(values)) ** 2)
        ss_residual = np.sum((values - y_hat) ** 2)
        r_squared = 1 - (ss_residual / ss_total) if ss_total > 0 else 0.0
        
        # Determine trend direction
        trend_direction = "up" if slope > 0 else "down" if slope < 0 else "none"
        
        return {
            "has_trend": abs(slope) > 0.01,
            "trend_direction": trend_direction,
            "trend_strength": r_squared,
            "slope": slope,
            "intercept": intercept,
        }
    
    @staticmethod
    def extrapolate(
        data: TimeSeriesData, periods: int = 3, method: str = "linear"
    ) -> TimeSeriesData:
        """
        Extrapolate time series data into the future.
        
        Args:
            data: The time series data
            periods: The number of periods to extrapolate
            method: The extrapolation method ("linear", "mean", "last")
            
        Returns:
            New time series data with extrapolated values
        """
        if not data.values or periods <= 0:
            return data
        
        # Convert to numpy array for efficient calculation
        values = np.array(data.values)
        dates = data.dates.copy()
        
        # Determine the date increment
        if len(dates) >= 2:
            if isinstance(dates[0], datetime):
                # For datetime objects
                date_diff = dates[1] - dates[0]
            else:
                # For date objects
                date_diff = timedelta(days=(dates[1] - dates[0]).days)
        else:
            # Default to daily if we can't determine
            date_diff = timedelta(days=1)
        
        # Extrapolate dates
        last_date = dates[-1]
        extrapolated_dates = []
        
        for i in range(1, periods + 1):
            if isinstance(last_date, datetime):
                next_date = last_date + date_diff * i
            else:
                # Convert to datetime for easier arithmetic, then back to date
                next_date = (datetime.combine(last_date, datetime.min.time()) + date_diff * i).date()
            
            extrapolated_dates.append(next_date)
        
        # Extrapolate values based on the method
        extrapolated_values = []
        
        if method == "linear" and len(values) >= 2:
            # Simple linear extrapolation
            trend_info = TimeSeriesAnalyzer.detect_trend(data)
            slope = trend_info["slope"]
            intercept = trend_info["intercept"]
            
            for i in range(1, periods + 1):
                next_value = slope * (len(values) + i - 1) + intercept
                extrapolated_values.append(next_value)
        
        elif method == "mean" and len(values) > 0:
            # Use the mean of the last few values
            window = min(len(values), 3)
            mean_value = np.mean(values[-window:])
            
            for _ in range(periods):
                extrapolated_values.append(mean_value)
        
        else:
            # Default to using the last value
            last_value = values[-1] if len(values) > 0 else 0.0
            
            for _ in range(periods):
                extrapolated_values.append(last_value)
        
        # Create new time series data with original and extrapolated values
        return TimeSeriesData(
            dates=dates + extrapolated_dates,
            values=values.tolist() + extrapolated_values,
            labels=data.labels,
            metadata={
                **data.metadata,
                "extrapolation_method": method,
                "extrapolation_periods": periods,
                "original_length": len(values),
            },
        )
    
    @staticmethod
    def normalize(data: TimeSeriesData) -> TimeSeriesData:
        """
        Normalize time series data to a 0-1 range.
        
        Args:
            data: The time series data
            
        Returns:
            New time series data with normalized values
        """
        if not data.values:
            return TimeSeriesData(dates=[], values=[])
        
        # Convert to numpy array for efficient calculation
        values = np.array(data.values)
        
        # Calculate min and max
        min_value = np.min(values)
        max_value = np.max(values)
        
        # Normalize the values
        if max_value > min_value:
            normalized = (values - min_value) / (max_value - min_value)
        else:
            # If all values are the same, normalize to 0.5
            normalized = np.full_like(values, 0.5)
        
        # Create new time series data with normalized values
        return TimeSeriesData(
            dates=data.dates,
            values=normalized.tolist(),
            labels=data.labels,
            metadata={
                **data.metadata,
                "normalization": True,
                "original_min": float(min_value),
                "original_max": float(max_value),
            },
        )
    
    @staticmethod
    def aggregate_by_period(
        dates: List[Union[date, datetime]],
        values: List[float],
        granularity: TimeSeriesGranularity,
        aggregation_fn: Callable[[List[float]], float] = lambda x: sum(x),
    ) -> Tuple[List[Union[date, datetime]], List[float]]:
        """
        Aggregate time series data by a specified granularity.
        
        Args:
            dates: List of dates
            values: List of values
            granularity: The desired granularity
            aggregation_fn: Function to aggregate values within a period
            
        Returns:
            Tuple of (aggregated_dates, aggregated_values)
        """
        if not dates or not values:
            return [], []
        
        # Combine dates and values for sorting and grouping
        data = list(zip(dates, values))
        data.sort(key=lambda x: x[0])  # Sort by date
        
        # Group by the specified granularity
        grouped_data = {}
        
        for dt, value in data:
            # Convert to datetime if it's a date
            if isinstance(dt, date) and not isinstance(dt, datetime):
                dt = datetime.combine(dt, datetime.min.time())
            
            # Group based on granularity
            if granularity == TimeSeriesGranularity.DAILY:
                key = dt.replace(hour=0, minute=0, second=0, microsecond=0)
            elif granularity == TimeSeriesGranularity.WEEKLY:
                # Get start of the week (Monday)
                start_of_week = dt - timedelta(days=dt.weekday())
                key = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
            elif granularity == TimeSeriesGranularity.MONTHLY:
                key = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            elif granularity == TimeSeriesGranularity.QUARTERLY:
                quarter = (dt.month - 1) // 3
                key = dt.replace(month=quarter * 3 + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
            elif granularity == TimeSeriesGranularity.YEARLY:
                key = dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                # Default to daily
                key = dt.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Add to the group
            if key in grouped_data:
                grouped_data[key].append(value)
            else:
                grouped_data[key] = [value]
        
        # Aggregate values within each group
        aggregated_data = [
            (key, aggregation_fn(values)) for key, values in grouped_data.items()
        ]
        
        # Sort by date and separate dates and values
        aggregated_data.sort(key=lambda x: x[0])
        
        # Convert datetime back to date if the input was dates
        if all(isinstance(dt, date) and not isinstance(dt, datetime) for dt in dates):
            aggregated_dates = [dt.date() for dt, _ in aggregated_data]
        else:
            aggregated_dates = [dt for dt, _ in aggregated_data]
            
        aggregated_values = [value for _, value in aggregated_data]
        
        return aggregated_dates, aggregated_values