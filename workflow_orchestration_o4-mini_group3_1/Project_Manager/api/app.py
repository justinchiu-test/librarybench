from flask import Flask, request
from core.workflow import Workflow
from core.task import Task
from core.queue import TaskQueue
from core.logger import logger
from utils import json_response, error_response

app = Flask(__name__)
workflows = {}
queue = TaskQueue()
queue.start()

@app.route("/workflows/<name>/run", methods=["POST"])
def run_workflow(name):
    wf = workflows.get(name)
    if not wf:
        return error_response("Workflow not found", 404)
    queue.enqueue(wf)
    return json_response(
        {"status": "queued", "workflow": name, "version": wf.version},
        202
    )

@app.route("/workflows/<name>/status", methods=["GET"])
def workflow_status(name):
    wf = workflows.get(name)
    if not wf:
        return error_response("Workflow not found", 404)
    return json_response({
        "name": wf.name,
        "version": wf.version,
        "last_status": wf.last_status,
        "details": wf.last_run_details
    }, 200)

@app.route("/workflows", methods=["POST"])
def create_workflow():
    data = request.json or {}
    name = data.get("name")
    if not name:
        return error_response("Name is required", 400)
    if name in workflows:
        return error_response("Workflow already exists", 400)
    # direct API task definitions not supported
    if data.get("tasks"):
        return error_response(
            "Direct task definitions via API not supported", 400
        )
    wf = Workflow(name)
    workflows[name] = wf
    return json_response({"status": "created", "name": name}, 201)

if __name__ == "__main__":
    from core.task import Task
    wf = Workflow("example")
    wf.add_task(Task("task1", func=lambda: print("Hello"), timeout=5))
    workflows["example"] = wf
    app.run(debug=True)
