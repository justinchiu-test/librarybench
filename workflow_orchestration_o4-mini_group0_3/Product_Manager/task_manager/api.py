from flask import Flask
from .task_manager import WorkflowManager, Task
from utils import parse_json, require_fields, ok, error

app = Flask(__name__)
manager = WorkflowManager()

@app.route('/workflows', methods=['GET'])
def list_workflows():
    wfs = manager.list_workflows()
    result = [
        {"workflow_id": wf.workflow_id, "name": wf.name, "version": wf.version}
        for wf in wfs
    ]
    return ok(result)

@app.route('/workflows', methods=['POST'])
def create_workflow():
    data = parse_json()
    try:
        [name] = require_fields(data, 'name')
    except ValueError as e:
        return error(str(e), 400)
    wid = manager.register_workflow(name)
    return ok({"workflow_id": wid}, 201)

@app.route('/workflows/<workflow_id>/tasks', methods=['POST'])
def add_task(workflow_id):
    data = parse_json()
    try:
        task_id, command = require_fields(data, 'task_id', 'command')
    except ValueError as e:
        return error(str(e), 400)

    timeout   = data.get('timeout')
    retries   = data.get('max_retries', 0)
    delay     = data.get('retry_delay_seconds', 0)
    backoff   = data.get('backoff_factor', 2)
    deps      = data.get('dependencies', [])

    # wrap the command in a callable
    def func():
        return eval(command, {})

    task = Task(
        task_id, func,
        timeout=timeout,
        max_retries=retries,
        retry_delay_seconds=delay,
        backoff_factor=backoff,
        dependencies=deps
    )
    try:
        manager.add_task_to_workflow(workflow_id, task)
    except KeyError:
        return error("Workflow not found", 404)
    return ok({"message": "Task added"}, 201)

@app.route('/workflows/<workflow_id>/run', methods=['POST'])
def run_workflow(workflow_id):
    manager.run_workflow(workflow_id)
    return ok({"message": "Execution started"})

@app.route('/workflows/<workflow_id>/schedule', methods=['POST'])
def schedule_workflow(workflow_id):
    data = parse_json()
    if 'interval_seconds' not in data:
        return error("Missing 'interval_seconds'", 400)
    try:
        manager.schedule_workflow(workflow_id, data['interval_seconds'])
    except KeyError:
        return error("Workflow not found", 404)
    return ok({"message": "Scheduled"})
