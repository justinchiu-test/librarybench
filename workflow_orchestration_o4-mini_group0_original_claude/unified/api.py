"""
API interface for the unified workflow orchestration system.
"""
from typing import Any, Dict, List, Optional, Union, Callable
import fastapi
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader
import inspect

from unified.task_manager import TaskManager
from unified.workflow.workflow import Workflow, WorkflowManager
from unified.auth import authenticate_token, USER_TOKENS


# Initialize the API
app = FastAPI(title="Workflow Orchestration API")

# Initialize the task and workflow managers
task_manager = TaskManager()
workflow_manager = WorkflowManager()

# Security
api_key_header = APIKeyHeader(name="X-API-Key")


def api_key_auth(api_key: str = Security(api_key_header)):
    """
    Authenticate API requests using API key.
    """
    if api_key not in USER_TOKENS.values():
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key


# Task routes
@app.post("/tasks", response_model=Dict[str, Any])
def create_task(
    task: Dict[str, Any],
    api_key: str = Depends(api_key_auth)
):
    """
    Create and queue a new task.
    
    The task should have the following properties:
    - function_code: Python code to execute (string)
    - args: List of positional arguments (optional)
    - kwargs: Dictionary of keyword arguments (optional)
    - priority: Task priority (optional, default: 5)
    - timeout: Task timeout in seconds (optional)
    - max_retries: Maximum retry attempts (optional, default: 0)
    - retry_delay_seconds: Initial retry delay (optional, default: 1.0)
    - backoff_factor: Backoff factor (optional, default: 2.0)
    - dependencies: List of task IDs that must complete first (optional)
    """
    try:
        # Validate required fields
        if "function_code" not in task:
            raise ValueError("function_code is required")
        
        # Convert function code string to callable
        function_code = task["function_code"]
        function_locals = {}
        exec(f"def task_function(*args, **kwargs):\n{function_code}", globals(), function_locals)
        func = function_locals["task_function"]
        
        # Queue the task
        task_id = task_manager.queue_task(
            func=func,
            args=task.get("args"),
            kwargs=task.get("kwargs"),
            priority=task.get("priority", 5),
            timeout=task.get("timeout"),
            max_retries=task.get("max_retries", 0),
            retry_delay_seconds=task.get("retry_delay_seconds", 1.0),
            backoff_factor=task.get("backoff_factor", 2.0),
            dependencies=task.get("dependencies")
        )
        
        return {"task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/tasks", response_model=List[Dict[str, Any]])
def list_tasks(api_key: str = Depends(api_key_auth)):
    """
    List all tasks.
    """
    return list(task_manager.get_all_task_metadata().values())


@app.get("/tasks/{task_id}", response_model=Dict[str, Any])
def get_task(task_id: str, api_key: str = Depends(api_key_auth)):
    """
    Get details of a specific task.
    """
    metadata = task_manager.get_task_metadata(task_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Task not found")
    return metadata


@app.delete("/tasks/{task_id}", response_model=Dict[str, bool])
def cancel_task(task_id: str, api_key: str = Depends(api_key_auth)):
    """
    Cancel a task.
    """
    canceled = task_manager.cancel_task(task_id)
    if not canceled:
        raise HTTPException(status_code=404, detail="Task not found or cannot be canceled")
    return {"success": True}


# Schedule routes
@app.post("/schedules", response_model=Dict[str, Any])
def create_schedule(
    schedule: Dict[str, Any],
    api_key: str = Depends(api_key_auth)
):
    """
    Create a new schedule.
    
    The schedule should have the following properties:
    - function_code: Python code to execute (string)
    - interval_seconds: Interval between executions
    - args: List of positional arguments (optional)
    - kwargs: Dictionary of keyword arguments (optional)
    - task_priority: Task priority (optional, default: 5)
    - task_timeout: Task timeout in seconds (optional)
    - task_max_retries: Maximum retry attempts (optional, default: 0)
    - task_retry_delay_seconds: Initial retry delay (optional, default: 1.0)
    - task_backoff_factor: Backoff factor (optional, default: 2.0)
    """
    try:
        # Validate required fields
        if "function_code" not in schedule:
            raise ValueError("function_code is required")
        if "interval_seconds" not in schedule:
            raise ValueError("interval_seconds is required")
        
        # Convert function code string to callable
        function_code = schedule["function_code"]
        function_locals = {}
        exec(f"def schedule_function(*args, **kwargs):\n{function_code}", globals(), function_locals)
        func = function_locals["schedule_function"]
        
        # Create the schedule
        schedule_id = task_manager.schedule_task(
            func=func,
            interval_seconds=schedule["interval_seconds"],
            args=schedule.get("args"),
            kwargs=schedule.get("kwargs"),
            task_priority=schedule.get("task_priority", 5),
            task_timeout=schedule.get("task_timeout"),
            task_max_retries=schedule.get("task_max_retries", 0),
            task_retry_delay_seconds=schedule.get("task_retry_delay_seconds", 1.0),
            task_backoff_factor=schedule.get("task_backoff_factor", 2.0)
        )
        
        return {"schedule_id": schedule_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/schedules", response_model=Dict[str, Dict[str, Any]])
def list_schedules(api_key: str = Depends(api_key_auth)):
    """
    List all schedules.
    """
    return task_manager.scheduler.get_all_schedules()


@app.delete("/schedules/{schedule_id}", response_model=Dict[str, bool])
def cancel_schedule(schedule_id: str, api_key: str = Depends(api_key_auth)):
    """
    Cancel a schedule.
    """
    canceled = task_manager.cancel_schedule(schedule_id)
    if not canceled:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return {"success": True}


# Workflow routes
@app.post("/workflows", response_model=Dict[str, Any])
def create_workflow(
    workflow: Dict[str, Any],
    api_key: str = Depends(api_key_auth)
):
    """
    Create a new workflow.
    
    The workflow should have the following properties:
    - name: Workflow name
    - description: Workflow description (optional)
    - version: Workflow version (optional, default: 1)
    """
    try:
        workflow_id = workflow_manager.register_workflow(
            name=workflow["name"],
            description=workflow.get("description", ""),
            version=workflow.get("version", 1)
        )
        
        return {"workflow_id": workflow_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/workflows", response_model=List[Dict[str, Any]])
def list_workflows(api_key: str = Depends(api_key_auth)):
    """
    List all workflows.
    """
    return workflow_manager.list_workflows()


@app.get("/workflows/{workflow_id}", response_model=Dict[str, Any])
def get_workflow(workflow_id: str, api_key: str = Depends(api_key_auth)):
    """
    Get details of a specific workflow.
    """
    workflow = workflow_manager.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@app.post("/workflows/{workflow_id}/tasks", response_model=Dict[str, bool])
def add_task_to_workflow(
    workflow_id: str,
    task: Dict[str, Any],
    api_key: str = Depends(api_key_auth)
):
    """
    Add a task to a workflow.
    
    The task should have the following properties:
    - function_code: Python code to execute (string)
    - task_id: Task ID (optional, auto-generated if not provided)
    - args: List of positional arguments (optional)
    - kwargs: Dictionary of keyword arguments (optional)
    - priority: Task priority (optional, default: 5)
    - timeout: Task timeout in seconds (optional)
    - max_retries: Maximum retry attempts (optional, default: 0)
    - retry_delay_seconds: Initial retry delay (optional, default: 1.0)
    - backoff_factor: Backoff factor (optional, default: 2.0)
    - dependencies: List of task IDs that must complete first (optional)
    """
    try:
        # Validate required fields
        if "function_code" not in task:
            raise ValueError("function_code is required")
        
        # Convert function code string to callable
        function_code = task["function_code"]
        function_locals = {}
        exec(f"def task_function(*args, **kwargs):\n{function_code}", globals(), function_locals)
        func = function_locals["task_function"]
        
        # Create the task
        from unified.task import Task
        workflow_task = Task(
            task_id=task.get("task_id"),
            func=func,
            args=task.get("args"),
            kwargs=task.get("kwargs"),
            priority=task.get("priority", 5),
            timeout=task.get("timeout"),
            max_retries=task.get("max_retries", 0),
            retry_delay_seconds=task.get("retry_delay_seconds", 1.0),
            backoff_factor=task.get("backoff_factor", 2.0),
            dependencies=task.get("dependencies", [])
        )
        
        # Add to workflow
        workflow_manager.add_task_to_workflow(workflow_id, workflow_task)
        
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/workflows/{workflow_id}/schedule", response_model=Dict[str, Any])
def schedule_workflow(
    workflow_id: str,
    schedule: Dict[str, Any],
    api_key: str = Depends(api_key_auth)
):
    """
    Schedule a workflow to run at regular intervals.
    
    The schedule should have the following properties:
    - interval_seconds: Interval between executions
    """
    try:
        if "interval_seconds" not in schedule:
            raise ValueError("interval_seconds is required")
        
        schedule_id = workflow_manager.schedule_workflow(
            workflow_id=workflow_id,
            interval_seconds=schedule["interval_seconds"]
        )
        
        return {"schedule_id": schedule_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/workflows/{workflow_id}/run", response_model=Dict[str, Any])
def run_workflow(workflow_id: str, api_key: str = Depends(api_key_auth)):
    """
    Run a workflow immediately.
    """
    try:
        result = workflow_manager.run_workflow(workflow_id)
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Health check
@app.get("/health")
def health_check():
    """
    Health check endpoint (no authentication required).
    """
    return {"status": "healthy", "version": "1.0.0"}