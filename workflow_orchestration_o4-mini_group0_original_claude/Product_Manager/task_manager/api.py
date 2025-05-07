from fastapi import FastAPI, HTTPException
from Product_Manager.task_manager.task_manager import TaskManager

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
    Get a single task.  404 if not found.
    """
    t = manager.get_task(task_id)
    if t is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return t


@app.put("/tasks/{task_id}", response_model=dict)
def update_task(task_id: int, task: dict):
    """
    Update a task.  404 if not found.
    """
    t = manager.update_task(task_id, task)
    if t is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return t


@app.delete("/tasks/{task_id}", response_model=dict)
def delete_task(task_id: int):
    """
    Delete a task.  404 if not found.
    Returns {'success': True} on removal.
    """
    ok = manager.delete_task(task_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"success": True}
