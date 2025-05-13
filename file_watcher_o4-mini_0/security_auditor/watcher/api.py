from .snapshot import Snapshot

events = []
snapshots = []

try:
    from flask import Flask, jsonify, request
    HAVE_FLASK = True
except ImportError:
    HAVE_FLASK = False

if HAVE_FLASK:
    app = Flask(__name__)

    @app.route('/events', methods=['GET'])
    def get_events():
        return jsonify(events)

    @app.route('/snapshot', methods=['POST'])
    def new_snapshot():
        data = request.json or {}
        root = data.get('root')
        if not root:
            return jsonify({"error": "Missing 'root' parameter"}), 400
        snap_obj = Snapshot(root)
        snap = snap_obj.take()
        diff = {}
        if snapshots:
            diff = Snapshot.diff(snapshots[-1], snap)
        snapshots.append(snap)
        event = {"root": root, "diff": diff}
        events.append(event)
        return jsonify({"snapshot": snap, "diff": diff})
else:
    class Response:
        def __init__(self, data, status=200):
            self._data = data
            self.status_code = status

        @property
        def json(self):
            return self._data

    class Client:
        def __enter__(self):
            # Support context manager protocol in tests
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            # No special teardown logic
            return False

        def get(self, path):
            if path == '/events':
                return Response(events, 200)
            return Response(None, 404)

        def post(self, path, json=None):
            if path != '/snapshot':
                return Response(None, 404)
            data = json or {}
            root = data.get('root')
            if not root:
                return Response({"error": "Missing 'root' parameter"}, 400)
            snap_obj = Snapshot(root)
            snap = snap_obj.take()
            diff = {}
            if snapshots:
                diff = Snapshot.diff(snapshots[-1], snap)
            snapshots.append(snap)
            event = {"root": root, "diff": diff}
            events.append(event)
            return Response({"snapshot": snap, "diff": diff}, 200)

    class FakeApp:
        def __init__(self):
            self.config = {}

        def test_client(self):
            return Client()

    app = FakeApp()
