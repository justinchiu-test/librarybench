"""
Workflow implementation for the unified workflow orchestration system.
"""
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Set, Union

from unified.task import Task, TaskState
from unified.scheduler import Scheduler
from unified.logger import default_logger
from unified.utils import generate_id


class Workflow:
    """
    Container for a group of related tasks with dependencies.
    """
    def __init__(
        self,
        workflow_id: str,
        name: str,
        description: str = "",
        version: int = 1
    ):
        """
        Initialize a workflow.
        
        :param workflow_id: Unique workflow identifier
        :param name: Workflow name
        :param description: Workflow description
        :param version: Workflow version
        """
        self.workflow_id = workflow_id
        self.name = name
        self.description = description
        self.version = version
        self.tasks: Dict[str, Task] = {}
        self.created_at = time.time()
        self.updated_at = time.time()
        self.last_run_at = None
        self.status = "created"
    
    def add_task(self, task: Task) -> bool:
        """
        Add a task to the workflow.
        
        :param task: Task instance
        :return: True if task was added, False if it already exists
        """
        if task.task_id in self.tasks:
            return False
        
        self.tasks[task.task_id] = task
        self.updated_at = time.time()
        return True
    
    def remove_task(self, task_id: str) -> bool:
        """
        Remove a task from the workflow.
        
        :param task_id: Task ID
        :return: True if task was removed, False if it doesn't exist
        """
        if task_id not in self.tasks:
            return False
        
        # Check if any other tasks depend on this one
        for other_task in self.tasks.values():
            if task_id in other_task.dependencies:
                # Update dependencies
                other_task.dependencies.remove(task_id)
        
        del self.tasks[task_id]
        self.updated_at = time.time()
        return True
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get a task by ID.
        
        :param task_id: Task ID
        :return: Task instance or None if not found
        """
        return self.tasks.get(task_id)
    
    def get_dependencies(self) -> Dict[str, List[str]]:
        """
        Get all task dependencies.
        
        :return: Dictionary mapping task IDs to lists of dependency task IDs
        """
        return {
            task_id: task.dependencies.copy() if task.dependencies else []
            for task_id, task in self.tasks.items()
        }
    
    def get_execution_order(self) -> List[str]:
        """
        Get a valid execution order for tasks based on dependencies.
        
        :return: List of task IDs in execution order
        """
        # Topological sort
        result = []
        visited = set()
        temp_visited = set()
        
        def visit(task_id: str):
            if task_id in temp_visited:
                raise ValueError("Circular dependency detected")
            if task_id in visited:
                return
                
            temp_visited.add(task_id)
            
            task = self.tasks[task_id]
            for dep_id in task.dependencies:
                if dep_id in self.tasks:
                    visit(dep_id)
            
            temp_visited.remove(task_id)
            visited.add(task_id)
            result.append(task_id)
        
        for task_id in self.tasks:
            if task_id not in visited:
                visit(task_id)
        
        # Reverse to get correct order
        return list(reversed(result))
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert workflow to dictionary.
        
        :return: Dictionary representation
        """
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "task_count": len(self.tasks),
            "tasks": {task_id: task.get_metadata() for task_id, task in self.tasks.items()},
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_run_at": self.last_run_at,
            "status": self.status
        }
    
    def __repr__(self) -> str:
        """
        String representation of the workflow.
        
        :return: Human-readable representation
        """
        return f"<Workflow {self.workflow_id} name='{self.name}' version={self.version} tasks={len(self.tasks)}>"


class WorkflowManager:
    """
    Manages workflow registration, versioning, scheduling, and execution.
    """
    def __init__(self):
        """
        Initialize a workflow manager.
        """
        self.workflows: Dict[str, Workflow] = {}
        self.scheduler = Scheduler()
        self.scheduler.start()
        self.logger = default_logger
        self.lock = threading.Lock()
    
    def register_workflow(
        self,
        name: str,
        description: str = "",
        version: int = 1
    ) -> str:
        """
        Register a new workflow.
        
        :param name: Workflow name
        :param description: Workflow description
        :param version: Initial version
        :return: Workflow ID
        """
        workflow_id = generate_id()
        
        with self.lock:
            workflow = Workflow(
                workflow_id=workflow_id,
                name=name,
                description=description,
                version=version
            )
            
            self.workflows[workflow_id] = workflow
            self.logger.info(f"Registered workflow '{name}' (ID: {workflow_id})")
        
        return workflow_id
    
    def update_workflow(
        self,
        workflow_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Optional[int]:
        """
        Update a workflow's metadata.
        
        :param workflow_id: Workflow ID
        :param name: New name (optional)
        :param description: New description (optional)
        :return: New version number or None if workflow not found
        """
        with self.lock:
            if workflow_id not in self.workflows:
                return None
            
            workflow = self.workflows[workflow_id]
            
            if name is not None:
                workflow.name = name
                
            if description is not None:
                workflow.description = description
            
            workflow.version += 1
            workflow.updated_at = time.time()
            
            self.logger.info(f"Updated workflow '{workflow_id}' to version {workflow.version}")
            return workflow.version
    
    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a workflow by ID.
        
        :param workflow_id: Workflow ID
        :return: Workflow dictionary or None if not found
        """
        with self.lock:
            workflow = self.workflows.get(workflow_id)
            return workflow.to_dict() if workflow else None
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """
        List all workflows.
        
        :return: List of workflow dictionaries
        """
        with self.lock:
            return [workflow.to_dict() for workflow in self.workflows.values()]
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """
        Delete a workflow.
        
        :param workflow_id: Workflow ID
        :return: True if workflow was deleted, False otherwise
        """
        with self.lock:
            if workflow_id not in self.workflows:
                return False
            
            del self.workflows[workflow_id]
            self.logger.info(f"Deleted workflow '{workflow_id}'")
            return True
    
    def add_task_to_workflow(self, workflow_id: str, task: Task) -> bool:
        """
        Add a task to a workflow.
        
        :param workflow_id: Workflow ID
        :param task: Task instance
        :return: True if task was added, False otherwise
        """
        with self.lock:
            if workflow_id not in self.workflows:
                return False
            
            workflow = self.workflows[workflow_id]
            added = workflow.add_task(task)
            
            if added:
                self.logger.info(f"Added task '{task.task_id}' to workflow '{workflow_id}'")
            
            return added
    
    def schedule_workflow(self, workflow_id: str, interval_seconds: float) -> Optional[str]:
        """
        Schedule a workflow to run at regular intervals.
        
        :param workflow_id: Workflow ID
        :param interval_seconds: Interval between executions
        :return: Schedule ID or None if workflow not found
        """
        with self.lock:
            if workflow_id not in self.workflows:
                return None
        
        def run_callback():
            self.run_workflow(workflow_id)
        
        schedule_id = self.scheduler.add_schedule(
            callback=run_callback,
            interval_seconds=interval_seconds
        )
        
        self.logger.info(f"Scheduled workflow '{workflow_id}' every {interval_seconds}s")
        return schedule_id
    
    def run_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Run a workflow.
        
        :param workflow_id: Workflow ID
        :return: Execution results or None if workflow not found
        """
        with self.lock:
            if workflow_id not in self.workflows:
                return None
            
            workflow = self.workflows[workflow_id]
            workflow.status = "running"
            workflow.last_run_at = time.time()
        
        self.logger.info(f"Starting workflow '{workflow_id}' (v{workflow.version})")
        
        execution_order = workflow.get_execution_order()
        results = {}
        success = True
        
        for task_id in execution_order:
            task = workflow.tasks[task_id]
            
            # Skip if any dependencies failed
            deps_ok = True
            for dep_id in task.dependencies:
                if dep_id in results and not results[dep_id]["success"]:
                    deps_ok = False
                    break
            
            if not deps_ok:
                results[task_id] = {
                    "success": False,
                    "error": "Dependency task failed",
                    "status": TaskState.PENDING
                }
                continue
            
            # Run the task
            try:
                task_result = task.run(self.logger)
                
                results[task_id] = {
                    "success": task.state == TaskState.SUCCESS,
                    "result": task_result,
                    "status": task.state
                }
                
                if task.state != TaskState.SUCCESS:
                    success = False
                    error_msg = f"Task {task_id} failed with state {task.state}"
                    results[task_id]["error"] = error_msg
                    self.logger.error(error_msg)
            
            except Exception as e:
                success = False
                error_msg = f"Task {task_id} failed with exception: {str(e)}"
                results[task_id] = {
                    "success": False,
                    "error": error_msg,
                    "status": TaskState.FAILURE
                }
                self.logger.error(error_msg)
        
        with self.lock:
            if workflow_id in self.workflows:
                workflow = self.workflows[workflow_id]
                workflow.status = "success" if success else "failed"
        
        if success:
            self.logger.info(f"Workflow '{workflow_id}' completed successfully")
        else:
            self.logger.error(f"Workflow '{workflow_id}' failed")
        
        return {
            "workflow_id": workflow_id,
            "success": success,
            "task_results": results
        }