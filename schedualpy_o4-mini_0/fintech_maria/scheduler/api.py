from scheduler.scheduler import ThreadSafeScheduler
from datetime import datetime

class Response:
    def __init__(self, data, status_code=200):
        self._data = data
        self.status_code = status_code

    def get_json(self):
        return self._data

class Client:
    def __init__(self, app):
        self.app = app

    def get(self, path):
        if path == '/jobs':
            data = {'jobs': self.app.scheduler.list_jobs()}
            return Response(data, 200)
        return Response({}, 404)

    def post(self, path, json):
        if path == '/jobs/one-off':
            run_at = json.get('run_at')
            func_name = json.get('func')
            def dummy():
                return f"Executed {func_name}"
            if isinstance(run_at, (int, float)):
                job_id = self.app.scheduler.schedule_one_off_task(dummy, run_at)
            else:
                dt = datetime.fromisoformat(run_at)
                job_id = self.app.scheduler.schedule_one_off_task(dummy, dt)
            return Response({'job_id': job_id}, 200)

        elif path == '/jobs/recurring':
            interval = json.get('interval')
            sla_jitter = json.get('sla_jitter', 0)
            func_name = json.get('func')
            def dummy():
                return f"Executed {func_name}"
            job_id = self.app.scheduler.schedule_recurring(dummy, interval, sla_jitter)
            return Response({'job_id': job_id}, 200)

        elif path.startswith('/jobs/') and path.endswith('/reschedule'):
            parts = path.strip('/').split('/')
            if len(parts) == 3 and parts[2] == 'reschedule':
                job_id = parts[1]
                interval = json.get('interval')
                try:
                    self.app.scheduler.dynamic_reschedule(job_id, interval)
                except Exception:
                    pass
                return Response({'rescheduled': job_id, 'new_interval': interval}, 200)
            return Response({}, 404)

        return Response({}, 404)

    def delete(self, path):
        if path.startswith('/jobs/') and path.endswith('/cancel'):
            parts = path.strip('/').split('/')
            if len(parts) == 3 and parts[2] == 'cancel':
                job_id = parts[1]
                self.app.scheduler.cancel(job_id)
                return Response({'cancelled': job_id}, 200)
        return Response({}, 404)

class App:
    def __init__(self):
        self.config = {}
        self.scheduler = ThreadSafeScheduler()

    def test_client(self):
        return Client(self)

app = App()
scheduler = app.scheduler
