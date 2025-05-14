from scheduler.scheduler import Scheduler
from flask import request

scheduler = Scheduler()

def trigger_task():
    data = request.get_json() or {}
    name = data.get('task')
    try:
        result = scheduler.run(name)
        return {'status': 'success', 'result': result}, 200
    except Exception as e:
        scheduler.send_alert('slack', str(e))
        return {'status': 'error', 'error': str(e)}, 500

scheduler.create_api_endpoint('/run', ['POST'], trigger_task)

def query_logs():
    return {'logs': []}, 200

scheduler.create_api_endpoint('/logs', ['GET'], query_logs)

def cancel_task():
    scheduler.graceful_shutdown()
    return {'status': 'cancelled'}, 200

scheduler.create_api_endpoint('/cancel', ['POST'], cancel_task)

app = scheduler.app
