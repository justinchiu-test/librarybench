"""Battery-aware operation modes for MobileSyncDB."""

import time
import logging
import threading
import asyncio
from enum import Enum
from typing import Dict, Any, Optional, List, Set, Callable, Tuple, Union

from .exceptions import BatteryModeError


logger = logging.getLogger(__name__)


class BatteryStatus(Enum):
    """Battery status of a mobile device."""

    FULL = "full"  # Battery is full or device is plugged in
    HIGH = "high"  # Battery level is high (> 70%)
    MEDIUM = "medium"  # Battery level is medium (30-70%)
    LOW = "low"  # Battery level is low (10-30%)
    CRITICAL = "critical"  # Battery level is critical (< 10%)
    UNKNOWN = "unknown"  # Battery status is unknown


class PowerMode(Enum):
    """Power-saving operation modes."""

    PERFORMANCE = "performance"  # Maximum performance, no battery optimizations
    BALANCED = "balanced"  # Balance between performance and battery life
    BATTERY_SAVER = "battery_saver"  # Prioritize battery life over performance
    EXTREME_SAVER = "extreme_saver"  # Maximize battery life, minimum operations
    AUTO = "auto"  # Automatically adjust based on battery status


class BatteryAwareConfig:
    """Configuration for battery-aware operations."""

    def __init__(
        self,
        mode: PowerMode = PowerMode.AUTO,
        sync_interval_seconds: Dict[str, int] = None,
        compression_profile: Dict[str, str] = None,
        max_sync_batch_size: Dict[str, int] = None,
        cache_ttl_seconds: Dict[str, int] = None,
        background_tasks_enabled: Dict[str, bool] = None,
    ):
        """Initialize battery-aware configuration."""
        self.mode = mode
        
        # Default values for different power modes
        self.sync_interval_seconds = sync_interval_seconds or {
            PowerMode.PERFORMANCE.value: 60,  # 1 minute
            PowerMode.BALANCED.value: 300,  # 5 minutes
            PowerMode.BATTERY_SAVER.value: 900,  # 15 minutes
            PowerMode.EXTREME_SAVER.value: 3600,  # 1 hour
        }
        
        self.compression_profile = compression_profile or {
            PowerMode.PERFORMANCE.value: "balanced",
            PowerMode.BALANCED.value: "balanced",
            PowerMode.BATTERY_SAVER.value: "high_compression",
            PowerMode.EXTREME_SAVER.value: "high_compression",
        }
        
        self.max_sync_batch_size = max_sync_batch_size or {
            PowerMode.PERFORMANCE.value: 1000,
            PowerMode.BALANCED.value: 500,
            PowerMode.BATTERY_SAVER.value: 200,
            PowerMode.EXTREME_SAVER.value: 100,
        }
        
        self.cache_ttl_seconds = cache_ttl_seconds or {
            PowerMode.PERFORMANCE.value: 60,  # 1 minute
            PowerMode.BALANCED.value: 300,  # 5 minutes
            PowerMode.BATTERY_SAVER.value: 900,  # 15 minutes
            PowerMode.EXTREME_SAVER.value: 1800,  # 30 minutes
        }
        
        self.background_tasks_enabled = background_tasks_enabled or {
            PowerMode.PERFORMANCE.value: True,
            PowerMode.BALANCED.value: True,
            PowerMode.BATTERY_SAVER.value: False,
            PowerMode.EXTREME_SAVER.value: False,
        }

    def get_sync_interval(self, mode: PowerMode) -> int:
        """Get the sync interval for a power mode."""
        return self.sync_interval_seconds.get(mode.value, self.sync_interval_seconds[PowerMode.BALANCED.value])

    def get_compression_profile(self, mode: PowerMode) -> str:
        """Get the compression profile for a power mode."""
        return self.compression_profile.get(mode.value, self.compression_profile[PowerMode.BALANCED.value])

    def get_max_sync_batch_size(self, mode: PowerMode) -> int:
        """Get the maximum sync batch size for a power mode."""
        return self.max_sync_batch_size.get(mode.value, self.max_sync_batch_size[PowerMode.BALANCED.value])

    def get_cache_ttl(self, mode: PowerMode) -> int:
        """Get the cache TTL for a power mode."""
        return self.cache_ttl_seconds.get(mode.value, self.cache_ttl_seconds[PowerMode.BALANCED.value])

    def are_background_tasks_enabled(self, mode: PowerMode) -> bool:
        """Check if background tasks are enabled for a power mode."""
        return self.background_tasks_enabled.get(mode.value, self.background_tasks_enabled[PowerMode.BALANCED.value])


class BatteryAwareScheduler:
    """Schedules operations based on battery status."""

    def __init__(
        self,
        config: BatteryAwareConfig,
        battery_status_provider: Callable[[], BatteryStatus],
    ):
        """Initialize a battery-aware scheduler."""
        self.config = config
        self.battery_status_provider = battery_status_provider
        self.current_mode = self._determine_power_mode()
        self.deferred_operations: List[Tuple[Callable, Dict[str, Any]]] = []
        self.operation_timers: Dict[str, float] = {}
        self.background_tasks: Dict[str, asyncio.Task] = {}
        self._lock = threading.RLock()
        self._stop_event = threading.Event()

    def _determine_power_mode(self) -> PowerMode:
        """Determine the power mode based on battery status."""
        if self.config.mode != PowerMode.AUTO:
            return self.config.mode
        
        status = self.battery_status_provider()
        
        if status == BatteryStatus.FULL:
            return PowerMode.PERFORMANCE
        elif status == BatteryStatus.HIGH:
            return PowerMode.BALANCED
        elif status == BatteryStatus.MEDIUM:
            return PowerMode.BALANCED
        elif status == BatteryStatus.LOW:
            return PowerMode.BATTERY_SAVER
        elif status == BatteryStatus.CRITICAL:
            return PowerMode.EXTREME_SAVER
        else:
            return PowerMode.BALANCED

    def update_battery_status(self) -> None:
        """Update the current power mode based on battery status."""
        with self._lock:
            old_mode = self.current_mode
            self.current_mode = self._determine_power_mode()
            
            if old_mode != self.current_mode:
                logger.info(f"Power mode changed from {old_mode.value} to {self.current_mode.value}")
                
                # Process any deferred operations that can now run
                self._process_deferred_operations()

    def should_run_operation(self, operation_type: str) -> bool:
        """Determine if an operation should run based on power mode."""
        with self._lock:
            # Check if the operation is throttled
            current_time = time.time()
            last_run = self.operation_timers.get(operation_type, 0)
            
            # Get the throttle interval based on current mode
            interval = self.config.get_sync_interval(self.current_mode)
            
            # Check if enough time has passed since last run
            if current_time - last_run < interval:
                return False
            
            # For extreme power saving, only run critical operations
            if self.current_mode == PowerMode.EXTREME_SAVER:
                # Define critical operations that run even in extreme saver mode
                critical_operations = {"sync", "save", "cleanup"}
                return operation_type in critical_operations
            
            return True

    def record_operation(self, operation_type: str) -> None:
        """Record that an operation was performed."""
        with self._lock:
            self.operation_timers[operation_type] = time.time()

    def defer_operation(
        self,
        operation: Callable,
        args: Dict[str, Any],
        operation_type: str,
    ) -> None:
        """Defer an operation until power conditions improve."""
        with self._lock:
            self.deferred_operations.append((operation, args))
            logger.debug(f"Operation {operation_type} deferred due to power mode {self.current_mode.value}")

    def _process_deferred_operations(self) -> None:
        """Process deferred operations if conditions allow."""
        with self._lock:
            # Only process if we're not in a low power mode
            if self.current_mode in {PowerMode.PERFORMANCE, PowerMode.BALANCED}:
                operations_to_run = self.deferred_operations.copy()
                self.deferred_operations.clear()
                
                # Run the operations outside the lock
                for operation, args in operations_to_run:
                    try:
                        operation(**args)
                    except Exception as e:
                        logger.error(f"Error running deferred operation: {str(e)}")

    def start_background_task(
        self,
        task_id: str,
        coroutine_function: Callable,
        interval_seconds: Optional[int] = None,
    ) -> None:
        """Start a background task if allowed by current power mode."""
        if task_id in self.background_tasks:
            logger.debug(f"Background task {task_id} is already running")
            return
        
        # Check if background tasks are enabled for current mode
        if not self.config.are_background_tasks_enabled(self.current_mode):
            logger.debug(f"Background task {task_id} not started due to power mode {self.current_mode.value}")
            return
        
        # Use the mode-specific interval or the provided one
        if interval_seconds is None:
            interval_seconds = self.config.get_sync_interval(self.current_mode)
        
        # Create the task
        async def task_wrapper():
            while not self._stop_event.is_set():
                try:
                    await coroutine_function()
                except Exception as e:
                    logger.error(f"Error in background task {task_id}: {str(e)}")
                
                # Wait for the interval or until stop is requested
                try:
                    await asyncio.sleep(interval_seconds)
                except asyncio.CancelledError:
                    break
        
        # Get the current event loop or create one
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Start the task
        self.background_tasks[task_id] = loop.create_task(task_wrapper())
        logger.debug(f"Background task {task_id} started with interval {interval_seconds}s")

    def stop_background_task(self, task_id: str) -> None:
        """Stop a background task."""
        if task_id not in self.background_tasks:
            return
        
        # Cancel the task
        self.background_tasks[task_id].cancel()
        del self.background_tasks[task_id]
        logger.debug(f"Background task {task_id} stopped")

    def shutdown(self) -> None:
        """Shutdown the scheduler and stop all background tasks."""
        self._stop_event.set()
        
        # Cancel all tasks
        for task_id in list(self.background_tasks.keys()):
            self.stop_background_task(task_id)


class BatteryAwareOperations:
    """Provides battery-aware operations for the database."""

    def __init__(
        self,
        scheduler: BatteryAwareScheduler,
        compression_profiles: Dict[str, Any],
    ):
        """Initialize battery-aware operations."""
        self.scheduler = scheduler
        self.compression_profiles = compression_profiles
        self.cache: Dict[str, Tuple[Any, float]] = {}

    def get_compression_profile(self) -> str:
        """Get the appropriate compression profile for current power mode."""
        return self.scheduler.config.get_compression_profile(self.scheduler.current_mode)

    def get_sync_batch_size(self) -> int:
        """Get the appropriate sync batch size for current power mode."""
        return self.scheduler.config.get_max_sync_batch_size(self.scheduler.current_mode)

    def get_from_cache(self, key: str) -> Optional[Any]:
        """Get a value from cache, respecting TTL based on power mode."""
        if key not in self.cache:
            return None
        
        value, timestamp = self.cache[key]
        ttl = self.scheduler.config.get_cache_ttl(self.scheduler.current_mode)
        
        if time.time() - timestamp > ttl:
            # Cache entry expired
            del self.cache[key]
            return None
        
        return value

    def store_in_cache(self, key: str, value: Any) -> None:
        """Store a value in cache with current timestamp."""
        self.cache[key] = (value, time.time())

    def clear_cache(self) -> None:
        """Clear all cached values."""
        self.cache.clear()

    def run_or_defer(
        self,
        operation_type: str,
        operation: Callable,
        args: Dict[str, Any],
    ) -> Optional[Any]:
        """Run an operation immediately or defer it based on power mode."""
        if self.scheduler.should_run_operation(operation_type):
            self.scheduler.record_operation(operation_type)
            return operation(**args)
        else:
            self.scheduler.defer_operation(operation, args, operation_type)
            return None

    def schedule_periodic_sync(
        self, 
        sync_function: Callable,
        tables: Optional[List[str]] = None,
    ) -> str:
        """Schedule periodic sync based on power mode."""
        task_id = f"periodic_sync_{id(sync_function)}"
        
        # Create a coroutine wrapper for the sync function
        async def sync_wrapper():
            await sync_function(tables=tables)
        
        # Start the background task
        self.scheduler.start_background_task(task_id, sync_wrapper)
        
        return task_id

    def adjust_for_battery(self, operation_type: str) -> Dict[str, Any]:
        """Get operation parameters adjusted for battery status."""
        mode = self.scheduler.current_mode
        
        # Return appropriate settings for the operation based on power mode
        if operation_type == "sync":
            return {
                "batch_size": self.scheduler.config.get_max_sync_batch_size(mode),
                "compression_profile": self.scheduler.config.get_compression_profile(mode),
                "aggressive_caching": mode in {PowerMode.BATTERY_SAVER, PowerMode.EXTREME_SAVER},
            }
        elif operation_type == "query":
            return {
                "use_cache": True,  # Always use cache for queries
                "cache_ttl": self.scheduler.config.get_cache_ttl(mode),
                "limit_results": mode in {PowerMode.BATTERY_SAVER, PowerMode.EXTREME_SAVER},
                "max_results": 100 if mode == PowerMode.EXTREME_SAVER else 500,
            }
        elif operation_type == "background":
            return {
                "enabled": self.scheduler.config.are_background_tasks_enabled(mode),
                "interval": self.scheduler.config.get_sync_interval(mode),
            }
        else:
            return {}


class MockBatteryProvider:
    """Mock battery status provider for testing."""

    def __init__(self, initial_status: BatteryStatus = BatteryStatus.FULL):
        """Initialize with a specific battery status."""
        self.status = initial_status

    def get_status(self) -> BatteryStatus:
        """Get the current battery status."""
        return self.status

    def set_status(self, status: BatteryStatus) -> None:
        """Set a new battery status."""
        self.status = status