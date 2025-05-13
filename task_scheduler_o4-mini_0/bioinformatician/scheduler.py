import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class Scheduler:
    def __init__(self):
        self.error_handlers = {}
        self.daily_schedules = {}
        self.cron_schedules = {}
        self.notifications = []
        self.tags = {}
        self.dependencies = {}
        self.exclusions = set()
        self.metrics = {'job_duration': [], 'queue_length': 0, 'error_count': 0}
        self._health_server = None
        self._health_thread = None

    def run_coroutine(self, *coros):
        if not coros:
            return None
        if len(coros) == 1:
            return asyncio.run(coros[0])
        # Wrap multiple coroutines into a single coroutine for asyncio.run
        async def _run_all():
            return await asyncio.gather(*coros)
        return asyncio.run(_run_all())

    def register_error_handler(self, stage, handler):
        self.error_handlers[stage] = handler

    def schedule_daily(self, name, time_str):
        self.daily_schedules[name] = time_str

    def schedule_cron(self, name, cron_expr):
        self.cron_schedules[name] = cron_expr

    def send_notification(self, message, level='info'):
        self.notifications.append({'message': message, 'level': level})

    def add_tag(self, task, tag):
        self.tags[task] = tag

    def define_dependency(self, task, depends_on):
        self.dependencies.setdefault(task, []).append(depends_on)

    def configure_calendar_exclusions(self, dates):
        self.exclusions.update(dates)

    def expose_metrics(self):
        return self.metrics

    def start_health_check(self, host='127.0.0.1', port=0):
        class HealthHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/health':
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'OK')
                else:
                    self.send_response(404)
                    self.end_headers()
            def log_message(self, format, *args):
                return

        server = HTTPServer((host, port), HealthHandler)
        def serve():
            server.serve_forever()
        thread = threading.Thread(target=serve, daemon=True)
        thread.start()
        self._health_server = server
        self._health_thread = thread
        return server.server_address
