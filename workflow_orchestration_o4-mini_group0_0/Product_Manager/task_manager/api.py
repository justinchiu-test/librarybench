from flask import Flask, request
from task_manager import WorkflowManager, Task
from utils import require_fields, flask_json_response, flask_error

app = Flask(__name__)
manager = WorkflowManager()

@app.route('/workflows', methods=['GET'])
def list_workflows():
    wfs = manager.list_workflows()
    result = [
        {"workflow_id": wf.workflow_id, "name": wf.name, "version": wf.version}
        for wf in wfs
    ]
    return flask_json_response(result, 200)

@app.route('/workflows', methods=['POST'])
def create_workflow():
    data = request.get_json() or {}
    ok, err = require_fields(data, 'name')
    if not ok:
        return flask_error(err, 400)
    wid = manager.register_workflow(data['name'])
    return flask_json_response({"workflow_id": wid}, 201)

@app.route('/workflows/<workflow_id>/tasks', methods=['POST'])
def add_task(workflow_id):
    data = request.get_json() or {}
    ok, err = require_fields(data, 'task_id', 'command')
    if not ok:
        return flask_error(err, 400)

    timeout = data.get('timeout')
    max_retries = data.get('max_retries', 0)
    retry_delay = data.get('retry_delay_seconds', 0)
    backoff = data.get('backoff_factor', 2)
    dependencies = data.get('dependencies', [])

    def func():
        return eval(data['command'], {})

    task = Task(
        data['task_id'], func,
        timeout=timeout,
        max_retries=max_retries,
        retry_delay_seconds=retry_delay,
        backoff_factor=backoff,
        dependencies=dependencies
    )
    try:
        manager.add_task_to_workflow(workflow_id, task)
    except KeyError:
        return flask_error("Workflow not found", 404)
    return flask_json_response({"message": "Task added"}, 201)

@app.route('/workflows/<workflow_id>/run', methods=['POST'])
def run_workflow(workflow_id):
    manager.run_workflow(workflow_id)
    return flask_json_response({"message": "Execution started"}, 200)

@app.route('/workflows/<workflow_id>/schedule', methods=['POST'])
def schedule_workflow(workflow_id):
    data = request.get_json() or {}
    ok, err = require_fields(data, 'interval_seconds')
    if not ok:
        return flask_error(err, 400)
    try:
        manager.schedule_workflow(workflow_id, data['interval_seconds'])
    except KeyError:
        return flask_error("Workflow not found", 404)
    return flask_json_response({"message": "Scheduled"}, 200)

if __name__ == '__main__':
    app.run(debug=True)
