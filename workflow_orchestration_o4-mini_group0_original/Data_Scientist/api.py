from flask import Flask, request, jsonify
from Data_Scientist.task_manager import WorkflowManager, Task

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
    name = data.get('name')
    if not name:
        return jsonify({"error": "Missing 'name'"}), 400
    wid = manager.register_workflow(name)
    return jsonify({"workflow_id": wid}), 201

@app.route('/workflows/<workflow_id>/tasks', methods=['POST'])
def add_task(workflow_id):
    data = request.get_json() or {}
    task_id = data.get('task_id')
    command = data.get('command')
    if not task_id or not command:
        return jsonify({"error": "Missing 'task_id' or 'command'"}), 400

    timeout = data.get('timeout')
    max_retries = data.get('max_retries', 0)
    retry_delay = data.get('retry_delay_seconds', 0)
    backoff = data.get('backoff_factor', 2)
    dependencies = data.get('dependencies', [])

    # Simple eval-based command execution
    def func():
        return eval(command, {})

    task = Task(
        task_id, func,
        timeout=timeout,
        max_retries=max_retries,
        retry_delay_seconds=retry_delay,
        backoff_factor=backoff,
        dependencies=dependencies
    )
    try:
        manager.add_task_to_workflow(workflow_id, task)
    except KeyError:
        return jsonify({"error": "Workflow not found"}), 404
    return jsonify({"message": "Task added"}), 201

@app.route('/workflows/<workflow_id>/run', methods=['POST'])
def run_workflow(workflow_id):
    manager.run_workflow(workflow_id)
    return jsonify({"message": "Execution started"}), 200

@app.route('/workflows/<workflow_id>/schedule', methods=['POST'])
def schedule_workflow(workflow_id):
    data = request.get_json() or {}
    interval = data.get('interval_seconds')
    if interval is None:
        return jsonify({"error": "Missing 'interval_seconds'"}), 400
    try:
        manager.schedule_workflow(workflow_id, interval)
    except KeyError:
        return jsonify({"error": "Workflow not found"}), 404
    return jsonify({"message": "Scheduled"}), 200

if __name__ == '__main__':
    app.run(debug=True)
