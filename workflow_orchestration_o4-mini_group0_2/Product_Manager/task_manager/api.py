from fastapi import FastAPI
from .task_manager import TaskManager
from .utils import get_or_404, assert_true_or_404

app = FastAPI()
manager = TaskManager()


@app.get("/tasks", response_model=list[dict])
def list_tasks():
    """
    List all tasks.
    """
    return manager.list_tasks()


@app.post("/tasks", response_model=dict)
def create_task(task: dict):
    """
    Create a new task.  The body is a free-form dict of task fields.
    """
    return manager.create_task(task)


@app.get("/tasks/{task_id}", response_model=dict)
def read_task(task_id: int):
    """
    Get a single task. 404 if not found.
    """
    task = get_or_404(manager.get_task(task_id), "Task not found")
    return task


@app.put("/tasks/{task_id}", response_model=dict)
def update_task(task_id: int, task: dict):
    """
    Update a task. 404 if not found.
    """
    updated = get_or_404(manager.update_task(task_id, task), "Task not found")
    return updated


@app.delete("/tasks/{task_id}", response_model=dict)
def delete_task(task_id: int):
    """
    Delete a task. 404 if not found.
    Returns {'success': True} on removal.
    """
    assert_true_or_404(manager.delete_task(task_id), "Task not found")
    return {"success": True}
