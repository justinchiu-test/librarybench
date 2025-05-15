"""
Resilience coordination for the unified concurrent task scheduler.

This module provides functionality for coordinating failure detection and recovery
that can be used by both the render farm manager and scientific computing implementations.
"""

import logging
import threading
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Any, Union, Callable

from common.core.models import (
    BaseJob,
    BaseNode,
    Checkpoint,
    CheckpointType,
    JobStatus,
    NodeStatus,
    Result,
)
from common.core.utils import ExponentialBackoff
from common.failure_resilience.checkpoint_manager import CheckpointManager
from common.failure_resilience.failure_detector import (
    FailureDetector,
    FailureEvent,
    FailureLevel,
    FailureType,
)

logger = logging.getLogger(__name__)


class RecoveryAction(str, Enum):
    """Types of recovery actions."""
    
    RESTART_JOB = "restart_job"  # Restart a failed job from scratch
    RESTORE_CHECKPOINT = "restore_checkpoint"  # Restore a job from a checkpoint
    RESCHEDULE = "reschedule"  # Reschedule a job on a different node
    PREEMPT = "preempt"  # Preempt a job to free resources
    RETRY = "retry"  # Retry a failed operation
    SKIP = "skip"  # Skip the failed component
    ABORT = "abort"  # Abort the operation
    MANUAL = "manual"  # Requires manual intervention


class RecoveryPlan:
    """A plan for recovering from a failure."""
    
    def __init__(
        self,
        failure_event: FailureEvent,
        action: RecoveryAction,
        job_id: Optional[str] = None,
        node_id: Optional[str] = None,
        checkpoint_id: Optional[str] = None,
        description: str = "",
        max_retries: int = 3,
    ):
        """
        Initialize a recovery plan.
        
        Args:
            failure_event: The failure event to recover from
            action: The recovery action to take
            job_id: Optional ID of the job to recover
            node_id: Optional ID of the node to recover
            checkpoint_id: Optional ID of the checkpoint to use
            description: Human-readable description of the recovery plan
            max_retries: Maximum number of retry attempts
        """
        self.id = f"recovery_{failure_event.id}"
        self.failure_event = failure_event
        self.action = action
        self.job_id = job_id or failure_event.job_id
        self.node_id = node_id or failure_event.node_id
        self.checkpoint_id = checkpoint_id
        self.description = description
        self.created_at = datetime.now()
        self.executed_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.success: Optional[bool] = None
        self.error_message: Optional[str] = None
        self.max_retries = max_retries
        self.retry_count = 0
        self.retry_backoff = ExponentialBackoff(
            initial_delay_seconds=1.0,
            max_delay_seconds=60.0,
            backoff_factor=2.0,
            jitter=0.1,
        )
    
    def execute(self, executor_func: Callable[["RecoveryPlan"], Result[bool]]) -> Result[bool]:
        """
        Execute this recovery plan.
        
        Args:
            executor_func: Function that executes the recovery plan
            
        Returns:
            Result with success status or error
        """
        self.executed_at = datetime.now()
        self.retry_count += 1
        
        result = executor_func(self)
        
        if result.success:
            self.success = True
            self.completed_at = datetime.now()
            return result
        
        # Handle failure
        self.error_message = result.error
        
        # Check if we've exceeded max retries
        if self.retry_count >= self.max_retries:
            self.success = False
            return Result.err(f"Recovery failed after {self.retry_count} attempts: {result.error}")
        
        # Return the error, but allow for retry
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "failure_id": self.failure_event.id,
            "action": self.action.value,
            "job_id": self.job_id,
            "node_id": self.node_id,
            "checkpoint_id": self.checkpoint_id,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "success": self.success,
            "error_message": self.error_message,
            "max_retries": self.max_retries,
            "retry_count": self.retry_count,
        }


class RecoveryStrategy:
    """A strategy for recovering from a failure."""
    
    def __init__(
        self,
        failure_type: FailureType,
        action: RecoveryAction,
        conditions: Optional[Dict[str, Any]] = None,
        description: str = "",
        priority: int = 1,
        max_retries: int = 3,
    ):
        """
        Initialize a recovery strategy.
        
        Args:
            failure_type: The type of failure this strategy applies to
            action: The recovery action to take
            conditions: Optional conditions that must be met to apply this strategy
            description: Human-readable description of the strategy
            priority: Priority of the strategy (lower values have higher priority)
            max_retries: Maximum number of retry attempts
        """
        self.failure_type = failure_type
        self.action = action
        self.conditions = conditions or {}
        self.description = description
        self.priority = priority
        self.max_retries = max_retries
    
    def applies_to(self, failure_event: FailureEvent) -> bool:
        """
        Check if this strategy applies to the given failure event.
        
        Args:
            failure_event: The failure event to check
            
        Returns:
            True if the strategy applies, False otherwise
        """
        # Check failure type
        if failure_event.failure_type != self.failure_type:
            return False
        
        # Check conditions
        for key, value in self.conditions.items():
            if key == "level":
                # Special handling for failure level
                if failure_event.level.value != value:
                    return False
            elif key == "job_status" and failure_event.job_id:
                # This condition requires context not available in the event
                # Will be checked by the coordinator
                continue
            elif key == "node_status" and failure_event.node_id:
                # This condition requires context not available in the event
                # Will be checked by the coordinator
                continue
            elif key in failure_event.details:
                if failure_event.details[key] != value:
                    return False
            else:
                # Condition not met
                return False
        
        return True
    
    def create_plan(
        self,
        failure_event: FailureEvent,
        checkpoint_id: Optional[str] = None,
    ) -> RecoveryPlan:
        """
        Create a recovery plan from this strategy.
        
        Args:
            failure_event: The failure event to recover from
            checkpoint_id: Optional ID of the checkpoint to use
            
        Returns:
            Recovery plan based on this strategy
        """
        return RecoveryPlan(
            failure_event=failure_event,
            action=self.action,
            checkpoint_id=checkpoint_id,
            description=self.description,
            max_retries=self.max_retries,
        )


class ResilienceCoordinator:
    """
    Coordinator for failure detection and recovery.
    
    This class is responsible for:
    1. Managing failure detection
    2. Selecting appropriate recovery strategies
    3. Executing recovery plans
    4. Tracking recovery history
    """
    
    def __init__(
        self,
        checkpoint_manager: Optional[CheckpointManager] = None,
        failure_detector: Optional[FailureDetector] = None,
    ):
        """
        Initialize the resilience coordinator.
        
        Args:
            checkpoint_manager: Optional checkpoint manager to use
            failure_detector: Optional failure detector to use
        """
        self.checkpoint_manager = checkpoint_manager or CheckpointManager()
        self.failure_detector = failure_detector or FailureDetector()
        self.recovery_strategies: List[RecoveryStrategy] = []
        self.active_recovery_plans: Dict[str, RecoveryPlan] = {}
        self.recovery_history: List[RecoveryPlan] = []
        self.recovery_executor: Optional[Callable[[RecoveryPlan], Result[bool]]] = None
        
        # Register default recovery strategies
        self._register_default_strategies()
    
    def set_recovery_executor(
        self,
        executor_func: Callable[[RecoveryPlan], Result[bool]],
    ) -> None:
        """
        Set the function to execute recovery plans.
        
        Args:
            executor_func: Function that executes recovery plans
        """
        self.recovery_executor = executor_func
    
    def register_recovery_strategy(self, strategy: RecoveryStrategy) -> None:
        """
        Register a recovery strategy.
        
        Args:
            strategy: The recovery strategy to register
        """
        self.recovery_strategies.append(strategy)
        
        # Sort strategies by priority
        self.recovery_strategies.sort(key=lambda s: s.priority)
    
    def create_checkpoint(
        self,
        job: BaseJob,
        checkpoint_type: CheckpointType = CheckpointType.FULL,
    ) -> Result[Checkpoint]:
        """
        Create a checkpoint for a job.
        
        Args:
            job: The job to checkpoint
            checkpoint_type: Type of checkpoint to create
            
        Returns:
            Result with the created checkpoint or error
        """
        return self.checkpoint_manager.create_checkpoint(job, checkpoint_type)
    
    def detect_and_recover(
        self,
        jobs: List[BaseJob],
        nodes: List[BaseNode],
        auto_recover: bool = True,
    ) -> Tuple[List[FailureEvent], List[RecoveryPlan]]:
        """
        Detect failures and create recovery plans.
        
        Args:
            jobs: List of jobs to check for failures
            nodes: List of nodes to check for failures
            auto_recover: Whether to automatically execute recovery plans
            
        Returns:
            Tuple of (detected failures, recovery plans)
        """
        # Detect failures
        failures = self.failure_detector.detect_failures(jobs, nodes)
        
        recovery_plans = []
        
        # Create job and node lookups
        job_lookup = {job.id: job for job in jobs}
        node_lookup = {node.id: node for node in nodes}
        
        # Create recovery plans for each failure
        for failure in failures:
            # Skip if already recovering
            recovery_key = f"recovery_{failure.id}"
            if recovery_key in self.active_recovery_plans:
                continue
            
            # Find matching strategies
            matching_strategies = []
            for strategy in self.recovery_strategies:
                if strategy.applies_to(failure):
                    # Check additional conditions that require context
                    skip = False
                    for key, value in strategy.conditions.items():
                        if key == "job_status" and failure.job_id:
                            job = job_lookup.get(failure.job_id)
                            if not job or job.status.value != value:
                                skip = True
                                break
                        elif key == "node_status" and failure.node_id:
                            node = node_lookup.get(failure.node_id)
                            if not node or node.status.value != value:
                                skip = True
                                break
                    
                    if not skip:
                        matching_strategies.append(strategy)
            
            if not matching_strategies:
                continue
            
            # Use the highest-priority strategy (already sorted)
            strategy = matching_strategies[0]
            
            # Find latest checkpoint if needed
            checkpoint_id = None
            if strategy.action == RecoveryAction.RESTORE_CHECKPOINT and failure.job_id:
                checkpoint = self.checkpoint_manager.get_latest_checkpoint(failure.job_id)
                if checkpoint:
                    checkpoint_id = checkpoint.id
            
            # Create recovery plan
            plan = strategy.create_plan(
                failure_event=failure,
                checkpoint_id=checkpoint_id,
            )
            
            recovery_plans.append(plan)
            self.active_recovery_plans[recovery_key] = plan
            
            # Auto-execute if enabled and executor is set
            if auto_recover and self.recovery_executor:
                plan.execute(self.recovery_executor)
        
        return failures, recovery_plans
    
    def execute_recovery_plan(self, plan_id: str) -> Result[bool]:
        """
        Execute a recovery plan.
        
        Args:
            plan_id: ID of the recovery plan to execute
            
        Returns:
            Result with success status or error
        """
        if plan_id not in self.active_recovery_plans:
            return Result.err(f"Recovery plan {plan_id} not found")
        
        plan = self.active_recovery_plans[plan_id]
        
        if not self.recovery_executor:
            return Result.err("No recovery executor set")
        
        return plan.execute(self.recovery_executor)
    
    def complete_recovery(
        self,
        plan_id: str,
        success: bool,
        error_message: Optional[str] = None,
    ) -> None:
        """
        Mark a recovery plan as completed.
        
        Args:
            plan_id: ID of the recovery plan
            success: Whether the recovery was successful
            error_message: Optional error message if unsuccessful
        """
        if plan_id in self.active_recovery_plans:
            plan = self.active_recovery_plans[plan_id]
            plan.success = success
            plan.error_message = error_message
            plan.completed_at = datetime.now()
            
            # Move to history
            self.recovery_history.append(plan)
            del self.active_recovery_plans[plan_id]
            
            # Resolve the failure if successful
            if success:
                self.failure_detector.resolve_failure(
                    plan.failure_event.id,
                    f"Resolved by recovery plan {plan_id}"
                )
    
    def get_active_recovery_plans(
        self,
        job_id: Optional[str] = None,
        node_id: Optional[str] = None,
        failure_type: Optional[FailureType] = None,
        action: Optional[RecoveryAction] = None,
    ) -> List[RecoveryPlan]:
        """
        Get active recovery plans matching the filters.
        
        Args:
            job_id: Optional filter by job ID
            node_id: Optional filter by node ID
            failure_type: Optional filter by failure type
            action: Optional filter by recovery action
            
        Returns:
            List of matching active recovery plans
        """
        filtered_plans = []
        
        for plan in self.active_recovery_plans.values():
            # Apply filters
            if job_id is not None and plan.job_id != job_id:
                continue
                
            if node_id is not None and plan.node_id != node_id:
                continue
                
            if failure_type is not None and plan.failure_event.failure_type != failure_type:
                continue
                
            if action is not None and plan.action != action:
                continue
                
            filtered_plans.append(plan)
        
        return filtered_plans
    
    def get_recovery_history(
        self,
        job_id: Optional[str] = None,
        node_id: Optional[str] = None,
        failure_type: Optional[FailureType] = None,
        action: Optional[RecoveryAction] = None,
        success: Optional[bool] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[RecoveryPlan]:
        """
        Get recovery history matching the filters.
        
        Args:
            job_id: Optional filter by job ID
            node_id: Optional filter by node ID
            failure_type: Optional filter by failure type
            action: Optional filter by recovery action
            success: Optional filter by success status
            start_time: Optional filter by start time
            end_time: Optional filter by end time
            
        Returns:
            List of matching recovery plans
        """
        filtered_plans = []
        
        for plan in self.recovery_history:
            # Apply filters
            if job_id is not None and plan.job_id != job_id:
                continue
                
            if node_id is not None and plan.node_id != node_id:
                continue
                
            if failure_type is not None and plan.failure_event.failure_type != failure_type:
                continue
                
            if action is not None and plan.action != action:
                continue
                
            if success is not None and plan.success != success:
                continue
                
            if start_time is not None and plan.created_at < start_time:
                continue
                
            if end_time is not None and plan.created_at > end_time:
                continue
                
            filtered_plans.append(plan)
        
        return filtered_plans
    
    def _register_default_strategies(self) -> None:
        """Register default recovery strategies."""
        
        # Node offline strategy
        self.register_recovery_strategy(
            RecoveryStrategy(
                failure_type=FailureType.NODE_OFFLINE,
                action=RecoveryAction.RESCHEDULE,
                description="Reschedule jobs from offline node",
                priority=1,
            )
        )
        
        # Node timeout strategy
        self.register_recovery_strategy(
            RecoveryStrategy(
                failure_type=FailureType.NODE_TIMEOUT,
                action=RecoveryAction.RESCHEDULE,
                description="Reschedule jobs from unresponsive node",
                priority=2,
            )
        )
        
        # Job error with checkpoint strategy
        self.register_recovery_strategy(
            RecoveryStrategy(
                failure_type=FailureType.JOB_ERROR,
                action=RecoveryAction.RESTORE_CHECKPOINT,
                conditions={"job_status": "failed"},
                description="Restore job from latest checkpoint",
                priority=1,
            )
        )
        
        # Job error without checkpoint strategy
        self.register_recovery_strategy(
            RecoveryStrategy(
                failure_type=FailureType.JOB_ERROR,
                action=RecoveryAction.RESTART_JOB,
                conditions={"job_status": "failed"},
                description="Restart failed job",
                priority=2,
            )
        )
        
        # Job timeout strategy
        self.register_recovery_strategy(
            RecoveryStrategy(
                failure_type=FailureType.JOB_TIMEOUT,
                action=RecoveryAction.RESCHEDULE,
                description="Reschedule stalled job",
                priority=1,
            )
        )
        
        # Resource exhaustion strategy
        self.register_recovery_strategy(
            RecoveryStrategy(
                failure_type=FailureType.RESOURCE_EXHAUSTION,
                action=RecoveryAction.PREEMPT,
                description="Preempt lower-priority jobs to free resources",
                priority=1,
            )
        )
        
        # Dependency failure strategy
        self.register_recovery_strategy(
            RecoveryStrategy(
                failure_type=FailureType.DEPENDENCY_FAILURE,
                action=RecoveryAction.SKIP,
                description="Skip failed dependency and continue",
                priority=1,
            )
        )
        
        # Critical failures require manual intervention
        self.register_recovery_strategy(
            RecoveryStrategy(
                failure_type=FailureType.SYSTEM_FAILURE,
                action=RecoveryAction.MANUAL,
                conditions={"level": "critical"},
                description="Critical system failure requires manual intervention",
                priority=1,
            )
        )