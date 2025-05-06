from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .workflow import Workflow
from .workflow_manager import workflow_manager
from .scheduler import scheduler
from .queue import TaskQueue

app = FastAPI()
task_queue = TaskQueue()

class WorkflowIn(BaseModel):
    name: str

class ScheduleIn(BaseModel):
    seconds: float

@app.post("/workflows")
def create_workflow(payload: WorkflowIn):
    wf = Workflow(payload.name)
    workflow_manager.register(wf)
    return {"name": wf.name, "version": wf.version}

@app.get("/workflows")
def list_workflows():
    return [{"name": w.name, "version": w.version}
            for w in workflow_manager.workflows]

@app.post("/workflows/{name}/{version}/run")
def run_workflow(name: str, version: int):
    wf = workflow_manager.get(name, version)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    task_queue.push(lambda: wf.run())
    return {"status": "scheduled"}

@app.post("/workflows/{name}/{version}/schedule")
def schedule_workflow(name: str, version: int, payload: ScheduleIn):
    wf = workflow_manager.get(name, version)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    scheduler.schedule(payload.seconds, lambda: wf.run())
    return {"interval": payload.seconds, "status": "scheduled"}
