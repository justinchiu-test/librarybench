from datetime import datetime
from iotscheduler.scheduler import ThreadSafeScheduler

scheduler = ThreadSafeScheduler()
is_dummy = False

try:
    # Attempt real Flask import
    from flask import Flask, request, jsonify, abort
    app = Flask(__name__)
except ImportError:
    # Minimal dummy Flask-like framework for testing without Flask installed
    from types import SimpleNamespace

    is_dummy = True

    class DummyResponse:
        def __init__(self, data=None, status_code=200):
            self._data = data
            self.status_code = status_code

        def get_json(self):
            return self._data

    class AbortException(Exception):
        def __init__(self, code):
            self.code = code

    def abort(code):
        raise AbortException(code)

    def jsonify(data):
        return DummyResponse(data)

    class DummyRequest:
        def __init__(self, json_data):
            self._json = json_data

        def get_json(self):
            return self._json

    class DummyApp:
        def __init__(self):
            self.routes = []

        def route(self, path, methods):
            def decorator(func):
                self.routes.append((path, methods, func))
                return func
            return decorator

        def test_client(self):
            return DummyClient(self)

    class DummyClient:
        def __init__(self, app):
            self.app = app

        def open(self, method, url, json=None):
            # find matching route
            for path, methods, func in self.app.routes:
                if method not in methods:
                    continue
                # match path template with actual url
                tpl_parts = path.strip("/").split("/")
                url_parts = url.strip("/").split("/")
                if len(tpl_parts) != len(url_parts):
                    continue
                params = {}
                matched = True
                for tp, up in zip(tpl_parts, url_parts):
                    if tp.startswith("<") and tp.endswith(">"):
                        key = tp[1:-1]
                        params[key] = up
                    elif tp != up:
                        matched = False
                        break
                if not matched:
                    continue
                # prepare request
                import iotscheduler.api as api_mod
                api_mod.request = DummyRequest(json)
                try:
                    rv = func(**params)
                except AbortException as e:
                    return DummyResponse(None, e.code)
                # process return value
                status = 200
                if isinstance(rv, tuple) and len(rv) == 2:
                    body, status = rv
                    if isinstance(body, DummyResponse):
                        body.status_code = status
                        return body
                    return DummyResponse(body, status)
                if isinstance(rv, DummyResponse):
                    return rv
                return DummyResponse(rv, status)
            # no route found
            return DummyResponse(None, 404)

        def get(self, url):
            return self.open("GET", url)

        def post(self, url, json=None):
            return self.open("POST", url, json=json)

        def delete(self, url):
            return self.open("DELETE", url)

    app = DummyApp()

# Define routes
@app.route("/tasks", methods=["GET"])
def list_tasks():
    if not is_dummy:
        with scheduler._lock:
            return jsonify(scheduler.tasks)
    return jsonify(scheduler.tasks)

@app.route("/tasks/oneoff", methods=["POST"])
def create_oneoff():
    data = request.get_json() or {}
    delay = data.get("delay")
    run_at = data.get("run_at")
    # for demonstration, tasks just no-op
    def noop():
        pass
    run_at_dt = None
    if run_at:
        try:
            run_at_dt = datetime.fromisoformat(run_at)
        except Exception:
            run_at_dt = None
    task_id = scheduler.schedule_one_off_task(
        data.get("task_id"), run_at_dt, delay, noop
    )
    resp = jsonify({"task_id": task_id})
    return resp, 201

@app.route("/tasks/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    try:
        scheduler.cancel(task_id)
    except Exception:
        abort(404)
    return "", 204

@app.route("/tasks/<task_id>/reschedule", methods=["POST"])
def reschedule_task(task_id):
    data = request.get_json() or {}
    cron = data.get("cron")
    interval = data.get("interval")
    try:
        scheduler.dynamic_reschedule(task_id, cron_expr=cron, interval=interval)
    except KeyError:
        abort(404)
    return "", 204
