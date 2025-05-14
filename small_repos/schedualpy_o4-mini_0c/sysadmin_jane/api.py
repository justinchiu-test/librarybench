from flask import Flask, request, jsonify
from scheduler import ThreadSafeScheduler

app = Flask(__name__)
scheduler = ThreadSafeScheduler()
scheduler.start()

@app.route('/jobs', methods=['GET'])
def list_jobs():
    return jsonify(scheduler.list_jobs()), 200

@app.route('/jobs', methods=['POST'])
def create_job():
    data = request.json or {}
    jtype = data.get('type')
    func_name = data.get('func', 'noop')
    func = getattr(ThreadSafeScheduler, func_name, None) or getattr(scheduler, func_name, None)
    if not callable(func):
        return jsonify({'error': 'invalid func'}), 400
    if jtype == 'interval':
        interval = data.get('interval')
        if interval is None:
            return jsonify({'error': 'missing interval'}), 400
        job_id = scheduler.schedule_interval(func, interval)
    elif jtype == 'cron':
        expr = data.get('cron')
        if expr is None:
            return jsonify({'error': 'missing cron'}), 400
        job_id = scheduler.schedule_cron(func, expr)
    elif jtype == 'once':
        run_at = data.get('run_at')
        delay = data.get('delay')
        job_id = scheduler.schedule_one_off_task(func, run_at=None, delay=delay)
    else:
        return jsonify({'error': 'invalid type'}), 400
    return jsonify({'job_id': job_id}), 201

@app.route('/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    job = scheduler.get_job(job_id)
    if job is None:
        return jsonify({'error': 'not found'}), 404
    return jsonify(job), 200

@app.route('/jobs/<job_id>', methods=['PUT'])
def update_job(job_id):
    data = request.json or {}
    try:
        scheduler.dynamic_reschedule(job_id, interval=data.get('interval'), cron_expr=data.get('cron'))
    except KeyError:
        return jsonify({'error': 'not found'}), 404
    return jsonify({'status': 'rescheduled'}), 200

@app.route('/jobs/<job_id>', methods=['DELETE'])
def delete_job(job_id):
    ok = scheduler.cancel_job(job_id)
    if not ok:
        return jsonify({'error': 'not found'}), 404
    return jsonify({'status': 'deleted'}), 200

if __name__ == '__main__':
    app.run()
