from flask import Flask, request, jsonify
from task_manager import WorkflowManager, Task
import utils

app = Flask(__name__)
manager = WorkflowManager()


@app.route('/workflows', methods=['GET'])
def list_workflows():
    wfs = manager.list_workflows()
    result = [
        {"workflow_id": wf.workflow_id, "name": wf.name, "version": wf.version}
        for wf in wfs
    ]
    return jsonify(result), 200


@app.route('/workflows', methods=['POST'])
def create_workflow():
    data = request.get_json() or {}
    missing = utils.require_fields(data, 'name')
    if missing:
        return utils.error_json(f"Missing '{missing}'", 400)
    wid = manager.register_workflow(data['name'])
    return jsonify({"workflow_id": wid}), 201


@app.route('/workflows/<workflow_id>/tasks', methods=['POST'])
def add_task(workflow_id):
    data = request.get_json() or {}
    missing = utils.require_fields(data, 'task_id', 'command')
    if missing:
        return utils.error_json(f"Missing '{missing}'", 400)

    timeout = data.get('timeout')
    task = Task(
        data['task_id'],
        func=lambda cmd=data['command']: eval(cmd, {}),
        timeout=timeout,
        max_retries=data.get('max_retries', 0),
        retry_delay_seconds=data.get('retry_delay_seconds', 0),
        backoff_factor=data.get('backoff_factor', 2),
        dependencies=data.get('dependencies', [])
    )
    try:
        manager.add_task_to_workflow(workflow_id, task)
    except KeyError:
        return utils.error_json("Workflow not found", 404)
    return jsonify({"message": "Task added"}), 201


@app.route('/workflows/<workflow_id>/run', methods=['POST'])
def run_workflow(workflow_id):
    manager.run_workflow(workflow_id)
    return jsonify({"message": "Execution started"}), 200


@app.route('/workflows/<workflow_id>/schedule', methods=['POST'])
def schedule_workflow(workflow_id):
    data = request.get_json() or {}
    missing = utils.require_fields(data, 'interval_seconds')
    if missing:
        return utils.error_json(f"Missing '{missing}'", 400)
    try:
        manager.schedule_workflow(workflow_id, data['interval_seconds'])
    except KeyError:
        return utils.error_json("Workflow not found", 404)
    return jsonify({"message": "Scheduled"}), 200


if __name__ == '__main__':
    app.run(debug=True)
