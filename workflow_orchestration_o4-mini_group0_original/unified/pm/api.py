from flask import Flask, request, jsonify
import time
from unified.pm.task_manager import TaskManager

app = Flask(__name__)
manager = TaskManager()

# simple mapping of task names to actual functions
def add(a, b):
    return a + b

TASK_FUNCTIONS = {
    'add': add,
    'sleep': time.sleep,
}

@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json() or {}
    name = data.get('task_name')
    args = data.get('args', [])
    timeout = data.get('timeout')
    max_retries = data.get('max_retries', 0)
    retry_delay_seconds = data.get('retry_delay_seconds', 0)
    func = TASK_FUNCTIONS.get(name)
    if func is None:
        return jsonify({'error': 'Unknown task_name'}), 400
    tid = manager.queue_task(
        func,
        args=tuple(args),
        timeout=timeout,
        max_retries=max_retries,
        retry_delay_seconds=retry_delay_seconds
    )
    return jsonify({'task_id': tid}), 202

@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    meta = manager.get_task_metadata(task_id)
    if meta is None:
        return jsonify({'error': 'Task not found'}), 404
    return jsonify(meta), 200

@app.route('/tasks/<int:task_id>/cancel', methods=['POST'])
def cancel_task(task_id):
    ok = manager.cancel_task(task_id)
    if not ok:
        return jsonify({'error': 'Task not found or cannot cancel'}), 404
    return jsonify({'success': True}), 200

@app.route('/tasks/<int:task_id>/timeout', methods=['POST'])
def set_timeout(task_id):
    data = request.get_json() or {}
    timeout = data.get('timeout')
    if timeout is None:
        return jsonify({'error': 'Missing timeout'}), 400
    meta = manager.tasks.get(task_id)
    if meta is None:
        return jsonify({'error': 'Task not found'}), 404
    # update timeout and mark as timed out
    meta['timeout'] = timeout
    meta['status'] = 'timeout'
    return jsonify({'success': True}), 200