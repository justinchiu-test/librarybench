"""
Resource usage forecasting for the unified concurrent task scheduler.

This module provides functionality for forecasting resource usage that can be used
by both the render farm manager and scientific computing implementations.
"""

import json
import logging
import math
import os
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Any, Union, Callable

import numpy as np

from common.core.exceptions import ConfigurationError
from common.core.interfaces import ResourceForecastingInterface
from common.core.models import (
    BaseJob,
    BaseNode,
    ResourceType,
    Result,
)
from common.core.utils import create_directory_if_not_exists

logger = logging.getLogger(__name__)


class ForecastMethod(str, Enum):
    """Methods for generating resource forecasts."""
    
    MOVING_AVERAGE = "moving_average"  # Simple moving average
    WEIGHTED_AVERAGE = "weighted_average"  # Weighted moving average
    EXPONENTIAL = "exponential"  # Exponential smoothing
    LINEAR_REGRESSION = "linear_regression"  # Linear regression
    CUSTOM = "custom"  # Custom forecasting method


class ResourceData:
    """Historical resource usage data for forecasting."""
    
    def __init__(
        self,
        owner_id: str,
        resource_type: ResourceType,
    ):
        """
        Initialize resource data.
        
        Args:
            owner_id: ID of the owner
            resource_type: Type of resource
        """
        self.owner_id = owner_id
        self.resource_type = resource_type
        self.data_points: List[Tuple[datetime, float]] = []
        self.last_update = datetime.now()
    
    def add_data_point(self, timestamp: datetime, value: float) -> None:
        """
        Add a data point.
        
        Args:
            timestamp: Time of the data point
            value: Resource usage value
        """
        self.data_points.append((timestamp, value))
        self.data_points.sort(key=lambda x: x[0])  # Sort by timestamp
        self.last_update = datetime.now()
    
    def get_data_in_range(
        self,
        start_time: datetime,
        end_time: datetime,
    ) -> List[Tuple[datetime, float]]:
        """
        Get data points within a time range.
        
        Args:
            start_time: Start of the time range
            end_time: End of the time range
            
        Returns:
            List of data points in the range
        """
        return [
            (ts, value) for ts, value in self.data_points
            if start_time <= ts <= end_time
        ]
    
    def get_recent_data(
        self,
        duration: timedelta = timedelta(days=30),
    ) -> List[Tuple[datetime, float]]:
        """
        Get recent data points.
        
        Args:
            duration: How far back to look
            
        Returns:
            List of recent data points
        """
        cutoff = datetime.now() - duration
        return [
            (ts, value) for ts, value in self.data_points
            if ts >= cutoff
        ]
    
    def clear_old_data(
        self,
        retention_days: int = 365,
    ) -> int:
        """
        Clear data points older than the retention period.
        
        Args:
            retention_days: Number of days to retain data
            
        Returns:
            Number of data points removed
        """
        cutoff = datetime.now() - timedelta(days=retention_days)
        old_count = len(self.data_points)
        
        self.data_points = [
            (ts, value) for ts, value in self.data_points
            if ts >= cutoff
        ]
        
        return old_count - len(self.data_points)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "owner_id": self.owner_id,
            "resource_type": self.resource_type.value,
            "data_points": [
                {"timestamp": ts.isoformat(), "value": value}
                for ts, value in self.data_points
            ],
            "last_update": self.last_update.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResourceData":
        """Create from dictionary."""
        resource_data = cls(
            owner_id=data["owner_id"],
            resource_type=ResourceType(data["resource_type"]),
        )
        
        # Parse data points
        for point in data.get("data_points", []):
            try:
                timestamp = datetime.fromisoformat(point["timestamp"])
                value = float(point["value"])
                resource_data.data_points.append((timestamp, value))
            except (ValueError, KeyError):
                continue
        
        # Parse last update time
        if "last_update" in data:
            try:
                resource_data.last_update = datetime.fromisoformat(data["last_update"])
            except ValueError:
                pass
        
        return resource_data


class ForecastModel:
    """Base class for forecast models."""
    
    def __init__(
        self,
        owner_id: str,
        resource_type: ResourceType,
        method: ForecastMethod = ForecastMethod.MOVING_AVERAGE,
        parameters: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a forecast model.
        
        Args:
            owner_id: ID of the owner
            resource_type: Type of resource
            method: Forecasting method
            parameters: Parameters for the forecast method
        """
        self.owner_id = owner_id
        self.resource_type = resource_type
        self.method = method
        self.parameters = parameters or {}
        self.trained = False
        self.last_training = None
        self.model_data: Dict[str, Any] = {}
        self.accuracy_metrics: Dict[str, float] = {}
    
    def train(self, data: ResourceData) -> bool:
        """
        Train the forecast model on historical data.
        
        Args:
            data: Historical resource usage data
            
        Returns:
            True if training was successful, False otherwise
        """
        if len(data.data_points) < 2:
            return False
        
        # Extract data
        timestamps = [ts for ts, _ in data.data_points]
        values = [value for _, value in data.data_points]
        
        # Convert timestamps to numeric values (seconds since epoch)
        times = [(ts - datetime(1970, 1, 1)).total_seconds() for ts in timestamps]
        
        try:
            if self.method == ForecastMethod.MOVING_AVERAGE:
                # Simple moving average
                window_size = self.parameters.get("window_size", 5)
                if len(values) < window_size:
                    window_size = len(values)
                
                self.model_data = {
                    "window_size": window_size,
                    "last_values": values[-window_size:],
                }
                
                # Calculate accuracy metrics
                self._calculate_accuracy_metrics(data)
                
                self.trained = True
                self.last_training = datetime.now()
                return True
                
            elif self.method == ForecastMethod.WEIGHTED_AVERAGE:
                # Weighted moving average
                window_size = self.parameters.get("window_size", 5)
                if len(values) < window_size:
                    window_size = len(values)
                
                # Default weights: more recent values have higher weights
                weights = self.parameters.get("weights", None)
                if weights is None or len(weights) != window_size:
                    weights = [i+1 for i in range(window_size)]
                    weights_sum = sum(weights)
                    weights = [w / weights_sum for w in weights]
                
                self.model_data = {
                    "window_size": window_size,
                    "weights": weights,
                    "last_values": values[-window_size:],
                }
                
                # Calculate accuracy metrics
                self._calculate_accuracy_metrics(data)
                
                self.trained = True
                self.last_training = datetime.now()
                return True
                
            elif self.method == ForecastMethod.EXPONENTIAL:
                # Exponential smoothing
                alpha = self.parameters.get("alpha", 0.3)
                beta = self.parameters.get("beta", 0.1)
                
                # Initialize level and trend
                level = values[0]
                trend = values[1] - values[0] if len(values) > 1 else 0
                
                # Apply exponential smoothing
                for value in values[1:]:
                    prev_level = level
                    level = alpha * value + (1 - alpha) * (level + trend)
                    trend = beta * (level - prev_level) + (1 - beta) * trend
                
                self.model_data = {
                    "alpha": alpha,
                    "beta": beta,
                    "level": level,
                    "trend": trend,
                }
                
                # Calculate accuracy metrics
                self._calculate_accuracy_metrics(data)
                
                self.trained = True
                self.last_training = datetime.now()
                return True
                
            elif self.method == ForecastMethod.LINEAR_REGRESSION:
                # Linear regression
                if len(times) < 2:
                    return False
                
                # Calculate slope and intercept
                n = len(times)
                sum_x = sum(times)
                sum_y = sum(values)
                sum_xy = sum(x * y for x, y in zip(times, values))
                sum_xx = sum(x * x for x in times)
                
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
                intercept = (sum_y - slope * sum_x) / n
                
                self.model_data = {
                    "slope": slope,
                    "intercept": intercept,
                    "x_offset": times[0],  # For numerical stability
                }
                
                # Calculate accuracy metrics
                self._calculate_accuracy_metrics(data)
                
                self.trained = True
                self.last_training = datetime.now()
                return True
                
            elif self.method == ForecastMethod.CUSTOM:
                # Custom method provided by the user
                if "train_func" not in self.parameters:
                    return False
                
                train_func = self.parameters["train_func"]
                result = train_func(data.data_points)
                
                if isinstance(result, dict):
                    self.model_data = result
                    
                    # Calculate accuracy metrics
                    self._calculate_accuracy_metrics(data)
                    
                    self.trained = True
                    self.last_training = datetime.now()
                    return True
                
                return False
                
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error training forecast model: {e}")
            return False
    
    def predict(
        self,
        target_time: datetime,
    ) -> Optional[float]:
        """
        Generate a prediction for a target time.
        
        Args:
            target_time: The time to predict for
            
        Returns:
            Predicted resource usage value
        """
        if not self.trained:
            return None
        
        try:
            if self.method == ForecastMethod.MOVING_AVERAGE:
                # Simple moving average - return average of last values
                if "last_values" in self.model_data:
                    return sum(self.model_data["last_values"]) / len(self.model_data["last_values"])
                return None
                
            elif self.method == ForecastMethod.WEIGHTED_AVERAGE:
                # Weighted moving average
                if "last_values" in self.model_data and "weights" in self.model_data:
                    values = self.model_data["last_values"]
                    weights = self.model_data["weights"]
                    
                    if len(values) != len(weights):
                        weights = weights[:len(values)] if len(weights) > len(values) else weights + [0] * (len(values) - len(weights))
                    
                    return sum(v * w for v, w in zip(values, weights))
                
                return None
                
            elif self.method == ForecastMethod.EXPONENTIAL:
                # Exponential smoothing - extrapolate based on level and trend
                if "level" in self.model_data and "trend" in self.model_data:
                    level = self.model_data["level"]
                    trend = self.model_data["trend"]
                    
                    # Calculate time difference in days
                    now = datetime.now()
                    days_ahead = (target_time - now).total_seconds() / (60 * 60 * 24)
                    
                    return level + trend * days_ahead
                
                return None
                
            elif self.method == ForecastMethod.LINEAR_REGRESSION:
                # Linear regression
                if "slope" in self.model_data and "intercept" in self.model_data:
                    slope = self.model_data["slope"]
                    intercept = self.model_data["intercept"]
                    x_offset = self.model_data.get("x_offset", 0)
                    
                    # Convert target time to seconds since epoch
                    x = (target_time - datetime(1970, 1, 1)).total_seconds() - x_offset
                    
                    return slope * x + intercept
                
                return None
                
            elif self.method == ForecastMethod.CUSTOM:
                # Custom method provided by the user
                if "predict_func" not in self.parameters:
                    return None
                
                predict_func = self.parameters["predict_func"]
                return predict_func(target_time, self.model_data)
                
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error generating prediction: {e}")
            return None
    
    def generate_forecast(
        self,
        start_date: datetime,
        end_date: datetime,
        interval_hours: int = 24,
    ) -> Dict[datetime, float]:
        """
        Generate a forecast for a time range.
        
        Args:
            start_date: Start of the forecast range
            end_date: End of the forecast range
            interval_hours: Hours between forecast points
            
        Returns:
            Dictionary mapping times to predicted values
        """
        if not self.trained:
            return {}
        
        forecast = {}
        current_time = start_date
        
        while current_time <= end_date:
            prediction = self.predict(current_time)
            
            if prediction is not None:
                forecast[current_time] = prediction
            
            current_time += timedelta(hours=interval_hours)
        
        return forecast
    
    def _calculate_accuracy_metrics(self, data: ResourceData) -> None:
        """
        Calculate accuracy metrics for the model.
        
        Args:
            data: Historical resource usage data
        """
        if len(data.data_points) < 5:
            # Not enough data for meaningful metrics
            self.accuracy_metrics = {
                "mse": 0.0,
                "mae": 0.0,
                "mape": 0.0,
                "r2": 0.0,
            }
            return
        
        # Split data into training and testing sets (80/20)
        split_index = int(len(data.data_points) * 0.8)
        train_data = data.data_points[:split_index]
        test_data = data.data_points[split_index:]
        
        if not test_data:
            self.accuracy_metrics = {
                "mse": 0.0,
                "mae": 0.0,
                "mape": 0.0,
                "r2": 0.0,
            }
            return
        
        # Train a temporary model on training data
        temp_data = ResourceData(data.owner_id, data.resource_type)
        for ts, value in train_data:
            temp_data.add_data_point(ts, value)
        
        temp_model = ForecastModel(
            self.owner_id,
            self.resource_type,
            self.method,
            self.parameters,
        )
        temp_model.train(temp_data)
        
        # Calculate metrics on test data
        actual_values = [value for _, value in test_data]
        predicted_values = [temp_model.predict(ts) or 0.0 for ts, _ in test_data]
        
        # Mean Squared Error (MSE)
        mse = sum((a - p) ** 2 for a, p in zip(actual_values, predicted_values)) / len(test_data)
        
        # Mean Absolute Error (MAE)
        mae = sum(abs(a - p) for a, p in zip(actual_values, predicted_values)) / len(test_data)
        
        # Mean Absolute Percentage Error (MAPE)
        mape_values = []
        for a, p in zip(actual_values, predicted_values):
            if a != 0:
                mape_values.append(abs((a - p) / a))
        
        mape = sum(mape_values) / len(mape_values) if mape_values else 0.0
        
        # R-squared (coefficient of determination)
        mean_actual = sum(actual_values) / len(actual_values)
        ss_total = sum((a - mean_actual) ** 2 for a in actual_values)
        ss_residual = sum((a - p) ** 2 for a, p in zip(actual_values, predicted_values))
        
        r2 = 1 - (ss_residual / ss_total) if ss_total != 0 else 0.0
        
        self.accuracy_metrics = {
            "mse": mse,
            "mae": mae,
            "mape": mape * 100.0,  # Convert to percentage
            "r2": r2,
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "owner_id": self.owner_id,
            "resource_type": self.resource_type.value,
            "method": self.method.value,
            "parameters": {k: v for k, v in self.parameters.items() if not callable(v)},
            "trained": self.trained,
            "last_training": self.last_training.isoformat() if self.last_training else None,
            "model_data": self.model_data,
            "accuracy_metrics": self.accuracy_metrics,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ForecastModel":
        """Create from dictionary."""
        model = cls(
            owner_id=data["owner_id"],
            resource_type=ResourceType(data["resource_type"]),
            method=ForecastMethod(data["method"]),
            parameters=data.get("parameters", {}),
        )
        
        model.trained = data.get("trained", False)
        
        if "last_training" in data and data["last_training"]:
            try:
                model.last_training = datetime.fromisoformat(data["last_training"])
            except ValueError:
                pass
        
        model.model_data = data.get("model_data", {})
        model.accuracy_metrics = data.get("accuracy_metrics", {})
        
        return model


class ResourceForecaster(ResourceForecastingInterface):
    """
    Forecaster for resource usage.
    
    This class is responsible for:
    1. Collecting historical resource usage data
    2. Training forecast models
    3. Generating resource usage forecasts
    """
    
    def __init__(
        self,
        data_directory: Optional[str] = None,
        default_method: ForecastMethod = ForecastMethod.MOVING_AVERAGE,
        default_parameters: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the resource forecaster.
        
        Args:
            data_directory: Directory for storing historical data
            default_method: Default forecasting method
            default_parameters: Default parameters for the forecasting method
        """
        import tempfile
        self.data_directory = data_directory or os.path.join(tempfile.gettempdir(), "resource_forecasts")
        self.default_method = default_method
        self.default_parameters = default_parameters or {}
        
        self.historical_data: Dict[str, Dict[str, ResourceData]] = {}  # owner_id -> resource_type -> ResourceData
        self.forecast_models: Dict[str, Dict[str, ForecastModel]] = {}  # owner_id -> resource_type -> ForecastModel
        
        # Create data directory if it doesn't exist
        create_directory_if_not_exists(self.data_directory)
        
        # Load existing data
        self._load_data()
    
    def add_data_point(
        self,
        owner_id: str,
        resource_type: ResourceType,
        value: float,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """
        Add a resource usage data point.
        
        Args:
            owner_id: ID of the owner
            resource_type: Type of resource
            value: Resource usage value
            timestamp: Time of the data point (defaults to now)
        """
        timestamp = timestamp or datetime.now()
        
        # Initialize data structures if needed
        if owner_id not in self.historical_data:
            self.historical_data[owner_id] = {}
        
        if resource_type not in self.historical_data[owner_id]:
            self.historical_data[owner_id][resource_type] = ResourceData(owner_id, resource_type)
        
        # Add the data point
        self.historical_data[owner_id][resource_type].add_data_point(timestamp, value)
        
        # Save the data
        self._save_data(owner_id, resource_type)
    
    def add_multiple_data_points(
        self,
        owner_id: str,
        resource_type: ResourceType,
        data_points: List[Tuple[datetime, float]],
    ) -> None:
        """
        Add multiple resource usage data points.
        
        Args:
            owner_id: ID of the owner
            resource_type: Type of resource
            data_points: List of (timestamp, value) tuples
        """
        # Initialize data structures if needed
        if owner_id not in self.historical_data:
            self.historical_data[owner_id] = {}
        
        if resource_type not in self.historical_data[owner_id]:
            self.historical_data[owner_id][resource_type] = ResourceData(owner_id, resource_type)
        
        # Add the data points
        for timestamp, value in data_points:
            self.historical_data[owner_id][resource_type].add_data_point(timestamp, value)
        
        # Save the data
        self._save_data(owner_id, resource_type)
    
    def get_historical_data(
        self,
        owner_id: str,
        resource_type: ResourceType,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Tuple[datetime, float]]:
        """
        Get historical resource usage data.
        
        Args:
            owner_id: ID of the owner
            resource_type: Type of resource
            start_date: Optional start of the time range
            end_date: Optional end of the time range
            
        Returns:
            List of data points in the specified range
        """
        if owner_id not in self.historical_data:
            return []
        
        if resource_type not in self.historical_data[owner_id]:
            return []
        
        data = self.historical_data[owner_id][resource_type]
        
        if start_date and end_date:
            return data.get_data_in_range(start_date, end_date)
        
        return data.data_points.copy()
    
    def train_model(
        self,
        owner_id: str,
        resource_type: ResourceType,
        method: Optional[ForecastMethod] = None,
        parameters: Optional[Dict[str, Any]] = None,
        training_days: int = 30,
    ) -> Result[bool]:
        """
        Train a forecast model for a specific owner and resource type.
        
        Args:
            owner_id: ID of the owner
            resource_type: Type of resource to forecast
            method: Forecasting method
            parameters: Parameters for the forecasting method
            training_days: Number of days of historical data to use
            
        Returns:
            Result with success status or error
        """
        # Check if we have historical data
        if owner_id not in self.historical_data or resource_type not in self.historical_data[owner_id]:
            return Result.err(f"No historical data available for {owner_id}/{resource_type.value}")
        
        data = self.historical_data[owner_id][resource_type]
        
        # Get recent data for training
        recent_data = ResourceData(owner_id, resource_type)
        for ts, value in data.get_recent_data(timedelta(days=training_days)):
            recent_data.add_data_point(ts, value)
        
        if len(recent_data.data_points) < 2:
            return Result.err(f"Insufficient historical data for training (need at least 2 data points)")
        
        # Use default method and parameters if not specified
        method = method or self.default_method
        parameters = parameters or self.default_parameters
        
        # Initialize model
        model = ForecastModel(
            owner_id=owner_id,
            resource_type=resource_type,
            method=method,
            parameters=parameters,
        )
        
        # Train the model
        success = model.train(recent_data)
        
        if success:
            # Store the trained model
            if owner_id not in self.forecast_models:
                self.forecast_models[owner_id] = {}
            
            self.forecast_models[owner_id][resource_type] = model
            
            # Save the model
            self._save_model(owner_id, resource_type)
            
            return Result.ok(True)
        
        return Result.err(f"Failed to train model for {owner_id}/{resource_type.value}")
    
    def generate_forecast(
        self,
        owner_id: str,
        resource_type: ResourceType,
        start_date: datetime,
        end_date: datetime,
        interval_hours: int = 24,
    ) -> Result[Dict[datetime, float]]:
        """
        Generate a resource usage forecast.
        
        Args:
            owner_id: ID of the owner
            resource_type: Type of resource to forecast
            start_date: Start date for the forecast
            end_date: End date for the forecast
            interval_hours: Hours between forecast points
            
        Returns:
            Result with dictionary mapping dates to forecasted values
        """
        # Check if we have a trained model
        if owner_id not in self.forecast_models or resource_type not in self.forecast_models[owner_id]:
            # Try to train a model
            result = self.train_model(owner_id, resource_type)
            if not result.success:
                return Result.err(f"No trained model available for {owner_id}/{resource_type.value}")
        
        model = self.forecast_models[owner_id][resource_type]
        
        if not model.trained:
            return Result.err(f"Model for {owner_id}/{resource_type.value} is not trained")
        
        # Generate the forecast
        forecast = model.generate_forecast(start_date, end_date, interval_hours)
        
        if not forecast:
            return Result.err(f"Failed to generate forecast for {owner_id}/{resource_type.value}")
        
        return Result.ok(forecast)
    
    def evaluate_accuracy(
        self,
        owner_id: str,
        resource_type: ResourceType,
    ) -> Result[Dict[str, float]]:
        """
        Evaluate the accuracy of the forecasting model.
        
        Args:
            owner_id: ID of the owner
            resource_type: Type of resource to evaluate
            
        Returns:
            Result with dictionary of accuracy metrics
        """
        # Check if we have a trained model
        if owner_id not in self.forecast_models or resource_type not in self.forecast_models[owner_id]:
            return Result.err(f"No trained model available for {owner_id}/{resource_type.value}")
        
        model = self.forecast_models[owner_id][resource_type]
        
        if not model.trained:
            return Result.err(f"Model for {owner_id}/{resource_type.value} is not trained")
        
        # Return the accuracy metrics
        metrics = model.accuracy_metrics
        
        if not metrics:
            return Result.err(f"No accuracy metrics available for {owner_id}/{resource_type.value}")
        
        return Result.ok(metrics)
    
    def clear_old_data(
        self,
        retention_days: int = 365,
    ) -> Dict[str, int]:
        """
        Clear data points older than the retention period.
        
        Args:
            retention_days: Number of days to retain data
            
        Returns:
            Dictionary mapping owner_id+resource_type to number of data points removed
        """
        removed_counts: Dict[str, int] = {}
        
        for owner_id, resources in self.historical_data.items():
            for resource_type, data in resources.items():
                count = data.clear_old_data(retention_days)
                if count > 0:
                    key = f"{owner_id}/{resource_type.value}"
                    removed_counts[key] = count
                    self._save_data(owner_id, resource_type)
        
        return removed_counts
    
    def _load_data(self) -> None:
        """Load historical data and models from disk."""
        try:
            # Load historical data
            data_dir = os.path.join(self.data_directory, "data")
            if os.path.isdir(data_dir):
                for owner_dir in os.listdir(data_dir):
                    owner_path = os.path.join(data_dir, owner_dir)
                    if not os.path.isdir(owner_path):
                        continue
                    
                    for filename in os.listdir(owner_path):
                        if not filename.endswith(".json"):
                            continue
                        
                        resource_type_str = filename.split(".")[0]
                        try:
                            resource_type = ResourceType(resource_type_str)
                        except ValueError:
                            continue
                        
                        file_path = os.path.join(owner_path, filename)
                        with open(file_path, "r") as f:
                            try:
                                data_dict = json.load(f)
                                resource_data = ResourceData.from_dict(data_dict)
                                
                                if owner_dir not in self.historical_data:
                                    self.historical_data[owner_dir] = {}
                                
                                self.historical_data[owner_dir][resource_type] = resource_data
                            except (json.JSONDecodeError, KeyError):
                                continue
            
            # Load forecast models
            model_dir = os.path.join(self.data_directory, "models")
            if os.path.isdir(model_dir):
                for owner_dir in os.listdir(model_dir):
                    owner_path = os.path.join(model_dir, owner_dir)
                    if not os.path.isdir(owner_path):
                        continue
                    
                    for filename in os.listdir(owner_path):
                        if not filename.endswith(".json"):
                            continue
                        
                        resource_type_str = filename.split(".")[0]
                        try:
                            resource_type = ResourceType(resource_type_str)
                        except ValueError:
                            continue
                        
                        file_path = os.path.join(owner_path, filename)
                        with open(file_path, "r") as f:
                            try:
                                data_dict = json.load(f)
                                forecast_model = ForecastModel.from_dict(data_dict)
                                
                                if owner_dir not in self.forecast_models:
                                    self.forecast_models[owner_dir] = {}
                                
                                self.forecast_models[owner_dir][resource_type] = forecast_model
                            except (json.JSONDecodeError, KeyError):
                                continue
        except Exception as e:
            logger.error(f"Error loading resource forecast data: {e}")
    
    def _save_data(
        self,
        owner_id: str,
        resource_type: ResourceType,
    ) -> None:
        """
        Save historical data to disk.
        
        Args:
            owner_id: ID of the owner
            resource_type: Type of resource
        """
        try:
            # Get the data
            if owner_id not in self.historical_data or resource_type not in self.historical_data[owner_id]:
                return
            
            data = self.historical_data[owner_id][resource_type]
            
            # Create the directory if it doesn't exist
            data_dir = os.path.join(self.data_directory, "data", owner_id)
            create_directory_if_not_exists(data_dir)
            
            # Save the data
            file_path = os.path.join(data_dir, f"{resource_type.value}.json")
            with open(file_path, "w") as f:
                json.dump(data.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving resource forecast data: {e}")
    
    def _save_model(
        self,
        owner_id: str,
        resource_type: ResourceType,
    ) -> None:
        """
        Save a forecast model to disk.
        
        Args:
            owner_id: ID of the owner
            resource_type: Type of resource
        """
        try:
            # Get the model
            if owner_id not in self.forecast_models or resource_type not in self.forecast_models[owner_id]:
                return
            
            model = self.forecast_models[owner_id][resource_type]
            
            # Create the directory if it doesn't exist
            model_dir = os.path.join(self.data_directory, "models", owner_id)
            create_directory_if_not_exists(model_dir)
            
            # Save the model
            file_path = os.path.join(model_dir, f"{resource_type.value}.json")
            with open(file_path, "w") as f:
                json.dump(model.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving forecast model: {e}")