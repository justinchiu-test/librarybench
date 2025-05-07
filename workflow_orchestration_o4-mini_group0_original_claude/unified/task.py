"""
Task implementation for the unified workflow orchestration system.
"""
import time
import threading
import traceback
from enum import Enum
from logging import Logger
from queue import Queue as ThreadQueue
from typing import Any, Callable, Dict, List, Optional, Union

from unified.utils import exponential_backoff, generate_id, safe_execute
from unified.logger import default_logger


class TaskState(str, Enum):
    """
    Task states for tracking progress.
    """
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    CANCELED = "canceled"


class Task:
    """
    Represents a single unit of work with retry, timeout, and backoff capabilities.
    """
    def __init__(
        self,
        task_id: Optional[str] = None,
        func: Optional[Callable[..., Any]] = None,
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        priority: int = 5,
        timeout: Optional[float] = None,
        max_retries: int = 0,
        retry_delay_seconds: float = 1.0,
        backoff_factor: float = 2.0,
        dependencies: Optional[List[str]] = None,
    ):
        """
        Initialize a Task instance.

        :param task_id: Unique identifier for the task (auto-generated if not provided)
        :param func: The callable to execute
        :param args: Positional arguments for the callable
        :param kwargs: Keyword arguments for the callable
        :param priority: Task priority (lower number means higher priority)
        :param timeout: Maximum execution time in seconds
        :param max_retries: Maximum number of retries on failure
        :param retry_delay_seconds: Base delay for retries in seconds
        :param backoff_factor: Multiplier for exponential backoff
        :param dependencies: List of task IDs that must complete before this task can run
        """
        self.task_id = task_id or generate_id()
        self.func = func
        self.args = args or []
        self.kwargs = kwargs or {}
        self.priority = priority
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds
        self.backoff_factor = backoff_factor
        self.dependencies = dependencies or []
        
        self.state = TaskState.PENDING
        self.attempts = 0
        self.start_time = None
        self.end_time = None
        self.execution_time = None
        self.result = None
        self.exception = None
        self._cancel_requested = False
        self._thread = None
    
    def run(self, logger: Optional[Logger] = None) -> Any:
        """
        Execute the task with retry, timeout, and exponential backoff.
        May return dynamically created tasks or the function's result.
        
        :param logger: Logger instance to use (uses default_logger if not provided)
        :return: Function result or list of dynamically created tasks
        """
        if logger is None:
            logger = default_logger
        
        self.state = TaskState.RUNNING
        self.start_time = time.time()
        dynamic_tasks = []
        
        logger.info(f"Task {self.task_id}: starting execution")
        
        while self.attempts <= self.max_retries:
            if self._cancel_requested:
                self.state = TaskState.CANCELED
                logger.info(f"Task {self.task_id}: execution canceled")
                break
            
            self.attempts += 1
            attempt_start = time.time()
            
            try:
                result = self._execute_with_timeout()
                self.result = result
                
                # Check if result is a list of Task objects
                if isinstance(result, list) and all(isinstance(item, Task) for item in result):
                    dynamic_tasks = result
                
                self.state = TaskState.SUCCESS
                self.end_time = time.time()
                self.execution_time = self.end_time - self.start_time
                logger.info(f"Task {self.task_id}: succeeded in {self.execution_time:.2f}s")
                
                return result
            
            except Exception as e:
                self.exception = e
                attempt_duration = time.time() - attempt_start
                
                if isinstance(e, TimeoutError):
                    self.state = TaskState.TIMEOUT
                    logger.error(f"Task {self.task_id}: timed out after {attempt_duration:.2f}s")
                    break
                
                logger.error(f"Task {self.task_id}: attempt {self.attempts} failed after {attempt_duration:.2f}s: {str(e)}")
                
                if self.attempts > self.max_retries:
                    self.state = TaskState.FAILURE
                    self.end_time = time.time()
                    self.execution_time = self.end_time - self.start_time
                    logger.error(f"Task {self.task_id}: failed after {self.attempts} attempts, exceeded max retries ({self.max_retries})")
                    break
                
                # Sleep with exponential backoff before retry
                delay = exponential_backoff(
                    self.retry_delay_seconds, 
                    self.attempts, 
                    self.backoff_factor
                )
                logger.info(f"Task {self.task_id}: retrying in {delay:.2f}s")
                time.sleep(delay)
        
        if self.state == TaskState.FAILURE:
            error_msg = f"Task {self.task_id} failed after {self.attempts} attempts"
            if self.exception:
                error_msg += f": {str(self.exception)}"
            raise Exception(error_msg)
        
        return dynamic_tasks
    
    def _execute_with_timeout(self) -> Any:
        """
        Execute the task function with timeout handling.
        
        :return: Function result
        :raises: TimeoutError if execution exceeds timeout
        :raises: Exception for any other execution errors
        """
        if not self.timeout:
            return self.func(*self.args, **self.kwargs)
        
        result_queue = ThreadQueue()
        
        def target():
            try:
                result = self.func(*self.args, **self.kwargs)
                result_queue.put((result, None))
            except Exception as e:
                result_queue.put((None, e))
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        self._thread = thread
        thread.start()
        
        thread.join(self.timeout)
        
        if thread.is_alive():
            self._thread = None
            raise TimeoutError(f"Task execution timed out after {self.timeout}s")
        
        if not result_queue.empty():
            result, error = result_queue.get()
            if error:
                raise error
            return result
        
        raise Exception("Unknown execution error")
    
    def cancel(self) -> bool:
        """
        Request cancellation of the task.
        
        :return: True if cancellation was requested, False otherwise
        """
        if self.state in [TaskState.PENDING, TaskState.RUNNING]:
            self._cancel_requested = True
            return True
        return False
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the task execution.
        
        :return: Dictionary with task metadata
        """
        return {
            "task_id": self.task_id,
            "state": self.state,
            "attempts": self.attempts,
            "priority": self.priority,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "execution_time": self.execution_time,
            "has_error": self.exception is not None,
            "error_message": str(self.exception) if self.exception else None,
            "dependencies": self.dependencies,
        }
    
    def __lt__(self, other: "Task") -> bool:
        """
        Compare tasks based on priority (for priority queue).
        
        :param other: Other task
        :return: True if this task has higher priority
        """
        return self.priority < other.priority
    
    def __repr__(self) -> str:
        """
        String representation of the task.
        
        :return: Human-readable representation
        """
        return f"<Task {self.task_id} state={self.state} priority={self.priority}>"