import uuid
from .flask import Flask, request, jsonify
from .batcher import EventBatcher

app = Flask(__name__)
_watchers = {}

class Watcher:
    def __init__(self, batch_size=10):
        self.id = str(uuid.uuid4())
        self.batcher = EventBatcher(batch_size=batch_size)

    def inject_event(self, event):
        self.batcher.add(event)

    def get_events(self):
        return self.batcher.flush()

@app.route('/start', methods=['POST'])
def start():
    data = request.json or {}
    batch_size = data.get('batch_size', 10)
    w = Watcher(batch_size)
    _watchers[w.id] = w
    return jsonify({"watcher_id": w.id})

@app.route('/inject', methods=['POST'])
def inject():
    data = request.json or {}
    wid = data.get('watcher_id')
    event = data.get('event')
    if wid not in _watchers:
        return jsonify({"error": "Watcher not found"}), 404
    _watchers[wid].inject_event(event)
    return jsonify({"status": "ok"})

@app.route('/results', methods=['GET'])
def results():
    wid = request.args.get('watcher_id')
    if wid not in _watchers:
        return jsonify({"error": "Watcher not found"}), 404
    events = _watchers[wid].get_events()
    return jsonify({"events": events})

@app.route('/stop', methods=['POST'])
def stop():
    data = request.json or {}
    wid = data.get('watcher_id')
    if wid in _watchers:
        del _watchers[wid]
        return jsonify({"status": "stopped"})
    return jsonify({"error": "Watcher not found"}), 404
