"""Unit tests for battery-aware operations."""

import pytest
import asyncio
import time
import threading
from unittest.mock import Mock, patch
from typing import Dict, Any, List, Callable

from in_memory_database_mobile_app_developer.battery import (
    BatteryStatus, PowerMode, BatteryAwareConfig, BatteryAwareScheduler,
    BatteryAwareOperations, MockBatteryProvider
)


@pytest.fixture
def mock_battery_provider() -> MockBatteryProvider:
    """Create a mock battery provider for testing."""
    return MockBatteryProvider(initial_status=BatteryStatus.FULL)


@pytest.fixture
def battery_config() -> BatteryAwareConfig:
    """Create a battery-aware configuration for testing."""
    return BatteryAwareConfig(mode=PowerMode.AUTO)


@pytest.fixture
def battery_scheduler(mock_battery_provider: MockBatteryProvider, battery_config: BatteryAwareConfig) -> BatteryAwareScheduler:
    """Create a battery-aware scheduler for testing."""
    return BatteryAwareScheduler(
        config=battery_config,
        battery_status_provider=mock_battery_provider.get_status,
    )


@pytest.fixture
def battery_ops(battery_scheduler: BatteryAwareScheduler) -> BatteryAwareOperations:
    """Create battery-aware operations for testing."""
    compression_profiles = {
        "high_compression": {"description": "High compression"},
        "balanced": {"description": "Balanced"},
        "fast": {"description": "Fast"},
    }
    return BatteryAwareOperations(
        scheduler=battery_scheduler,
        compression_profiles=compression_profiles,
    )


def test_battery_status_provider(mock_battery_provider: MockBatteryProvider) -> None:
    """Test the battery status provider."""
    # Check initial status
    assert mock_battery_provider.get_status() == BatteryStatus.FULL
    
    # Change status
    mock_battery_provider.set_status(BatteryStatus.LOW)
    assert mock_battery_provider.get_status() == BatteryStatus.LOW
    
    # Change to another status
    mock_battery_provider.set_status(BatteryStatus.CRITICAL)
    assert mock_battery_provider.get_status() == BatteryStatus.CRITICAL


def test_battery_aware_config() -> None:
    """Test the battery-aware configuration."""
    # Create config with defaults
    config = BatteryAwareConfig()
    
    # Check default values
    assert config.mode == PowerMode.AUTO
    
    # Check sync intervals for different modes
    assert config.get_sync_interval(PowerMode.PERFORMANCE) == 60  # 1 minute
    assert config.get_sync_interval(PowerMode.BALANCED) == 300  # 5 minutes
    assert config.get_sync_interval(PowerMode.BATTERY_SAVER) == 900  # 15 minutes
    assert config.get_sync_interval(PowerMode.EXTREME_SAVER) == 3600  # 1 hour
    
    # Check compression profiles
    assert config.get_compression_profile(PowerMode.PERFORMANCE) == "balanced"
    assert config.get_compression_profile(PowerMode.BATTERY_SAVER) == "high_compression"
    
    # Check batch sizes
    assert config.get_max_sync_batch_size(PowerMode.PERFORMANCE) == 1000
    assert config.get_max_sync_batch_size(PowerMode.EXTREME_SAVER) == 100
    
    # Check cache TTLs
    assert config.get_cache_ttl(PowerMode.PERFORMANCE) == 60
    assert config.get_cache_ttl(PowerMode.EXTREME_SAVER) == 1800
    
    # Check background tasks
    assert config.are_background_tasks_enabled(PowerMode.PERFORMANCE) is True
    assert config.are_background_tasks_enabled(PowerMode.EXTREME_SAVER) is False
    
    # Create config with custom values
    custom_config = BatteryAwareConfig(
        mode=PowerMode.BATTERY_SAVER,
        sync_interval_seconds={
            PowerMode.PERFORMANCE.value: 30,
            PowerMode.BATTERY_SAVER.value: 1800,
        },
        compression_profile={
            PowerMode.PERFORMANCE.value: "fast",
            PowerMode.BATTERY_SAVER.value: "balanced",
        },
    )
    
    # Check custom values
    assert custom_config.mode == PowerMode.BATTERY_SAVER
    assert custom_config.get_sync_interval(PowerMode.PERFORMANCE) == 30
    assert custom_config.get_sync_interval(PowerMode.BATTERY_SAVER) == 1800
    assert custom_config.get_compression_profile(PowerMode.PERFORMANCE) == "fast"
    assert custom_config.get_compression_profile(PowerMode.BATTERY_SAVER) == "balanced"
    
    # Check default values are still used when not overridden
    assert custom_config.get_max_sync_batch_size(PowerMode.PERFORMANCE) == 1000


def test_power_mode_determination(mock_battery_provider: MockBatteryProvider, battery_scheduler: BatteryAwareScheduler) -> None:
    """Test power mode determination based on battery status."""
    # Set explicit mode (non-auto) - should ignore battery status
    battery_scheduler.config.mode = PowerMode.PERFORMANCE
    mock_battery_provider.set_status(BatteryStatus.CRITICAL)
    battery_scheduler.update_battery_status()
    assert battery_scheduler.current_mode == PowerMode.PERFORMANCE
    
    # Set to auto mode - should follow battery status
    battery_scheduler.config.mode = PowerMode.AUTO
    
    # Test different battery levels
    mock_battery_provider.set_status(BatteryStatus.FULL)
    battery_scheduler.update_battery_status()
    assert battery_scheduler.current_mode == PowerMode.PERFORMANCE
    
    mock_battery_provider.set_status(BatteryStatus.HIGH)
    battery_scheduler.update_battery_status()
    assert battery_scheduler.current_mode == PowerMode.BALANCED
    
    mock_battery_provider.set_status(BatteryStatus.MEDIUM)
    battery_scheduler.update_battery_status()
    assert battery_scheduler.current_mode == PowerMode.BALANCED
    
    mock_battery_provider.set_status(BatteryStatus.LOW)
    battery_scheduler.update_battery_status()
    assert battery_scheduler.current_mode == PowerMode.BATTERY_SAVER
    
    mock_battery_provider.set_status(BatteryStatus.CRITICAL)
    battery_scheduler.update_battery_status()
    assert battery_scheduler.current_mode == PowerMode.EXTREME_SAVER
    
    mock_battery_provider.set_status(BatteryStatus.UNKNOWN)
    battery_scheduler.update_battery_status()
    assert battery_scheduler.current_mode == PowerMode.BALANCED  # Default for unknown


def test_operation_throttling(battery_scheduler: BatteryAwareScheduler) -> None:
    """Test throttling operations based on power mode."""
    # Set to performance mode
    battery_scheduler.config.mode = PowerMode.PERFORMANCE
    battery_scheduler.update_battery_status()
    
    # First operation should be allowed
    assert battery_scheduler.should_run_operation("sync") is True
    
    # Record the operation
    battery_scheduler.record_operation("sync")
    
    # Immediate retry should be throttled
    assert battery_scheduler.should_run_operation("sync") is False
    
    # Different operation type should be allowed
    assert battery_scheduler.should_run_operation("query") is True
    
    # Change to extreme saver mode
    battery_scheduler.config.mode = PowerMode.EXTREME_SAVER
    battery_scheduler.update_battery_status()
    
    # Critical operations should still run
    assert battery_scheduler.should_run_operation("sync") is True
    
    # Non-critical operations should be deferred
    assert battery_scheduler.should_run_operation("analytics") is False


def test_deferred_operations(battery_scheduler: BatteryAwareScheduler) -> None:
    """Test deferring and processing operations."""
    # Create a mock operation
    mock_operation = Mock()
    
    # Set to extreme saver mode
    battery_scheduler.config.mode = PowerMode.EXTREME_SAVER
    battery_scheduler.update_battery_status()
    
    # Defer a non-critical operation
    battery_scheduler.defer_operation(
        operation=mock_operation,
        args={"arg1": "value1"},
        operation_type="analytics",
    )
    
    # Check it was added to deferred operations
    assert len(battery_scheduler.deferred_operations) == 1
    
    # Operation should not have been called yet
    mock_operation.assert_not_called()
    
    # Change to performance mode
    battery_scheduler.config.mode = PowerMode.PERFORMANCE
    battery_scheduler.update_battery_status()
    
    # Deferred operations should be processed
    mock_operation.assert_called_once_with(arg1="value1")
    
    # Deferred operations list should be empty
    assert len(battery_scheduler.deferred_operations) == 0


@pytest.mark.asyncio
async def test_background_tasks(battery_scheduler: BatteryAwareScheduler) -> None:
    """Test background task management."""
    # Create a mock coroutine function
    counter = {"count": 0}
    
    async def mock_task():
        counter["count"] += 1
    
    # Set to performance mode (background tasks enabled)
    battery_scheduler.config.mode = PowerMode.PERFORMANCE
    battery_scheduler.update_battery_status()
    
    # Start a background task
    battery_scheduler.start_background_task(
        task_id="test_task",
        coroutine_function=mock_task,
        interval_seconds=0.1,  # Short interval for testing
    )
    
    # Wait for the task to run a few times
    await asyncio.sleep(0.35)  # Should run about 3 times
    
    # Check the task ran
    assert counter["count"] >= 2
    
    # Stop the task
    battery_scheduler.stop_background_task("test_task")
    
    # Remember the count
    count_after_stop = counter["count"]
    
    # Wait to ensure task is stopped
    await asyncio.sleep(0.3)
    
    # Count should not have increased
    assert counter["count"] == count_after_stop
    
    # Clean up
    battery_scheduler.shutdown()


def test_background_tasks_power_mode(battery_scheduler: BatteryAwareScheduler) -> None:
    """Test background tasks behavior with different power modes."""
    # Set to extreme saver mode (background tasks disabled)
    battery_scheduler.config.mode = PowerMode.EXTREME_SAVER
    battery_scheduler.update_battery_status()
    
    # Create a mock coroutine function
    async def mock_task():
        pass
    
    # Try to start a background task
    battery_scheduler.start_background_task(
        task_id="test_task",
        coroutine_function=mock_task,
    )
    
    # Task should not have been started
    assert "test_task" not in battery_scheduler.background_tasks
    
    # Change to performance mode
    battery_scheduler.config.mode = PowerMode.PERFORMANCE
    battery_scheduler.update_battery_status()
    
    # Try to start a background task again
    battery_scheduler.start_background_task(
        task_id="test_task",
        coroutine_function=mock_task,
    )
    
    # Task should have been started
    assert "test_task" in battery_scheduler.background_tasks
    
    # Clean up
    battery_scheduler.shutdown()


def test_cache_handling(battery_ops: BatteryAwareOperations) -> None:
    """Test cache handling based on power mode."""
    # Store an item in cache
    battery_ops.store_in_cache("test_key", "test_value")
    
    # Retrieve it immediately
    assert battery_ops.get_from_cache("test_key") == "test_value"
    
    # Set to performance mode (short TTL)
    battery_ops.scheduler.config.mode = PowerMode.PERFORMANCE
    battery_ops.scheduler.update_battery_status()
    
    # Modify the timestamp to simulate elapsed time
    timestamp = time.time() - 61  # 61 seconds ago (past the 60s TTL)
    battery_ops.cache["test_key"] = ("test_value", timestamp)
    
    # Item should be expired in performance mode
    assert battery_ops.get_from_cache("test_key") is None
    
    # Store again
    battery_ops.store_in_cache("test_key", "test_value")
    
    # Set to extreme saver mode (long TTL)
    battery_ops.scheduler.config.mode = PowerMode.EXTREME_SAVER
    battery_ops.scheduler.update_battery_status()
    
    # Modify the timestamp to simulate elapsed time
    timestamp = time.time() - 1000  # 1000 seconds ago (within the 1800s TTL)
    battery_ops.cache["test_key"] = ("test_value", timestamp)
    
    # Item should still be valid in extreme saver mode
    assert battery_ops.get_from_cache("test_key") == "test_value"
    
    # Clear cache
    battery_ops.clear_cache()
    assert battery_ops.get_from_cache("test_key") is None


def test_run_or_defer(battery_ops: BatteryAwareOperations) -> None:
    """Test run_or_defer behavior."""
    # Create a mock operation
    mock_operation = Mock(return_value="result")
    
    # Set to performance mode
    battery_ops.scheduler.config.mode = PowerMode.PERFORMANCE
    battery_ops.scheduler.update_battery_status()
    
    # Run operation
    result = battery_ops.run_or_defer(
        operation_type="test_op",
        operation=mock_operation,
        args={"arg1": "value1"},
    )
    
    # Operation should have been run
    mock_operation.assert_called_once_with(arg1="value1")
    assert result == "result"
    
    # Record the operation to trigger throttling
    battery_ops.scheduler.record_operation("test_op")
    
    # Reset the mock
    mock_operation.reset_mock()
    
    # Try to run again (should be deferred due to throttling)
    result = battery_ops.run_or_defer(
        operation_type="test_op",
        operation=mock_operation,
        args={"arg1": "value2"},
    )
    
    # Operation should not have been run
    mock_operation.assert_not_called()
    assert result is None
    
    # There should be a deferred operation
    assert len(battery_ops.scheduler.deferred_operations) == 1


def test_battery_aware_parameters(battery_ops: BatteryAwareOperations) -> None:
    """Test getting battery-aware parameters for operations."""
    # Test in performance mode
    battery_ops.scheduler.config.mode = PowerMode.PERFORMANCE
    battery_ops.scheduler.update_battery_status()
    
    # Get sync parameters
    sync_params = battery_ops.adjust_for_battery("sync")
    assert sync_params["batch_size"] == 1000
    assert sync_params["compression_profile"] == "balanced"
    assert sync_params["aggressive_caching"] is False
    
    # Get query parameters
    query_params = battery_ops.adjust_for_battery("query")
    assert query_params["use_cache"] is True
    assert query_params["limit_results"] is False
    
    # Test in extreme saver mode
    battery_ops.scheduler.config.mode = PowerMode.EXTREME_SAVER
    battery_ops.scheduler.update_battery_status()
    
    # Get sync parameters
    sync_params = battery_ops.adjust_for_battery("sync")
    assert sync_params["batch_size"] == 100
    assert sync_params["compression_profile"] == "high_compression"
    assert sync_params["aggressive_caching"] is True
    
    # Get query parameters
    query_params = battery_ops.adjust_for_battery("query")
    assert query_params["use_cache"] is True
    assert query_params["limit_results"] is True
    assert query_params["max_results"] == 100
    
    # Get background parameters
    bg_params = battery_ops.adjust_for_battery("background")
    assert bg_params["enabled"] is False
    assert bg_params["interval"] == 3600