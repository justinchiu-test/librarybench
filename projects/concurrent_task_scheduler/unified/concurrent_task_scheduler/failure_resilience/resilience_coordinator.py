"""Resilience coordinator for managing failures and recovery."""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime, timedelta
from enum import Enum
from threading import Lock
from typing import Dict, List, Optional, Set, Tuple, Union, Any, Callable

from common.core.models import (
    BaseJob,
    BaseNode,
    Result,
)
from common.failure_resilience.failure_detector import (
    FailureEvent as CommonFailureEvent,
    FailureLevel,
    FailureType as CommonFailureType,
)
from common.failure_resilience.resilience_coordinator import (
    RecoveryAction,
    RecoveryPlan,
    RecoveryStrategy as CommonRecoveryStrategy,
    ResilienceCoordinator as CommonResilienceCoordinator,
)

from concurrent_task_scheduler.failure_resilience.checkpoint_manager import (
    CheckpointCoordinator,
    CheckpointManager,
    CheckpointCreationStrategy,
)
from concurrent_task_scheduler.failure_resilience.failure_detector import (
    DetectionMethod,
    FailureDetector,
    FailureRecoveryManager,
    FailureReport,
    FailureSeverity,
    FailureType,
    RecoveryStrategy,
    map_failure_type_to_common,
    map_severity_to_common,
)
from concurrent_task_scheduler.models import (
    Checkpoint,
    CheckpointType,
    ComputeNode,
    NodeStatus,
    Result,
    Simulation,
    SimulationStage,
    SimulationStageStatus,
    SystemEvent,
)
from concurrent_task_scheduler.models.utils import generate_id

logger = logging.getLogger(__name__)


class ResilienceLevel(str, Enum):
    """Resilience levels for the system."""

    MINIMAL = "minimal"  # Basic resilience
    STANDARD = "standard"  # Standard resilience
    HIGH = "high"  # High resilience
    MAXIMUM = "maximum"  # Maximum resilience


class RestartMode(str, Enum):
    """Modes for restarting simulations."""

    FULL = "full"  # Restart the entire simulation
    PARTIAL = "partial"  # Restart only failed stages
    INCREMENTAL = "incremental"  # Restart from last checkpoint
    SOFT = "soft"  # Soft restart (try to keep state)
    HARD = "hard"  # Hard restart (discard all state)


# Define mapping from domain-specific recovery strategies to common ones
def map_recovery_strategy_to_common(strategy: RecoveryStrategy) -> RecoveryAction:
    """Map domain-specific recovery strategy to common recovery action."""
    mapping = {
        RecoveryStrategy.RESTART: RecoveryAction.RESTART_JOB,
        RecoveryStrategy.RESTORE_CHECKPOINT: RecoveryAction.RESTORE_CHECKPOINT,
        RecoveryStrategy.MIGRATE: RecoveryAction.RESCHEDULE,
        RecoveryStrategy.PARTIAL_RESTART: RecoveryAction.RETRY,
        RecoveryStrategy.RECONFIGURE: RecoveryAction.RETRY,
        RecoveryStrategy.ROLLBACK: RecoveryAction.RESTORE_CHECKPOINT,
        RecoveryStrategy.IGNORE: RecoveryAction.SKIP,
    }
    return mapping.get(strategy, RecoveryAction.MANUAL)


def map_common_recovery_action_to_strategy(action: RecoveryAction) -> RecoveryStrategy:
    """Map common recovery action to domain-specific recovery strategy."""
    mapping = {
        RecoveryAction.RESTART_JOB: RecoveryStrategy.RESTART,
        RecoveryAction.RESTORE_CHECKPOINT: RecoveryStrategy.RESTORE_CHECKPOINT,
        RecoveryAction.RESCHEDULE: RecoveryStrategy.MIGRATE,
        RecoveryAction.PREEMPT: RecoveryStrategy.RESTART,
        RecoveryAction.RETRY: RecoveryStrategy.PARTIAL_RESTART,
        RecoveryAction.SKIP: RecoveryStrategy.IGNORE,
        RecoveryAction.ABORT: RecoveryStrategy.RESTART,
        RecoveryAction.MANUAL: RecoveryStrategy.RESTORE_CHECKPOINT,
    }
    return mapping.get(action, RecoveryStrategy.RESTORE_CHECKPOINT)


class ResilienceEvent:
    """An event related to system resilience."""

    def __init__(
        self,
        event_id: str,
        event_type: str,
        timestamp: datetime,
        description: str,
        severity: str,
        source: str,
        details: Optional[Dict] = None,
    ):
        self.id = event_id
        self.event_type = event_type
        self.timestamp = timestamp
        self.description = description
        self.severity = severity
        self.source = source
        self.details = details or {}
        self.related_events: List[str] = []
        self.handled = False
        self.handling_time: Optional[datetime] = None
        self.handler: Optional[str] = None
    
    def mark_handled(self, handler: str) -> None:
        """Mark the event as handled."""
        self.handled = True
        self.handling_time = datetime.now()
        self.handler = handler
    
    def add_related_event(self, event_id: str) -> None:
        """Add a related event."""
        if event_id not in self.related_events:
            self.related_events.append(event_id)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "description": self.description,
            "severity": self.severity,
            "source": self.source,
            "details": self.details,
            "related_events": self.related_events,
            "handled": self.handled,
            "handling_time": self.handling_time.isoformat() if self.handling_time else None,
            "handler": self.handler,
        }


class ResilienceMetrics:
    """Metrics for system resilience."""

    def __init__(self):
        self.total_failures = 0
        self.resolved_failures = 0
        self.checkpoint_operations = 0
        self.successful_recoveries = 0
        self.failed_recoveries = 0
        self.mean_time_to_detection = 0.0  # seconds
        self.mean_time_to_recovery = 0.0  # seconds
        self.recovery_success_rate = 0.0
        self.checkpoint_creation_time = 0.0  # seconds
        self.checkpoint_restore_time = 0.0  # seconds
        self.node_failure_rate = 0.0  # failures per hour
        self.simulation_failure_rate = 0.0  # failures per hour
        self.total_downtime = 0.0  # seconds
        
        # Time window metrics
        self.start_time = datetime.now()
        self.failures_in_window: List[datetime] = []
        self.window_size = timedelta(hours=24)
    
    def record_failure(self, detection_time: Optional[datetime] = None) -> None:
        """Record a failure."""
        self.total_failures += 1
        
        if detection_time:
            self.failures_in_window.append(detection_time)
        else:
            self.failures_in_window.append(datetime.now())
        
        # Clean up old entries
        self._clean_up_window()
    
    def record_resolution(self, detection_time: datetime, resolution_time: datetime) -> None:
        """Record a failure resolution."""
        self.resolved_failures += 1
        
        # Update mean time to recovery
        time_to_recovery = (resolution_time - detection_time).total_seconds()
        
        if self.resolved_failures == 1:
            self.mean_time_to_recovery = time_to_recovery
        else:
            self.mean_time_to_recovery = (
                (self.mean_time_to_recovery * (self.resolved_failures - 1) + time_to_recovery) /
                self.resolved_failures
            )
        
        # Update recovery success rate
        total_recovery_attempts = self.successful_recoveries + self.failed_recoveries
        if total_recovery_attempts > 0:
            self.recovery_success_rate = self.successful_recoveries / total_recovery_attempts
    
    def record_checkpoint_operation(self, duration_seconds: float) -> None:
        """Record a checkpoint operation."""
        self.checkpoint_operations += 1
        
        # Update mean checkpoint creation time
        if self.checkpoint_operations == 1:
            self.checkpoint_creation_time = duration_seconds
        else:
            self.checkpoint_creation_time = (
                (self.checkpoint_creation_time * (self.checkpoint_operations - 1) + duration_seconds) /
                self.checkpoint_operations
            )
    
    def record_recovery_attempt(self, success: bool, duration_seconds: float) -> None:
        """Record a recovery attempt."""
        if success:
            self.successful_recoveries += 1
        else:
            self.failed_recoveries += 1
        
        # Update recovery success rate
        total_recovery_attempts = self.successful_recoveries + self.failed_recoveries
        if total_recovery_attempts > 0:
            self.recovery_success_rate = self.successful_recoveries / total_recovery_attempts
        
        # Update checkpoint restore time if successful
        if success:
            if self.successful_recoveries == 1:
                self.checkpoint_restore_time = duration_seconds
            else:
                self.checkpoint_restore_time = (
                    (self.checkpoint_restore_time * (self.successful_recoveries - 1) + duration_seconds) /
                    self.successful_recoveries
                )
    
    def record_downtime(self, downtime_seconds: float) -> None:
        """Record system downtime."""
        self.total_downtime += downtime_seconds
    
    def calculate_failure_rate(self) -> float:
        """Calculate the current failure rate (failures per hour)."""
        self._clean_up_window()
        
        hours = (datetime.now() - self.start_time).total_seconds() / 3600
        if hours < 0.1:  # Less than 6 minutes
            return 0.0
        
        return len(self.failures_in_window) / hours
    
    def _clean_up_window(self) -> None:
        """Clean up entries outside the time window."""
        now = datetime.now()
        window_start = now - self.window_size
        
        self.failures_in_window = [
            t for t in self.failures_in_window
            if t >= window_start
        ]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "total_failures": self.total_failures,
            "resolved_failures": self.resolved_failures,
            "checkpoint_operations": self.checkpoint_operations,
            "successful_recoveries": self.successful_recoveries,
            "failed_recoveries": self.failed_recoveries,
            "mean_time_to_detection": self.mean_time_to_detection,
            "mean_time_to_recovery": self.mean_time_to_recovery,
            "recovery_success_rate": self.recovery_success_rate,
            "checkpoint_creation_time": self.checkpoint_creation_time,
            "checkpoint_restore_time": self.checkpoint_restore_time,
            "node_failure_rate": self.node_failure_rate,
            "simulation_failure_rate": self.simulation_failure_rate,
            "total_downtime": self.total_downtime,
            "failures_last_24h": len(self.failures_in_window),
            "current_failure_rate": self.calculate_failure_rate(),
        }


class ResilienceCoordinator(CommonResilienceCoordinator):
    """Coordinator for failure resilience and recovery."""

    def __init__(
        self,
        checkpoint_manager: CheckpointManager,
        failure_detector: FailureDetector,
        checkpoint_base_path: str = "/tmp/checkpoints",
        resilience_level: ResilienceLevel = ResilienceLevel.STANDARD,
    ):
        # Initialize the common implementation
        super().__init__(
            checkpoint_manager=checkpoint_manager,
            failure_detector=failure_detector,
        )
        
        # Initialize domain-specific components
        self.recovery_manager = FailureRecoveryManager(failure_detector)
        self.checkpoint_coordinator = CheckpointCoordinator(checkpoint_manager)
        self.checkpoint_base_path = checkpoint_base_path
        self.resilience_level = resilience_level
        self.events: Dict[str, ResilienceEvent] = {}
        self.metrics = ResilienceMetrics()
        self.active_recoveries: Dict[str, Dict] = {}  # simulation_id -> recovery_info
        self.checkpoint_schedule: Dict[str, datetime] = {}  # simulation_id -> next_checkpoint_time
        self.simulation_status_history: Dict[str, List[Tuple[datetime, str]]] = {}
        self.node_status_history: Dict[str, List[Tuple[datetime, str]]] = {}
        
        # Configuration based on resilience level
        self.checkpoint_configs = {
            ResilienceLevel.MINIMAL: {
                "frequency_minutes": 120,  # 2 hours
                "strategy": CheckpointCreationStrategy.PERIODIC,
            },
            ResilienceLevel.STANDARD: {
                "frequency_minutes": 60,  # 1 hour
                "strategy": CheckpointCreationStrategy.HYBRID,
            },
            ResilienceLevel.HIGH: {
                "frequency_minutes": 30,  # 30 minutes
                "strategy": CheckpointCreationStrategy.HYBRID,
            },
            ResilienceLevel.MAXIMUM: {
                "frequency_minutes": 15,  # 15 minutes
                "strategy": CheckpointCreationStrategy.HYBRID,
            },
        }
        
        # Set checkpoint frequency based on resilience level
        self.checkpoint_frequency = timedelta(
            minutes=self.checkpoint_configs[resilience_level]["frequency_minutes"]
        )
        
        # Register the recovery executor
        self.set_recovery_executor(self._execute_recovery_plan)
    
    def _execute_recovery_plan(self, plan: RecoveryPlan) -> Result[bool]:
        """Execute a recovery plan for the common implementation."""
        # Map the common recovery action to a domain-specific strategy
        strategy = map_common_recovery_action_to_strategy(plan.action)
        
        # Get the failure report from our detector
        failure_id = plan.failure_event.id
        domain_failures = [
            f for f in self.failure_detector.failure_reports.values()
            if f.id == failure_id or failure_id.endswith(f.id)
        ]
        
        if not domain_failures:
            # This might be a failure detected by the common implementation
            # Create a domain-specific failure report
            domain_failure = FailureReport(
                id=failure_id,
                failure_type=FailureType.UNKNOWN,  # Default if we can't determine
                severity=FailureSeverity.MEDIUM,
                detection_time=plan.failure_event.timestamp,
                detection_method=DetectionMethod.SYSTEM_REPORT,
                node_id=plan.node_id,
                simulation_id=plan.job_id,
                description=plan.failure_event.description,
                details=plan.failure_event.details,
            )
            
            # Add to our tracking
            self.failure_detector.record_failure(domain_failure)
        else:
            domain_failure = domain_failures[0]
        
        # Initiate recovery using our domain-specific approach
        if domain_failure.simulation_id:
            recovery_info = self._initiate_simulation_recovery(
                domain_failure.simulation_id,
                f"Failure recovery for {failure_id}",
                strategy,
                failure_id
            )
            
            if not recovery_info:
                return Result.err(f"Failed to initiate recovery for {failure_id}")
            
            # Mark as successful for now (the actual recovery is async)
            # In a real implementation, we'd track this and update when done
            return Result.ok(True)
        
        return Result.err(f"Cannot recover from failure {failure_id}: no simulation ID")
    
    def set_resilience_level(self, level: ResilienceLevel) -> None:
        """Set the resilience level."""
        self.resilience_level = level
        
        # Update checkpoint frequency
        self.checkpoint_frequency = timedelta(
            minutes=self.checkpoint_configs[level]["frequency_minutes"]
        )
    
    def record_event(
        self,
        event_type: str,
        description: str,
        severity: str,
        source: str,
        details: Optional[Dict] = None,
    ) -> str:
        """Record a resilience event."""
        event_id = generate_id("event")
        
        event = ResilienceEvent(
            event_id=event_id,
            event_type=event_type,
            timestamp=datetime.now(),
            description=description,
            severity=severity,
            source=source,
            details=details,
        )
        
        self.events[event_id] = event
        return event_id
    
    def schedule_checkpoint(
        self,
        simulation: Simulation,
        delay_minutes: Optional[int] = None,
    ) -> None:
        """Schedule a checkpoint for a simulation."""
        if delay_minutes is None:
            # Use default frequency from resilience level
            delay_minutes = self.checkpoint_configs[self.resilience_level]["frequency_minutes"]
        
        # Calculate next checkpoint time
        next_checkpoint = datetime.now() + timedelta(minutes=delay_minutes)
        
        # Update schedule
        self.checkpoint_schedule[simulation.id] = next_checkpoint
        
        # Also schedule in checkpoint coordinator
        self.checkpoint_coordinator.schedule_checkpoint(
            simulation.id,
            next_checkpoint,
        )
    
    def process_scheduled_checkpoints(
        self,
        simulations: Dict[str, Simulation],
    ) -> List[str]:
        """Process scheduled checkpoints."""
        # Let the checkpoint coordinator handle it
        return self.checkpoint_coordinator.process_scheduled_checkpoints(simulations)
    
    def handle_node_status_change(
        self,
        node_id: str,
        old_status: NodeStatus,
        new_status: NodeStatus,
        affected_simulations: List[str],
    ) -> List[str]:
        """Handle a node status change."""
        # Record in history
        if node_id not in self.node_status_history:
            self.node_status_history[node_id] = []
        
        self.node_status_history[node_id].append((datetime.now(), new_status.value))
        
        # Record event
        event_id = self.record_event(
            event_type="node_status_change",
            description=f"Node {node_id} changed status from {old_status.value} to {new_status.value}",
            severity="warning" if new_status in [NodeStatus.OFFLINE, NodeStatus.MAINTENANCE] else "info",
            source="node_monitor",
            details={
                "node_id": node_id,
                "old_status": old_status.value,
                "new_status": new_status.value,
                "affected_simulations": affected_simulations,
            },
        )
        
        # If node went offline, check for failures
        if new_status == NodeStatus.OFFLINE and old_status == NodeStatus.ONLINE:
            # Report node failure
            failure = self.failure_detector.report_failure(
                failure_type=FailureType.NODE_OFFLINE,
                severity=FailureSeverity.HIGH,
                description=f"Node {node_id} went offline unexpectedly",
                node_id=node_id,
            )
            
            # Record metrics
            self.metrics.record_failure(failure.detection_time)
            
            # Link events
            event = self.events[event_id]
            event.add_related_event(failure.id)
            
            # Also report to common implementation
            common_failure_type = map_failure_type_to_common(failure.failure_type)
            common_failure_level = map_severity_to_common(failure.severity)
            
            common_event = CommonFailureEvent(
                failure_id=failure.id,
                failure_type=common_failure_type,
                level=common_failure_level,
                node_id=node_id,
                description=failure.description,
                details=failure.details,
                timestamp=failure.detection_time,
            )
            
            # Add to common implementation's tracking
            self._add_failure_to_common(common_event)
        
        affected_handled = []
        
        # Handle affected simulations
        for sim_id in affected_simulations:
            # If node went offline and sim was running, need recovery
            if new_status == NodeStatus.OFFLINE and old_status == NodeStatus.ONLINE:
                # Check if already recovering
                if sim_id in self.active_recoveries:
                    continue
                
                # Start recovery process
                recovery_info = self._initiate_simulation_recovery(
                    sim_id,
                    f"Node {node_id} failure",
                    RecoveryStrategy.RESTORE_CHECKPOINT,
                    event_id,
                )
                
                if recovery_info:
                    affected_handled.append(sim_id)
        
        return affected_handled
    
    def _add_failure_to_common(self, common_event: CommonFailureEvent) -> None:
        """Add a failure event to the common implementation's tracking."""
        # Check if the failure detector has a function to handle this
        if hasattr(self.failure_detector, 'add_failure_event'):
            self.failure_detector.add_failure_event(common_event)
        else:
            # Fallback if the method doesn't exist
            self.failure_detector.failure_history.append(common_event)
            self.failure_detector.active_failures[common_event.id] = common_event
    
    def handle_simulation_status_change(
        self,
        simulation: Simulation,
        old_status: str,
        new_status: str,
    ) -> Optional[str]:
        """Handle a simulation status change."""
        # Record in history
        if simulation.id not in self.simulation_status_history:
            self.simulation_status_history[simulation.id] = []
        
        self.simulation_status_history[simulation.id].append((datetime.now(), new_status))
        
        # Record event
        event_id = self.record_event(
            event_type="simulation_status_change",
            description=f"Simulation {simulation.id} ({simulation.name}) changed status from {old_status} to {new_status}",
            severity="warning" if new_status == "failed" else "info",
            source="simulation_monitor",
            details={
                "simulation_id": simulation.id,
                "simulation_name": simulation.name,
                "old_status": old_status,
                "new_status": new_status,
            },
        )
        
        # If simulation failed, check for recovery options
        if new_status == "failed" and old_status in ["running", "paused"]:
            # Report simulation failure
            failure = self.failure_detector.report_failure(
                failure_type=FailureType.PROCESS_CRASH,
                severity=FailureSeverity.HIGH,
                description=f"Simulation {simulation.id} ({simulation.name}) failed unexpectedly",
                simulation_id=simulation.id,
            )
            
            # Record metrics
            self.metrics.record_failure(failure.detection_time)
            
            # Link events
            event = self.events[event_id]
            event.add_related_event(failure.id)
            
            # Report to common implementation
            common_event = failure.to_common_event()
            self._add_failure_to_common(common_event)
            
            # Check if already recovering
            if simulation.id in self.active_recoveries:
                return None
            
            # Start recovery process
            recovery_info = self._initiate_simulation_recovery(
                simulation.id,
                f"Simulation failure",
                RecoveryStrategy.RESTORE_CHECKPOINT,
                event_id,
            )
            
            if recovery_info:
                return recovery_info.get("recovery_id")
        
        # If simulation started running, schedule checkpoints
        elif new_status == "running" and old_status in ["scheduled", "paused"]:
            # Schedule next checkpoint
            self.schedule_checkpoint(simulation)
            
            # Also create an immediate checkpoint for resilience level high or maximum
            if self.resilience_level in [ResilienceLevel.HIGH, ResilienceLevel.MAXIMUM]:
                # Schedule quick initial checkpoint
                self.schedule_checkpoint(simulation, delay_minutes=5)
        
        return None
    
    def handle_stage_status_change(
        self,
        simulation: Simulation,
        stage_id: str,
        old_status: SimulationStageStatus,
        new_status: SimulationStageStatus,
    ) -> Optional[str]:
        """Handle a simulation stage status change."""
        stage = simulation.stages.get(stage_id)
        if not stage:
            return None
        
        # Record event
        event_id = self.record_event(
            event_type="stage_status_change",
            description=f"Stage {stage_id} ({stage.name}) in simulation {simulation.id} changed status from {old_status.value} to {new_status.value}",
            severity="warning" if new_status == SimulationStageStatus.FAILED else "info",
            source="simulation_monitor",
            details={
                "simulation_id": simulation.id,
                "simulation_name": simulation.name,
                "stage_id": stage_id,
                "stage_name": stage.name,
                "old_status": old_status.value,
                "new_status": new_status.value,
            },
        )
        
        # If stage completed, consider creating a checkpoint
        if new_status == SimulationStageStatus.COMPLETED:
            if self.resilience_level in [ResilienceLevel.HIGH, ResilienceLevel.MAXIMUM]:
                # Create checkpoint after stage completion for high resilience levels
                self.checkpoint_coordinator.schedule_checkpoint(simulation.id)
        
        # If stage failed, check for recovery options
        elif new_status == SimulationStageStatus.FAILED:
            # Report stage failure
            failure = self.failure_detector.report_failure(
                failure_type=FailureType.PROCESS_CRASH,
                severity=FailureSeverity.MEDIUM,
                description=f"Stage {stage_id} ({stage.name}) in simulation {simulation.id} failed",
                simulation_id=simulation.id,
                stage_id=stage_id,
            )
            
            # Record metrics
            self.metrics.record_failure(failure.detection_time)
            
            # Link events
            event = self.events[event_id]
            event.add_related_event(failure.id)
            
            # Report to common implementation
            common_event = failure.to_common_event()
            self._add_failure_to_common(common_event)
            
            # Check if already recovering
            if simulation.id in self.active_recoveries:
                return None
            
            # For partial stage failure, try PARTIAL_RESTART strategy
            recovery_info = self._initiate_simulation_recovery(
                simulation.id,
                f"Stage failure",
                RecoveryStrategy.PARTIAL_RESTART,
                event_id,
            )
            
            if recovery_info:
                return recovery_info.get("recovery_id")
        
        return None
    
    def register_failure(
        self,
        node_id: str,
        affected_simulations: List[str],
        failure_time: datetime = None,
    ) -> Result[bool]:
        """Register a node failure."""
        if failure_time is None:
            failure_time = datetime.now()
            
        # Create a failure report
        failure = FailureReport(
            id=generate_id("failure"),
            failure_type=FailureType.NODE_OFFLINE,
            severity=FailureSeverity.HIGH,
            description=f"Node {node_id} failure affecting {len(affected_simulations)} simulations",
            detection_time=failure_time,
            detection_method=DetectionMethod.MANUAL,  # Using MANUAL as EXTERNAL is not defined
            node_id=node_id,
            simulation_id=affected_simulations[0] if affected_simulations else None,
        )
        
        # Record the failure with the failure detector
        self.failure_detector.record_failure(failure)
        
        # Record metrics
        self.metrics.record_failure(failure.detection_time)
        
        # Report to common implementation
        common_event = failure.to_common_event()
        self._add_failure_to_common(common_event)
        
        # Handle the failure
        self.handle_failure_detection(failure)
        
        return Result.ok(True)
    
    def handle_failure_detection(self, failure: FailureReport) -> Optional[str]:
        """Handle a detected failure."""
        # Record event
        event_id = self.record_event(
            event_type="failure_detected",
            description=failure.description,
            severity="critical" if failure.severity == FailureSeverity.CRITICAL else 
                     "error" if failure.severity == FailureSeverity.HIGH else 
                     "warning" if failure.severity == FailureSeverity.MEDIUM else "info",
            source="failure_detector",
            details={
                "failure_id": failure.id,
                "failure_type": failure.failure_type.value,
                "severity": failure.severity.value,
                "detection_method": failure.detection_method.value,
                "node_id": failure.node_id,
                "simulation_id": failure.simulation_id,
                "stage_id": failure.stage_id,
            },
        )
        
        # Record metrics
        self.metrics.record_failure(failure.detection_time)
        
        # Add to common implementation if not already there
        common_event = failure.to_common_event()
        self._add_failure_to_common(common_event)
        
        # If simulation affected, initiate recovery
        if failure.simulation_id:
            # Check if already recovering
            if failure.simulation_id in self.active_recoveries:
                # Link the event to the existing recovery
                recovery_info = self.active_recoveries[failure.simulation_id]
                if "events" in recovery_info:
                    recovery_info["events"].append(event_id)
                
                return None
            
            # Determine recovery strategy based on failure type
            strategy = None
            if failure.failure_type == FailureType.NODE_OFFLINE:
                strategy = RecoveryStrategy.MIGRATE
            elif failure.failure_type == FailureType.PROCESS_CRASH:
                strategy = RecoveryStrategy.RESTORE_CHECKPOINT
            elif failure.failure_type == FailureType.MEMORY_EXHAUSTION:
                strategy = RecoveryStrategy.RECONFIGURE
            elif failure.failure_type == FailureType.DEADLOCK:
                strategy = RecoveryStrategy.RESTART
            else:
                # Use recovery manager to determine best strategy
                result = self.recovery_manager.initiate_recovery(failure.id)
                if result.success:
                    strategy = result.value
            
            if strategy:
                recovery_info = self._initiate_simulation_recovery(
                    failure.simulation_id,
                    f"Failure recovery",
                    strategy,
                    event_id,
                )
                
                if recovery_info:
                    return recovery_info.get("recovery_id")
        
        return None
    
    def _initiate_simulation_recovery(
        self,
        simulation_id: str,
        reason: str,
        strategy: RecoveryStrategy,
        event_id: Optional[str] = None,
    ) -> Optional[Dict]:
        """Initiate recovery for a simulation."""
        # Generate recovery ID
        recovery_id = generate_id("recovery")
        
        # Create recovery info
        recovery_info = {
            "recovery_id": recovery_id,
            "simulation_id": simulation_id,
            "strategy": strategy.value,
            "reason": reason,
            "initiated_at": datetime.now().isoformat(),
            "completed": False,
            "events": [event_id] if event_id else [],
        }
        
        # Add to active recoveries
        self.active_recoveries[simulation_id] = recovery_info
        
        # Record event
        recovery_event_id = self.record_event(
            event_type="recovery_initiated",
            description=f"Recovery initiated for simulation {simulation_id} using strategy {strategy.value}",
            severity="info",
            source="resilience_coordinator",
            details={
                "recovery_id": recovery_id,
                "simulation_id": simulation_id,
                "strategy": strategy.value,
                "reason": reason,
            },
        )
        
        if event_id:
            # Link events
            event = self.events.get(event_id)
            if event:
                event.add_related_event(recovery_event_id)
        
        # Create a recovery plan for the common implementation
        if self.recovery_executor:
            # Find the associated failure event
            failure_events = [f for f in self.failure_detector.failure_reports.values() 
                            if f.simulation_id == simulation_id and not f.resolved]
            
            if failure_events:
                failure = failure_events[0]
                common_event = failure.to_common_event()
                
                # Check if it's in the common implementation
                found = False
                for common_failure in self.failure_detector.active_failures.values():
                    if common_failure.id == common_event.id or common_failure.job_id == simulation_id:
                        found = True
                        common_event = common_failure
                        break
                
                if not found:
                    # Add to common implementation
                    self._add_failure_to_common(common_event)
                
                # Create a recovery strategy for the common implementation
                common_action = map_recovery_strategy_to_common(strategy)
                common_strategy = CommonRecoveryStrategy(
                    failure_type=common_event.failure_type,
                    action=common_action,
                    description=reason,
                )
                
                # Find latest checkpoint if needed
                checkpoint_id = None
                if strategy == RecoveryStrategy.RESTORE_CHECKPOINT:
                    checkpoint = self.checkpoint_manager.get_latest_checkpoint(simulation_id)
                    if checkpoint:
                        checkpoint_id = checkpoint.id
                
                # Create recovery plan
                common_plan = common_strategy.create_plan(
                    failure_event=common_event,
                    checkpoint_id=checkpoint_id,
                )
                
                # Execute plan
                try:
                    self.execute_recovery_plan(common_plan.id)
                except Exception as e:
                    logger.error(f"Failed to execute common recovery plan: {e}")
        
        return recovery_info
    
    def restore_simulation(
        self,
        simulation_id: str,
        checkpoint_id: str,
    ) -> Result[bool]:
        """Restore a simulation from a checkpoint."""
        # Get the latest checkpoint if ID not provided
        if not checkpoint_id:
            # Try to get latest checkpoint
            latest_checkpoint = self.checkpoint_manager.get_latest_checkpoint(simulation_id)
            if not latest_checkpoint:
                return Result.err(f"No checkpoints found for simulation {simulation_id}")
            checkpoint_id = latest_checkpoint.id
        
        # Restore from checkpoint
        result = self.checkpoint_manager.restore_from_checkpoint(checkpoint_id, simulation_id)
        if not result.success:
            return Result.err(f"Failed to restore from checkpoint: {result.error}")
        
        # Create a recovery ID for tracking
        recovery_id = generate_id("recovery")
        
        # Record the recovery event
        event_id = self.record_event(
            event_type="simulation_restored",
            description=f"Simulation {simulation_id} restored from checkpoint {checkpoint_id}",
            severity="info",
            source="resilience_coordinator",
            details={
                "simulation_id": simulation_id,
                "checkpoint_id": checkpoint_id,
                "recovery_id": recovery_id,
            },
        )
        
        return Result.ok(True)
    
    def complete_recovery(
        self,
        recovery_id: str,
        success: bool,
        details: Optional[Dict] = None,
    ) -> Result[bool]:
        """Mark a recovery as complete."""
        # Find recovery
        for sim_id, recovery_info in self.active_recoveries.items():
            if recovery_info.get("recovery_id") == recovery_id:
                # Update recovery info
                recovery_info["completed"] = True
                recovery_info["completed_at"] = datetime.now().isoformat()
                recovery_info["success"] = success
                if details:
                    recovery_info["details"] = details
                
                # Record event
                event_id = self.record_event(
                    event_type="recovery_completed",
                    description=f"Recovery {recovery_id} for simulation {sim_id} completed with {'success' if success else 'failure'}",
                    severity="info" if success else "warning",
                    source="resilience_coordinator",
                    details={
                        "recovery_id": recovery_id,
                        "simulation_id": sim_id,
                        "success": success,
                        "details": details or {},
                    },
                )
                
                # Link to previous events
                for prev_event_id in recovery_info.get("events", []):
                    event = self.events.get(prev_event_id)
                    if event:
                        event.add_related_event(event_id)
                
                # Record metrics
                duration = (datetime.now() - datetime.fromisoformat(recovery_info["initiated_at"])).total_seconds()
                self.metrics.record_recovery_attempt(success, duration)
                
                # Also complete any common implementation recovery plans
                completed_plans = 0
                for plan_id, plan in list(self.active_recovery_plans.items()):
                    if plan.job_id == sim_id:
                        # Mark as complete
                        self.complete_recovery_plan(
                            plan_id=plan_id, 
                            success=success, 
                            error_message=details.get("error", "") if details and not success else None
                        )
                        completed_plans += 1
                
                if completed_plans > 0:
                    logger.info(f"Completed {completed_plans} common implementation recovery plans for simulation {sim_id}")
                
                # Remove from active recoveries
                del self.active_recoveries[sim_id]
                
                # Resolve any associated failures if successful
                if success:
                    for failure in self.failure_detector.get_active_failures(simulation_id=sim_id):
                        self.failure_detector.resolve_failure(
                            failure.id,
                            f"Recovery {recovery_id} completed successfully"
                        )
                
                return Result.ok(True)
        
        return Result.err(f"Recovery {recovery_id} not found")
    
    def execute_recovery_plan(self, plan_id: str) -> Result[bool]:
        """
        Execute a recovery plan.
        
        Override the parent implementation to also handle domain-specific tracking.
        """
        # Call the parent implementation
        result = super().execute_recovery_plan(plan_id)
        
        # Track this in our domain-specific system
        plan = self.active_recovery_plans.get(plan_id)
        if result.success and plan:
            # Add plan to our tracking
            # In a real implementation, we'd track this recovery and update when done
            # For now, just log the execution
            logger.info(f"Executing recovery plan {plan_id} for {plan.job_id or plan.node_id}")
        
        return result
    
    def complete_recovery_plan(
        self,
        plan_id: str,
        success: bool,
        error_message: Optional[str] = None,
    ) -> None:
        """Complete a recovery plan."""
        # Call the parent implementation
        super().complete_recovery(plan_id, success, error_message)
    
    def get_active_recoveries(self) -> Dict[str, Dict]:
        """Get all active recovery operations."""
        return self.active_recoveries.copy()
    
    def get_checkpoint_schedule(self) -> Dict[str, datetime]:
        """Get the current checkpoint schedule."""
        return self.checkpoint_schedule.copy()
    
    def get_resilience_metrics(self) -> Dict:
        """Get current resilience metrics."""
        return self.metrics.to_dict()
    
    def detect_and_handle_failures(
        self,
        nodes: Dict[str, ComputeNode],
        simulations: Dict[str, Simulation],
    ) -> List[str]:
        """Detect and handle failures in nodes and simulations."""
        handled_failures = []
        
        # Detect node failures
        node_failures = self.failure_detector.detect_node_failures(nodes)
        
        # Detect simulation failures
        sim_failures = self.failure_detector.detect_simulation_failures(simulations)
        
        # Handle all failures
        all_failures = node_failures + sim_failures
        
        for failure in all_failures:
            recovery_id = self.handle_failure_detection(failure)
            if recovery_id:
                handled_failures.append(recovery_id)
        
        # Process scheduled recoveries
        self.recovery_manager.process_failures()
        
        # Convert nodes and simulations for common implementation
        common_nodes = []
        for node in nodes.values():
            # Convert to BaseNode (minimal implementation)
            common_node = BaseNode(
                id=node.id,
                name=node.name,
                cpu_cores=node.cpu_cores,
                memory_gb=node.memory_gb,
                storage_gb=node.storage_gb,
                gpu_count=node.gpu_count if hasattr(node, 'gpu_count') else 0,
            )
            common_nodes.append(common_node)
        
        common_jobs = []
        for sim in simulations.values():
            # Convert to BaseJob (minimal implementation)
            common_job = BaseJob(
                id=sim.id,
                name=sim.name,
                owner=sim.owner,
                project=sim.project,
                estimated_duration=sim.estimated_duration,
                progress=sim.total_progress(),
            )
            common_jobs.append(common_job)
        
        # Also use common implementation
        _, common_plans = super().detect_and_recover(
            jobs=common_jobs,
            nodes=common_nodes,
            auto_recover=True  # Automatically execute recovery plans
        )
        
        # Add any recovery plans from common implementation
        for plan in common_plans:
            if plan.job_id and plan.job_id in simulations:
                recovery_id = self._initiate_simulation_recovery(
                    plan.job_id,
                    f"Failure recovery from common implementation",
                    map_common_recovery_action_to_strategy(plan.action),
                    plan.failure_event.id,
                )
                
                if recovery_id:
                    handled_failures.append(recovery_id)
        
        return handled_failures
    
    def process_checkpoints(
        self,
        simulations: Dict[str, Simulation],
    ) -> List[str]:
        """Process checkpoint creation for simulations."""
        # Check each simulation
        for sim_id, simulation in simulations.items():
            # Skip non-running simulations
            if simulation.status != "running":
                continue
            
            # Check if checkpoint is needed
            if self.checkpoint_coordinator.should_checkpoint_simulation(simulation):
                # Schedule checkpoint
                self.checkpoint_coordinator.schedule_checkpoint(sim_id)
        
        # Process scheduled checkpoints
        return self.process_scheduled_checkpoints(simulations)