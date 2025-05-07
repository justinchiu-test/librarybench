"""
Task manager for the unified workflow orchestration system.
"""
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from unified.task import Task, TaskState
from unified.queue import PriorityQueue, FIFOQueue
from unified.scheduler import Scheduler
from unified.logger import default_logger
from unified.utils import generate_id


class TaskManager:
    """
    Manages tasks, queuing, scheduling, and execution.
    """
    def __init__(self, max_workers: int = 5):
        """
        Initialize a TaskManager.
        
        :param max_workers: Maximum number of worker threads
        """
        self.logger = default_logger
        self.max_workers = max_workers
        
        # Task storage and tracking
        self._tasks: Dict[str, Task] = {}
        self._task_lock = threading.Lock()
        
        # Task queuing
        self._queue = PriorityQueue[Task]()
        
        # Thread pool for execution
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Task dependencies
        self._dependencies: Dict[str, Set[str]] = {}  # task_id -> set of dependent task_ids
        
        # Scheduling
        self.scheduler = Scheduler()
        self.scheduler.start()
        
        # Alerting
        self.alerts: List[str] = []
        
        # Metadata
        self._metadata: Dict[str, Dict[str, Any]] = {}
        self._metadata_lock = threading.Lock()
        
        # Running state
        self._running = True
        self._worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self._worker_thread.start()
    
    def queue_task(
        self,
        func: Callable[..., Any],
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        task_id: Optional[str] = None,
        priority: int = 5,
        timeout: Optional[float] = None,
        max_retries: int = 0,
        retry_delay_seconds: float = 1.0,
        backoff_factor: float = 2.0,
        dependencies: Optional[List[str]] = None,
    ) -> str:
        """
        Queue a task for execution.
        
        :param func: Function to execute
        :param args: Positional arguments for the function
        :param kwargs: Keyword arguments for the function
        :param task_id: Unique task ID (auto-generated if not provided)
        :param priority: Task priority (lower is higher priority)
        :param timeout: Maximum execution time in seconds
        :param max_retries: Maximum number of retry attempts
        :param retry_delay_seconds: Initial delay between retries
        :param backoff_factor: Factor for exponential backoff
        :param dependencies: List of task IDs that must complete before this task
        :return: Task ID
        """
        task_id = task_id or generate_id()
        
        task = Task(
            task_id=task_id,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            timeout=timeout,
            max_retries=max_retries,
            retry_delay_seconds=retry_delay_seconds,
            backoff_factor=backoff_factor,
            dependencies=dependencies or []
        )
        
        with self._task_lock:
            if task_id in self._tasks:
                raise ValueError(f"Task with ID {task_id} already exists")
            self._tasks[task_id] = task
            
            # Register dependencies
            for dep_id in task.dependencies:
                if dep_id not in self._dependencies:
                    self._dependencies[dep_id] = set()
                self._dependencies[dep_id].add(task_id)
        
        # Initialize metadata
        self._init_task_metadata(task)
        
        # Queue task if no dependencies, otherwise it will be queued when dependencies complete
        if not task.dependencies:
            self._queue.push(task)
        
        self.logger.info(f"Queued task {task_id} with priority {priority}")
        return task_id
    
    def _init_task_metadata(self, task: Task):
        """
        Initialize task metadata.
        
        :param task: Task instance
        """
        with self._metadata_lock:
            self._metadata[task.task_id] = {
                "task_id": task.task_id,
                "status": task.state.value,
                "priority": task.priority,
                "queued_at": time.time(),
                "start_time": None,
                "end_time": None,
                "execution_time": None,
                "retry_count": 0,
                "dependencies": task.dependencies.copy() if task.dependencies else [],
                "dependent_tasks": list(self._dependencies.get(task.task_id, set())),
            }
    
    def get_task_metadata(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a task.
        
        :param task_id: Task ID
        :return: Metadata dictionary or None if task not found
        """
        with self._metadata_lock:
            return self._metadata.get(task_id)
    
    def get_all_task_metadata(self) -> Dict[str, Dict[str, Any]]:
        """
        Get metadata for all tasks.
        
        :return: Dictionary mapping task IDs to metadata
        """
        with self._metadata_lock:
            return self._metadata.copy()
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a queued or running task.
        
        :param task_id: Task ID
        :return: True if task was canceled, False otherwise
        """
        with self._task_lock:
            if task_id not in self._tasks:
                return False
            task = self._tasks[task_id]
            
            canceled = task.cancel()
            if canceled:
                self.logger.info(f"Canceled task {task_id}")
                
                with self._metadata_lock:
                    if task_id in self._metadata:
                        self._metadata[task_id]["status"] = TaskState.CANCELED.value
                        self._metadata[task_id]["end_time"] = time.time()
            
            return canceled
    
    def schedule_task(
        self,
        func: Callable[..., Any],
        interval_seconds: float,
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        task_priority: int = 5,
        task_timeout: Optional[float] = None,
        task_max_retries: int = 0,
        task_retry_delay_seconds: float = 1.0,
        task_backoff_factor: float = 2.0,
    ) -> str:
        """
        Schedule a task to run at regular intervals.
        
        :param func: Function to execute
        :param interval_seconds: Interval between executions
        :param args: Positional arguments for the function
        :param kwargs: Keyword arguments for the function
        :param task_priority: Task priority
        :param task_timeout: Task timeout
        :param task_max_retries: Task max retries
        :param task_retry_delay_seconds: Task retry delay
        :param task_backoff_factor: Task backoff factor
        :return: Schedule ID
        """
        def schedule_callback():
            self.queue_task(
                func=func,
                args=args,
                kwargs=kwargs,
                priority=task_priority,
                timeout=task_timeout,
                max_retries=task_max_retries,
                retry_delay_seconds=task_retry_delay_seconds,
                backoff_factor=task_backoff_factor
            )
        
        schedule_id = self.scheduler.add_schedule(
            callback=schedule_callback,
            interval_seconds=interval_seconds
        )
        
        self.logger.info(f"Created schedule {schedule_id} with interval {interval_seconds}s")
        return schedule_id
    
    def cancel_schedule(self, schedule_id: str) -> bool:
        """
        Cancel a scheduled task.
        
        :param schedule_id: Schedule ID
        :return: True if schedule was canceled, False otherwise
        """
        return self.scheduler.remove_schedule(schedule_id)
    
    def _process_queue(self):
        """
        Process the task queue in a background thread.
        """
        while self._running:
            # Get the next task from the queue
            task = self._queue.pop()
            if task is None:
                time.sleep(0.1)
                continue
            
            # Check if task is valid
            with self._task_lock:
                if task.task_id not in self._tasks:
                    continue
                
                # Check if dependencies are satisfied
                deps_satisfied = True
                for dep_id in task.dependencies:
                    if dep_id not in self._tasks or self._tasks[dep_id].state != TaskState.SUCCESS:
                        deps_satisfied = False
                        break
                
                if not deps_satisfied:
                    # Put the task back in the queue for later processing
                    self._queue.push(task)
                    time.sleep(0.1)
                    continue
            
            # Update metadata
            with self._metadata_lock:
                if task.task_id in self._metadata:
                    self._metadata[task.task_id]["status"] = TaskState.RUNNING.value
                    self._metadata[task.task_id]["start_time"] = time.time()
            
            # Submit task to thread pool
            self._executor.submit(self._execute_task, task)
    
    def _execute_task(self, task: Task):
        """
        Execute a task and handle its result.
        
        :param task: Task to execute
        """
        try:
            result = task.run(self.logger)
            
            # Update metadata after execution
            with self._metadata_lock:
                if task.task_id in self._metadata:
                    metadata = self._metadata[task.task_id]
                    metadata["status"] = task.state.value
                    metadata["end_time"] = time.time()
                    metadata["execution_time"] = metadata["end_time"] - metadata["start_time"] if metadata["start_time"] else None
                    metadata["retry_count"] = task.attempts - 1
            
            # Check for dynamically created tasks
            if isinstance(result, list) and all(isinstance(item, Task) for item in result):
                for new_task in result:
                    self.queue_task(
                        func=new_task.func,
                        args=new_task.args,
                        kwargs=new_task.kwargs,
                        task_id=new_task.task_id,
                        priority=new_task.priority,
                        timeout=new_task.timeout,
                        max_retries=new_task.max_retries,
                        retry_delay_seconds=new_task.retry_delay_seconds,
                        backoff_factor=new_task.backoff_factor
                    )
            
            # Process dependent tasks
            self._process_dependent_tasks(task.task_id)
            
        except Exception as e:
            self.logger.error(f"Task {task.task_id} failed with error: {str(e)}")
            
            # Update metadata
            with self._metadata_lock:
                if task.task_id in self._metadata:
                    metadata = self._metadata[task.task_id]
                    metadata["status"] = TaskState.FAILURE.value
                    metadata["end_time"] = time.time()
                    metadata["execution_time"] = metadata["end_time"] - metadata["start_time"] if metadata["start_time"] else None
                    metadata["retry_count"] = task.attempts - 1
            
            # Generate alert
            alert_msg = f"Task {task.task_id} failed after {task.attempts} attempts: {str(e)}"
            self.alerts.append(alert_msg)
            self.logger.error(alert_msg)
            
            # Process dependent tasks (they won't run because this task failed)
            self._process_dependent_tasks(task.task_id)
    
    def _process_dependent_tasks(self, task_id: str):
        """
        Process tasks that depend on the completed task.
        
        :param task_id: Completed task ID
        """
        dependent_tasks = []
        
        with self._task_lock:
            if task_id in self._dependencies:
                dependent_tasks = list(self._dependencies[task_id])
                for dep_id in dependent_tasks:
                    # Check if all dependencies are satisfied
                    if dep_id in self._tasks:
                        task = self._tasks[dep_id]
                        deps_satisfied = True
                        for dependency_id in task.dependencies:
                            if dependency_id not in self._tasks or self._tasks[dependency_id].state != TaskState.SUCCESS:
                                deps_satisfied = False
                                break
                        
                        if deps_satisfied:
                            self._queue.push(task)
                            self.logger.info(f"Queued dependent task {dep_id}")
    
    def shutdown(self, wait: bool = True):
        """
        Shut down the task manager and wait for tasks to complete.
        
        :param wait: Whether to wait for tasks to complete
        """
        self._running = False
        self.scheduler.stop()
        
        if wait:
            self._worker_thread.join()
            self._executor.shutdown(wait=True)
        
        self.logger.info("Task manager shut down")