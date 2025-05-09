from fastapi import FastAPI, HTTPException
from src.scheduler import WorkflowManager, Scheduler, Workflow, Task
from typing import Dict, Any, List

app = FastAPI()
manager = WorkflowManager()


@app.get("/healthz")
async def healthz() -> Dict[str, str]:
    """
    Healthcheck endpoint.
    """
    return {"status": "ok"}


@app.post("/workflows")
async def submit_workflow(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Submit (or update) a workflow.  Expects a JSON body like:
      {
        "id": "workflow1",
        "tasks": [
          {"id": "A", "dependencies": []},
          {"id": "B", "dependencies": ["A"]}
        ]
      }
    """
    # basic validation
    wf_id = payload.get("id")
    tasks_data = payload.get("tasks")
    if not wf_id or not isinstance(tasks_data, list):
        raise HTTPException(status_code=400, detail="Invalid workflow payload")

    # build Task objects
    tasks: List[Task] = []
    for td in tasks_data:
        tid = td.get("id")
        deps = td.get("dependencies", td.get("depends_on", []))
        if not tid or not isinstance(deps, list):
            raise HTTPException(status_code=400, detail="Invalid task definition")
        tasks.append(Task(id=tid, dependencies=deps))

    # register & run
    wf = Workflow(id=wf_id, tasks=tasks)
    manager.register_workflow(wf)
    sched = Scheduler(manager)
    sched.run(wf_id)

    # return summary
    return {
        "workflow_id": wf.id,
        "version": manager.get_version(wf.id),
        "tasks": [{"id": t.id, "status": t.status} for t in wf.tasks.values()],
    }


@app.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str) -> Dict[str, Any]:
    """
    Retrieve a submitted workflow's status.
    """
    if workflow_id not in manager.workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    wf = manager.workflows[workflow_id]
    return {
        "workflow_id": wf.id,
        "version": manager.get_version(wf.id),
        "tasks": [{"id": t.id, "status": t.status} for t in wf.tasks.values()],
    }
