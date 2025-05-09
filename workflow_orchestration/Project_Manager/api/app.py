from flask import Flask, jsonify, request
from core.workflow import Workflow
from core.task import Task
from core.queue import TaskQueue
from core.logger import logger

app = Flask(__name__)
workflows = {}
queue = TaskQueue()
queue.start()

@app.route("/workflows/<name>/run", methods=["POST"])
def run_workflow(name):
    wf = workflows.get(name)
    if not wf:
        return jsonify({"error": "Workflow not found"}), 404
    queue.enqueue(wf)
    return jsonify({"status": "queued", "workflow": name, "version": wf.version}), 202

@app.route("/workflows/<name>/status", methods=["GET"])
def workflow_status(name):
    wf = workflows.get(name)
    if not wf:
        return jsonify({"error": "Workflow not found"}), 404
    return jsonify({
        "name": wf.name,
        "version": wf.version,
        "last_status": wf.last_status,
        "details": wf.last_run_details
    }), 200

@app.route("/workflows", methods=["POST"])
def create_workflow():
    data = request.json
    name = data.get("name")
    tasks_data = data.get("tasks", [])
    if name in workflows:
        return jsonify({"error": "Workflow already exists"}), 400
    wf = Workflow(name)
    for td in tasks_data:
        # tasks_data items: {"name":..., "func": code not supported via API}
        return jsonify({"error": "Direct task definitions via API not supported"}), 400
    workflows[name] = wf
    return jsonify({"status": "created", "name": name}), 201

if __name__ == "__main__":
    # Example workflow for manual testing
    from core.task import Task
    wf = Workflow("example")
    wf.add_task(Task("task1", func=lambda: print("Hello"), timeout=5))
    workflows["example"] = wf
    app.run(debug=True)
