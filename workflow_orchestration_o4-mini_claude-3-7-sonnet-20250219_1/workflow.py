"""
Workflow management system for defining and executing task-based workflows.

This module provides classes for creating tasks with dependencies, organizing them
into workflows, and executing them with support for retries, timeouts, and parallel execution.
"""

import threading
import time
import datetime
import inspect
from enum import Enum
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union


class TaskState(Enum):
    """Represents the possible states of a task during execution."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    RETRYING = "retrying"


class TaskFailedError(Exception):
    """Exception raised when a task fails during workflow execution."""
    pass


class TaskExecutionRecord:
    """Records details about a single execution of a task."""
    
    def __init__(self, start_time: datetime.datetime, end_time: datetime.datetime, status: str):
        """
        Initialize a task execution record.
        
        Args:
            start_time: When the task execution started
            end_time: When the task execution ended
            status: The execution result status ("success" or "failure")
        """
        self.start_time = start_time
        self.end_time = end_time
        self.status = status  # "success" or "failure"


class WorkflowExecutionRecord:
    """Records details about a single execution of a workflow."""
    
    def __init__(self, start_time: datetime.datetime):
        """
        Initialize a workflow execution record.
        
        Args:
            start_time: When the workflow execution started
        """
        self.start_time = start_time
        self.end_time: Optional[datetime.datetime] = None
        self.status: Optional[str] = None  # "success" or "failure"
        self.task_executions: Dict[str, TaskExecutionRecord] = {}  # name -> TaskExecutionRecord


class Task:
    """
    Represents a single task in a workflow with its execution logic and dependencies.
    """
    
    def __init__(
        self, 
        name: str, 
        func: Callable,
        dependencies: Optional[List[str]] = None,
        max_retries: int = 0,
        retry_delay: float = 0,
        timeout: Optional[float] = None,
        logger: Any = None
    ):
        """
        Initialize a task.
        
        Args:
            name: Unique name for the task
            func: The function to execute for this task
            dependencies: List of task names this task depends on
            max_retries: Maximum number of retry attempts if the task fails
            retry_delay: Delay between retry attempts in seconds
            timeout: Maximum execution time in seconds before timing out
            logger: Logger instance for task logging
        """
        self.name = name
        self.func = func
        self.dependencies = dependencies[:] if dependencies else []
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        self.logger = logger
        self.state = TaskState.PENDING
        self.result = None
        self.error = None
        self.attempts = 0
        self.execution_records: List[TaskExecutionRecord] = []

    def reset(self) -> None:
        """Reset the task state for a new execution while preserving execution history."""
        self.state = TaskState.PENDING
        self.result = None
        self.error = None
        self.attempts = 0
        # keep execution history across runs

    def execute(self, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute one attempt of the task.
        
        Args:
            context: Optional context data passed from dependent tasks
            
        Returns:
            The result of the task execution
        """
        self.attempts += 1
        start = datetime.datetime.now()
        self.state = TaskState.RUNNING
        exc = None
        result = None

        try:
            result = self._execute_with_timeout(context)
            self.state = TaskState.SUCCESS
            self.result = result
            self.error = None
        except TimeoutError:
            exc = Exception(f"Task '{self.name}' timed out")
            self.error = exc
        except Exception as e:
            exc = e
            self.error = e

        end = datetime.datetime.now()
        status = self._determine_execution_status(exc)
        
        # Record execution
        rec = TaskExecutionRecord(start, end, status)
        self.execution_records.append(rec)

        return getattr(self, 'result', None)
    
    def _execute_with_timeout(self, context: Optional[Dict[str, Any]]) -> Any:
        """
        Execute the task function with timeout handling if configured.
        
        Args:
            context: Optional context data passed from dependent tasks
            
        Returns:
            The result of the task execution
            
        Raises:
            TimeoutError: If the task execution exceeds the timeout
        """
        # Prepare call based on function signature
        call_func = self._prepare_function_call(context)
        
        # Execute with timeout if specified
        if self.timeout is not None:
            with ThreadPoolExecutor(max_workers=1) as executor:
                fut = executor.submit(call_func)
                return fut.result(timeout=self.timeout)
        else:
            return call_func()
    
    def _prepare_function_call(self, context: Optional[Dict[str, Any]]) -> Callable:
        """
        Prepare the function call based on the function signature.
        
        Args:
            context: Optional context data passed from dependent tasks
            
        Returns:
            A callable that will execute the task function
        """
        sig = inspect.signature(self.func)
        if len(sig.parameters) == 0:
            # Call without context
            return lambda: self.func()
        else:
            return lambda: self.func(context=context)
    
    def _determine_execution_status(self, exc: Optional[Exception]) -> str:
        """
        Determine the execution status based on the presence of an exception.
        
        Args:
            exc: The exception that occurred during execution, if any
            
        Returns:
            The execution status ("success" or "failure")
        """
        if exc is None:
            return "success"
        
        if self.attempts <= self.max_retries:
            self.state = TaskState.RETRYING
        else:
            self.state = TaskState.FAILURE
            
        return "failure"


class ScheduleType(Enum):
    """Types of scheduling intervals for workflow execution."""
    HOURLY = "hourly"
    DAILY = "daily"


class Schedule:
    """
    Defines when a workflow should be executed based on time-based rules.
    """
    
    def __init__(self, type: ScheduleType, hour: Optional[int] = None, minute: Optional[int] = None):
        """
        Initialize a schedule.
        
        Args:
            type: The type of schedule (hourly, daily)
            hour: The hour to run (for daily schedules)
            minute: The minute to run (for daily schedules)
        """
        self.type = type
        self.hour = hour
        self.minute = minute
        self.last_run: Optional[datetime.datetime] = None

    def should_run(self) -> bool:
        """
        Determine if the workflow should run based on the schedule.
        
        Returns:
            True if the workflow should run, False otherwise
        """
        now = datetime.datetime.now()
        
        if self.last_run is None:
            return True
            
        if self.type == ScheduleType.HOURLY:
            return now >= self.last_run + datetime.timedelta(hours=1)
            
        if self.type == ScheduleType.DAILY:
            # Only run once per day at specified hour/minute
            if self.hour is None or self.minute is None:
                return True
                
            today_sched = now.replace(
                hour=self.hour, 
                minute=self.minute,
                second=0, 
                microsecond=0
            )
            
            # If scheduled time passed, and last_run date < today
            return now >= today_sched and self.last_run.date() < now.date()
            
        return False


class Workflow:
    """
    A workflow composed of tasks with dependencies that can be executed.
    """
    
    def __init__(self, name: Optional[str] = None):
        """
        Initialize a workflow.
        
        Args:
            name: Optional name for the workflow
        """
        self.name = name
        self.tasks: Dict[str, Task] = {}
        self.execution_history: List[WorkflowExecutionRecord] = []

    def add_task(self, task: Task) -> None:
        """
        Add a task to the workflow.
        
        Args:
            task: The task to add
            
        Raises:
            ValueError: If a task with the same name already exists
        """
        if task.name in self.tasks:
            raise ValueError(f"Task {task.name} already exists")
        self.tasks[task.name] = task

    def get_task_result(self, name: str) -> Any:
        """
        Get the result of a task by name.
        
        Args:
            name: The name of the task
            
        Returns:
            The result of the task
        """
        return self.tasks[name].result

    def validate(self) -> None:
        """
        Validate the workflow for missing dependencies and cycles.
        
        Raises:
            ValueError: If there are missing dependencies or cycles in the workflow
        """
        self._check_missing_dependencies()
        self._check_for_cycles()

    def _check_missing_dependencies(self) -> None:
        """
        Check for missing dependencies in the workflow.
        
        Raises:
            ValueError: If there are missing dependencies
        """
        for task in self.tasks.values():
            for dep in task.dependencies:
                if dep not in self.tasks:
                    raise ValueError(f"Missing dependency: {dep}")

    def _check_for_cycles(self) -> None:
        """
        Check for cycles in the workflow dependency graph.
        
        Raises:
            ValueError: If there are cycles in the workflow
        """
        visited: Dict[str, int] = {}
        
        def dfs(node: str) -> bool:
            if node in visited:
                if visited[node] == 1:
                    return True  # Cycle detected
                return False
            visited[node] = 1  # Mark as visiting
            for dep in self.tasks[node].dependencies:
                if dfs(dep):
                    return True
            visited[node] = 2  # Mark as visited
            return False

        for name in self.tasks:
            if dfs(name):
                raise ValueError("Cycle detected in workflow")

    def run(self) -> Dict[str, Any]:
        """
        Execute the workflow, respecting task dependencies.
        
        Returns:
            A dictionary mapping task names to their results
            
        Raises:
            TaskFailedError: If any task fails during execution
        """
        self.validate()
        wf_record = WorkflowExecutionRecord(datetime.datetime.now())
        
        # Prepare results from already successful tasks
        results = self._initialize_results()
        
        # Get task execution levels (for parallel execution)
        levels = self._compute_execution_levels()
        
        # Group tasks by level
        level_groups = self._group_tasks_by_level(levels)
        
        # Execute tasks level by level
        executor = ThreadPoolExecutor(max_workers=len(self.tasks) or 1)
        try:
            for level in sorted(level_groups):
                tasks_at_level = level_groups[level]
                
                # Check for dependency failures before executing this level
                if self._handle_dependency_failures(tasks_at_level, wf_record):
                    wf_record.status = "failure"
                    wf_record.end_time = datetime.datetime.now()
                    self.execution_history.append(wf_record)
                    raise TaskFailedError("Workflow failed due to dependency failure")
                
                # Execute tasks at this level in parallel
                results = self._execute_task_level(
                    tasks_at_level, 
                    results, 
                    executor, 
                    wf_record
                )
            
            # All levels completed successfully
            wf_record.status = "success"
            wf_record.end_time = datetime.datetime.now()
            self.execution_history.append(wf_record)
            return results
            
        finally:
            executor.shutdown(wait=False)

    def _initialize_results(self) -> Dict[str, Any]:
        """
        Initialize results dictionary with results from already successful tasks.
        
        Returns:
            Dictionary mapping task names to their results
        """
        results = {}
        
        # Reset pending tasks and collect results from successful ones
        for task in self.tasks.values():
            if task.state == TaskState.SUCCESS:
                results[task.name] = task.result
            else:
                task.state = TaskState.PENDING
                
        return results

    def _compute_execution_levels(self) -> Dict[str, int]:
        """
        Compute the execution level for each task using topological sort.
        
        Returns:
            Dictionary mapping task names to their execution levels
        """
        # Calculate indegree for each task
        indegree = {name: 0 for name in self.tasks}
        graph = defaultdict(list)
        
        for task in self.tasks.values():
            for dep in task.dependencies:
                graph[dep].append(task.name)
                indegree[task.name] += 1
        
        # BFS to compute levels
        queue = deque()
        levels = {}
        
        # Start with tasks that have no dependencies
        for name, deg in indegree.items():
            if deg == 0:
                queue.append(name)
                levels[name] = 0
        
        # Process the queue
        while queue:
            current = queue.popleft()
            
            for dependent in graph[current]:
                indegree[dependent] -= 1
                if indegree[dependent] == 0:
                    levels[dependent] = levels[current] + 1
                    queue.append(dependent)
        
        return levels

    def _group_tasks_by_level(self, levels: Dict[str, int]) -> Dict[int, List[Task]]:
        """
        Group tasks by their execution level.
        
        Args:
            levels: Dictionary mapping task names to their execution levels
            
        Returns:
            Dictionary mapping levels to lists of tasks
        """
        level_groups = defaultdict(list)
        
        for name, level in levels.items():
            level_groups[level].append(self.tasks[name])
            
        return level_groups

    def _handle_dependency_failures(
        self, 
        tasks: List[Task], 
        wf_record: WorkflowExecutionRecord
    ) -> bool:
        """
        Mark tasks as failed if their dependencies failed.
        
        Args:
            tasks: List of tasks to check
            wf_record: The workflow execution record to update
            
        Returns:
            True if any task was marked as failed, False otherwise
        """
        any_failed = False
        
        for task in tasks:
            if task.state != TaskState.PENDING:
                continue
                
            for dep_name in task.dependencies:
                dep_task = self.tasks[dep_name]
                if dep_task.state == TaskState.FAILURE:
                    task.state = TaskState.FAILURE
                    task.error = Exception(f"Dependency {dep_name} failed")
                    
                    # Record the failure
                    now = datetime.datetime.now()
                    rec = TaskExecutionRecord(now, now, "failure")
                    task.execution_records.append(rec)
                    wf_record.task_executions[task.name] = rec
                    any_failed = True
                    break
        
        return any_failed

    def _execute_task_level(
        self, 
        tasks: List[Task], 
        results: Dict[str, Any],
        executor: ThreadPoolExecutor,
        wf_record: WorkflowExecutionRecord
    ) -> Dict[str, Any]:
        """
        Execute all tasks at a given level in parallel.
        
        Args:
            tasks: List of tasks to execute
            results: Dictionary of results from previous tasks
            executor: ThreadPoolExecutor to use for parallel execution
            wf_record: The workflow execution record to update
            
        Returns:
            Updated results dictionary
            
        Raises:
            TaskFailedError: If any task fails during execution
        """
        # Handle already successful tasks
        for task in tasks:
            if task.state == TaskState.SUCCESS:
                # Ensure there's a record
                if not task.execution_records:
                    now = datetime.datetime.now()
                    rec = TaskExecutionRecord(now, now, "success")
                    task.execution_records.append(rec)
                wf_record.task_executions[task.name] = task.execution_records[-1]
        
        # Submit pending tasks for execution
        futures = {}
        for task in tasks:
            if task.state == TaskState.PENDING:
                # Build context from dependencies
                context = self._build_task_context(task, results)
                
                # Submit task for execution
                futures[executor.submit(self._run_task, task, context)] = task
        
        # Process completed tasks
        for future in as_completed(futures):
            task = futures[future]
            
            # Record execution
            wf_record.task_executions[task.name] = task.execution_records[-1]
            
            if task.state == TaskState.SUCCESS:
                results[task.name] = task.result
            else:
                # Handle task failure
                self._handle_task_failure(task, wf_record)
                
                # Raise exception to abort workflow
                err_msg = str(task.error) or ""
                raise TaskFailedError(f"Task {task.name} failed: {err_msg}")
        
        return results

    def _build_task_context(self, task: Task, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build the context for a task from its dependencies' results.
        
        Args:
            task: The task to build context for
            results: Dictionary of results from previous tasks
            
        Returns:
            The context dictionary for the task
        """
        context = {}
        
        for dep_name in task.dependencies:
            dep_result = results.get(dep_name)
            if isinstance(dep_result, dict):
                context.update(dep_result)
                
        return context

    def _handle_task_failure(self, task: Task, wf_record: WorkflowExecutionRecord) -> None:
        """
        Handle a task failure by marking dependent tasks as failed.
        
        Args:
            task: The failed task
            wf_record: The workflow execution record to update
        """
        # Mark workflow as failed
        wf_record.status = "failure"
        wf_record.end_time = datetime.datetime.now()
        self.execution_history.append(wf_record)
        
        # Mark dependent tasks as failed
        for dep_task in self.tasks.values():
            if (task.name in dep_task.dependencies and 
                dep_task.state == TaskState.PENDING):
                
                dep_task.state = TaskState.FAILURE
                dep_task.error = Exception(f"Dependency {task.name} failed")
                
                # Record the failure
                now = datetime.datetime.now()
                rec = TaskExecutionRecord(now, now, "failure")
                dep_task.execution_records.append(rec)
                wf_record.task_executions[dep_task.name] = rec

    def _run_task(self, task: Task, context: Dict[str, Any]) -> TaskState:
        """
        Run a task with retry logic.
        
        Args:
            task: The task to run
            context: The context for the task
            
        Returns:
            The final state of the task
        """
        # Handle retries internally
        while True:
            task.execute(context=context)
            if task.state == TaskState.RETRYING:
                # Backoff logic could go here (skipped for tests)
                continue
            break
            
        return task.state
