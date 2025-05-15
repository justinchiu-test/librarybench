"""Data collection for resource usage forecasting."""

from __future__ import annotations

import logging
import math
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Union

import numpy as np
import pandas as pd

from concurrent_task_scheduler.models import (
    ResourceType,
    Result,
    Simulation,
    UtilizationDataPoint,
)
from concurrent_task_scheduler.models.resource_forecast import ResourceUtilizationHistory

logger = logging.getLogger(__name__)


class AggregationMethod(str, Enum):
    """Methods for aggregating resource usage data."""

    MEAN = "mean"
    MEDIAN = "median"
    MAX = "max"
    MIN = "min"
    SUM = "sum"
    P90 = "p90"  # 90th percentile
    P95 = "p95"  # 95th percentile
    P99 = "p99"  # 99th percentile


class AggregationPeriod(str, Enum):
    """Time periods for aggregating resource usage data."""

    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


class ResourceDataCollector:
    """Collector for resource usage data."""

    def __init__(
        self,
        storage_capacity: int = 10000,  # Maximum number of data points to store
        default_aggregation_method: AggregationMethod = AggregationMethod.MEAN,
        default_aggregation_period: AggregationPeriod = AggregationPeriod.HOUR,
    ):
        self.storage_capacity = storage_capacity
        self.default_aggregation_method = default_aggregation_method
        self.default_aggregation_period = default_aggregation_period
        self.data_points: Dict[ResourceType, List[UtilizationDataPoint]] = {
            resource_type: [] for resource_type in ResourceType
        }
        self.simulation_data_points: Dict[str, Dict[ResourceType, List[UtilizationDataPoint]]] = {}
        self.node_data_points: Dict[str, Dict[ResourceType, List[UtilizationDataPoint]]] = {}
        self.last_collection_time = datetime.now()
        self.collection_frequency = timedelta(minutes=5)
    
    def record_data_point(
        self,
        resource_type: ResourceType,
        utilization: float,
        capacity: float,
        timestamp: Optional[datetime] = None,
        simulation_id: Optional[str] = None,
        node_id: Optional[str] = None,
    ) -> None:
        """Record a new data point."""
        if timestamp is None:
            timestamp = datetime.now()
        
        data_point = UtilizationDataPoint(
            timestamp=timestamp,
            resource_type=resource_type,
            utilization=utilization,
            capacity=capacity,
            simulation_id=simulation_id,
            node_id=node_id,
        )
        
        # Add to global data points
        self.data_points[resource_type].append(data_point)
        
        # Keep within capacity
        if len(self.data_points[resource_type]) > self.storage_capacity:
            self.data_points[resource_type] = self.data_points[resource_type][-self.storage_capacity:]
        
        # Add to simulation-specific data points if applicable
        if simulation_id:
            if simulation_id not in self.simulation_data_points:
                self.simulation_data_points[simulation_id] = {
                    resource_type: [] for resource_type in ResourceType
                }
            
            self.simulation_data_points[simulation_id][resource_type].append(data_point)
            
            # Keep within capacity
            if len(self.simulation_data_points[simulation_id][resource_type]) > self.storage_capacity:
                self.simulation_data_points[simulation_id][resource_type] = \
                    self.simulation_data_points[simulation_id][resource_type][-self.storage_capacity:]
        
        # Add to node-specific data points if applicable
        if node_id:
            if node_id not in self.node_data_points:
                self.node_data_points[node_id] = {
                    resource_type: [] for resource_type in ResourceType
                }
            
            self.node_data_points[node_id][resource_type].append(data_point)
            
            # Keep within capacity
            if len(self.node_data_points[node_id][resource_type]) > self.storage_capacity:
                self.node_data_points[node_id][resource_type] = \
                    self.node_data_points[node_id][resource_type][-self.storage_capacity:]
    
    def collect_simulation_data(
        self,
        simulation: Simulation,
        collect_time: Optional[datetime] = None,
    ) -> Dict[ResourceType, UtilizationDataPoint]:
        """Collect resource usage data from a simulation."""
        if collect_time is None:
            collect_time = datetime.now()
        
        data_points = {}
        
        # In a real implementation, this would collect actual resource usage
        # Here we'll generate some simulated data
        
        # Calculate simulated resource usage based on simulation properties
        progress = simulation.total_progress()
        total_stages = len(simulation.stages)
        active_stages = sum(1 for stage in simulation.stages.values() 
                           if stage.status.value == "running")
        
        # Adjust usage patterns based on simulation characteristics
        # For demo purposes, we'll use a pattern where CPU usage starts high,
        # then decreases, while memory usage gradually increases
        
        # CPU usage pattern: start high, decrease with progress
        cpu_pattern = 0.3 + (1 - progress) * 0.5
        # Add some noise
        cpu_usage = cpu_pattern + np.random.normal(0, 0.05)
        cpu_usage = max(0.1, min(1.0, cpu_usage))
        
        # Memory usage pattern: start low, increase with progress
        memory_pattern = 0.2 + progress * 0.6
        # Add some noise
        memory_usage = memory_pattern + np.random.normal(0, 0.05)
        memory_usage = max(0.1, min(1.0, memory_usage))
        
        # Storage usage pattern: gradual increase
        storage_pattern = 0.2 + (progress * 0.4)
        # Add some noise
        storage_usage = storage_pattern + np.random.normal(0, 0.02)
        storage_usage = max(0.1, min(1.0, storage_usage))
        
        # Network usage pattern: spikes during certain phases
        network_phase = (progress * 10) % 1  # creates a cyclical pattern
        network_pattern = 0.2 + (0.6 * np.sin(network_phase * 2 * math.pi) ** 2)
        # Add some noise
        network_usage = network_pattern + np.random.normal(0, 0.07)
        network_usage = max(0.1, min(1.0, network_usage))
        
        # Scale based on active stages
        stage_factor = max(1.0, active_stages / max(1, total_stages) * 1.5)
        
        # Record data points
        self.record_data_point(
            resource_type=ResourceType.CPU,
            utilization=cpu_usage * stage_factor,
            capacity=1.0,
            timestamp=collect_time,
            simulation_id=simulation.id,
        )
        data_points[ResourceType.CPU] = UtilizationDataPoint(
            timestamp=collect_time,
            resource_type=ResourceType.CPU,
            utilization=cpu_usage * stage_factor,
            capacity=1.0,
            simulation_id=simulation.id,
        )
        
        self.record_data_point(
            resource_type=ResourceType.MEMORY,
            utilization=memory_usage * stage_factor,
            capacity=1.0,
            timestamp=collect_time,
            simulation_id=simulation.id,
        )
        data_points[ResourceType.MEMORY] = UtilizationDataPoint(
            timestamp=collect_time,
            resource_type=ResourceType.MEMORY,
            utilization=memory_usage * stage_factor,
            capacity=1.0,
            simulation_id=simulation.id,
        )
        
        self.record_data_point(
            resource_type=ResourceType.STORAGE,
            utilization=storage_usage,
            capacity=1.0,
            timestamp=collect_time,
            simulation_id=simulation.id,
        )
        data_points[ResourceType.STORAGE] = UtilizationDataPoint(
            timestamp=collect_time,
            resource_type=ResourceType.STORAGE,
            utilization=storage_usage,
            capacity=1.0,
            simulation_id=simulation.id,
        )
        
        self.record_data_point(
            resource_type=ResourceType.NETWORK,
            utilization=network_usage * stage_factor,
            capacity=1.0,
            timestamp=collect_time,
            simulation_id=simulation.id,
        )
        data_points[ResourceType.NETWORK] = UtilizationDataPoint(
            timestamp=collect_time,
            resource_type=ResourceType.NETWORK,
            utilization=network_usage * stage_factor,
            capacity=1.0,
            simulation_id=simulation.id,
        )
        
        return data_points
    
    def collect_node_data(
        self,
        node_id: str,
        node_metrics: Dict[str, float],
        collect_time: Optional[datetime] = None,
    ) -> Dict[ResourceType, UtilizationDataPoint]:
        """Collect resource usage data from a node."""
        if collect_time is None:
            collect_time = datetime.now()
        
        data_points = {}
        
        # Map node metrics to resource types
        resource_mapping = {
            "cpu_usage": ResourceType.CPU,
            "memory_usage": ResourceType.MEMORY,
            "disk_usage": ResourceType.STORAGE,
            "network_usage": ResourceType.NETWORK,
        }
        
        # Record data points for each resource type
        for metric_name, resource_type in resource_mapping.items():
            if metric_name in node_metrics:
                utilization = node_metrics[metric_name]
                capacity = node_metrics.get(f"{metric_name}_capacity", 1.0)
                
                self.record_data_point(
                    resource_type=resource_type,
                    utilization=utilization,
                    capacity=capacity,
                    timestamp=collect_time,
                    node_id=node_id,
                )
                
                data_points[resource_type] = UtilizationDataPoint(
                    timestamp=collect_time,
                    resource_type=resource_type,
                    utilization=utilization,
                    capacity=capacity,
                    node_id=node_id,
                )
        
        return data_points
    
    def get_resource_history(
        self,
        resource_type: ResourceType,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        simulation_id: Optional[str] = None,
        node_id: Optional[str] = None,
        aggregation_method: Optional[AggregationMethod] = None,
        aggregation_period: Optional[AggregationPeriod] = None,
    ) -> Result[ResourceUtilizationHistory]:
        """Get historical resource usage data."""
        if aggregation_method is None:
            aggregation_method = self.default_aggregation_method
        
        if aggregation_period is None:
            aggregation_period = self.default_aggregation_period
        
        # If specific to a simulation
        if simulation_id:
            if simulation_id not in self.simulation_data_points:
                return Result.err(f"No data found for simulation {simulation_id}")
            
            data_points = self.simulation_data_points[simulation_id][resource_type]
        # If specific to a node
        elif node_id:
            if node_id not in self.node_data_points:
                return Result.err(f"No data found for node {node_id}")
            
            data_points = self.node_data_points[node_id][resource_type]
        # Otherwise, use global data
        else:
            data_points = self.data_points[resource_type]
        
        if not data_points:
            return Result.err(f"No data found for resource type {resource_type}")
        
        # Filter by date range
        if start_date or end_date:
            if not start_date:
                start_date = min(dp.timestamp for dp in data_points)
            if not end_date:
                end_date = max(dp.timestamp for dp in data_points)
            
            data_points = [
                dp for dp in data_points
                if start_date <= dp.timestamp <= end_date
            ]
        else:
            start_date = min(dp.timestamp for dp in data_points)
            end_date = max(dp.timestamp for dp in data_points)
        
        if not data_points:
            return Result.err(f"No data found in the specified date range")
        
        # Apply aggregation if requested
        if aggregation_method != AggregationMethod.SUM and aggregation_period != AggregationPeriod.MINUTE:
            data_points = self._aggregate_data_points(
                data_points, aggregation_method, aggregation_period
            )
        
        # Create resource utilization history
        history = ResourceUtilizationHistory(
            resource_type=resource_type,
            start_date=start_date,
            end_date=end_date,
            data_points=data_points,
            aggregation_period=aggregation_period.value,
        )
        
        return Result.ok(history)
    
    def _aggregate_data_points(
        self,
        data_points: List[UtilizationDataPoint],
        method: AggregationMethod,
        period: AggregationPeriod,
    ) -> List[UtilizationDataPoint]:
        """Aggregate data points by time period."""
        if not data_points:
            return []
        
        # Convert to DataFrame for easier aggregation
        df = pd.DataFrame([
            {
                "timestamp": dp.timestamp,
                "utilization": dp.utilization,
                "capacity": dp.capacity,
                "simulation_id": dp.simulation_id,
                "node_id": dp.node_id,
            }
            for dp in data_points
        ])
        
        # Set timestamp as index
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.set_index("timestamp", inplace=True)
        
        # Define resampling frequency
        freq_map = {
            AggregationPeriod.MINUTE: "T",
            AggregationPeriod.HOUR: "H",
            AggregationPeriod.DAY: "D",
            AggregationPeriod.WEEK: "W",
            AggregationPeriod.MONTH: "M",
        }
        
        freq = freq_map.get(period, "H")
        
        # Define aggregation function
        agg_func = {
            AggregationMethod.MEAN: "mean",
            AggregationMethod.MEDIAN: "median",
            AggregationMethod.MAX: "max",
            AggregationMethod.MIN: "min",
            AggregationMethod.SUM: "sum",
            AggregationMethod.P90: lambda x: x.quantile(0.9),
            AggregationMethod.P95: lambda x: x.quantile(0.95),
            AggregationMethod.P99: lambda x: x.quantile(0.99),
        }.get(method, "mean")
        
        # Apply resampling and aggregation
        aggregated = df.resample(freq).agg({
            "utilization": agg_func,
            "capacity": "mean",
            # For categorical values, use mode (most common value)
            "simulation_id": lambda x: x.mode()[0] if not x.mode().empty else None,
            "node_id": lambda x: x.mode()[0] if not x.mode().empty else None,
        })
        
        # Convert back to UtilizationDataPoint objects
        resource_type = data_points[0].resource_type
        
        return [
            UtilizationDataPoint(
                timestamp=timestamp,
                resource_type=resource_type,
                utilization=row["utilization"],
                capacity=row["capacity"],
                simulation_id=row["simulation_id"],
                node_id=row["node_id"],
            )
            for timestamp, row in aggregated.iterrows()
        ]
    
    def collect_batch_data(
        self,
        simulations: Dict[str, Simulation],
        node_metrics: Dict[str, Dict[str, float]],
    ) -> None:
        """Collect batch data from multiple simulations and nodes."""
        collect_time = datetime.now()
        
        # Check if it's time to collect data
        time_since_last = (collect_time - self.last_collection_time).total_seconds()
        if time_since_last < self.collection_frequency.total_seconds():
            return
        
        # Update last collection time
        self.last_collection_time = collect_time
        
        # Collect simulation data
        for sim_id, simulation in simulations.items():
            if simulation.status.value == "running":
                self.collect_simulation_data(simulation, collect_time)
        
        # Collect node data
        for node_id, metrics in node_metrics.items():
            self.collect_node_data(node_id, metrics, collect_time)


class ResourceUsageAnalyzer:
    """Analyzer for resource usage data."""

    def __init__(self, data_collector: ResourceDataCollector):
        self.data_collector = data_collector
    
    def calculate_utilization_metrics(
        self,
        resource_type: ResourceType,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        simulation_id: Optional[str] = None,
        node_id: Optional[str] = None,
    ) -> Result[Dict[str, float]]:
        """Calculate utilization metrics for a resource type."""
        # Get resource history
        result = self.data_collector.get_resource_history(
            resource_type=resource_type,
            start_date=start_date,
            end_date=end_date,
            simulation_id=simulation_id,
            node_id=node_id,
            aggregation_method=AggregationMethod.MEAN,
            aggregation_period=AggregationPeriod.HOUR,
        )
        
        if not result.success:
            return Result.err(result.error)
        
        history = result.value
        
        if not history.data_points:
            return Result.err("No data points available for analysis")
        
        # Calculate metrics
        utilization_values = [dp.utilization for dp in history.data_points]
        capacity_values = [dp.capacity for dp in history.data_points]
        
        metrics = {
            "mean_utilization": float(np.mean(utilization_values)),
            "median_utilization": float(np.median(utilization_values)),
            "max_utilization": float(np.max(utilization_values)),
            "min_utilization": float(np.min(utilization_values)),
            "std_dev_utilization": float(np.std(utilization_values)),
            "p90_utilization": float(np.percentile(utilization_values, 90)),
            "p95_utilization": float(np.percentile(utilization_values, 95)),
            "p99_utilization": float(np.percentile(utilization_values, 99)),
            "mean_utilization_rate": float(np.mean([u / c for u, c in zip(utilization_values, capacity_values)])),
            "max_utilization_rate": float(np.max([u / c for u, c in zip(utilization_values, capacity_values)])),
        }
        
        return Result.ok(metrics)
    
    def detect_resource_bottlenecks(
        self,
        simulation_id: str,
        threshold: float = 0.8,
    ) -> Result[Dict[ResourceType, float]]:
        """Detect resource bottlenecks for a simulation."""
        bottlenecks = {}
        
        # Check each resource type
        for resource_type in ResourceType:
            # Get recent resource history
            end_date = datetime.now()
            start_date = end_date - timedelta(hours=6)
            
            result = self.data_collector.get_resource_history(
                resource_type=resource_type,
                start_date=start_date,
                end_date=end_date,
                simulation_id=simulation_id,
                aggregation_method=AggregationMethod.P95,
                aggregation_period=AggregationPeriod.HOUR,
            )
            
            if not result.success or not result.value.data_points:
                continue
            
            history = result.value
            
            # Calculate utilization rates
            utilization_rates = [
                dp.utilization / dp.capacity
                for dp in history.data_points
            ]
            
            # Check if P95 utilization rate exceeds threshold
            if utilization_rates:
                p95_rate = np.percentile(utilization_rates, 95)
                if p95_rate > threshold:
                    bottlenecks[resource_type] = float(p95_rate)
        
        return Result.ok(bottlenecks)
    
    def calculate_resource_growth_rate(
        self,
        resource_type: ResourceType,
        simulation_id: str,
        window_days: int = 7,
    ) -> Result[float]:
        """Calculate growth rate for a resource over time."""
        # Get resource history
        end_date = datetime.now()
        start_date = end_date - timedelta(days=window_days)
        
        result = self.data_collector.get_resource_history(
            resource_type=resource_type,
            start_date=start_date,
            end_date=end_date,
            simulation_id=simulation_id,
            aggregation_method=AggregationMethod.MEAN,
            aggregation_period=AggregationPeriod.DAY,
        )
        
        if not result.success:
            return Result.err(result.error)
        
        history = result.value
        
        if len(history.data_points) < 2:
            return Result.err("Insufficient data points for growth rate calculation")
        
        # Sort data points by timestamp
        data_points = sorted(history.data_points, key=lambda dp: dp.timestamp)
        
        # Simple linear regression to calculate growth rate
        x = np.array([(dp.timestamp - data_points[0].timestamp).total_seconds() / 86400
                     for dp in data_points])  # Convert to days
        y = np.array([dp.utilization for dp in data_points])
        
        if len(x) < 2:
            return Result.err("Insufficient data points for growth rate calculation")
        
        # Calculate slope using np.polyfit
        slope, _ = np.polyfit(x, y, 1)
        
        # Growth rate as percentage per day
        growth_rate = slope / np.mean(y) * 100 if np.mean(y) > 0 else 0
        
        return Result.ok(float(growth_rate))
    
    def compare_simulations(
        self,
        simulation_ids: List[str],
        resource_type: ResourceType,
        window_days: int = 7,
    ) -> Result[Dict[str, Dict[str, float]]]:
        """Compare resource usage across multiple simulations."""
        comparison = {}
        
        for sim_id in simulation_ids:
            # Get metrics for this simulation
            result = self.calculate_utilization_metrics(
                resource_type=resource_type,
                start_date=datetime.now() - timedelta(days=window_days),
                simulation_id=sim_id,
            )
            
            if result.success:
                comparison[sim_id] = result.value
        
        if not comparison:
            return Result.err("No valid data available for simulation comparison")
        
        return Result.ok(comparison)