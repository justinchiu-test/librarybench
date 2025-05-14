from flask import Flask, request, jsonify, abort
from db import Database
from metrics import Metrics
from hooks import Hooks

def create_app(db_path=None, key=None):
    app = Flask(__name__)
    metrics = Metrics()
    hooks = Hooks()
    db = Database(db_path or './data', key or b'\x00' * 32, metrics, hooks)

    @app.before_request
    def before_request():
        metrics.increment('request_count')

    @app.route('/health')
    def health():
        return jsonify({'status': 'ok'})

    @app.route('/metrics')
    def metrics_endpoint():
        text, status, headers = metrics.expose()
        return text, status, headers

    @app.route('/events', methods=['POST'])
    def insert_event():
        data = request.get_json()
        ev = db.insert_event(data)
        # return the raw dict so Flask will jsonify it properly
        return ev, 201

    @app.route('/events/batch', methods=['POST'])
    def batch():
        events = request.get_json()
        res = db.batch_upsert(events)
        # return the raw list so Flask will jsonify it properly
        return res, 201

    @app.route('/events/<id>', methods=['GET'])
    def get_event(id):
        ev = db.get_event(id)
        if not ev:
            abort(404)
        return jsonify(ev)

    @app.route('/events/<id>', methods=['PUT'])
    def update(id):
        data = request.get_json()
        ev = db.update_event(id, data)
        if not ev:
            abort(404)
        return jsonify(ev)

    @app.route('/events/<id>', methods=['DELETE'])
    def delete(id):
        soft = request.args.get('soft', 'true') == 'true'
        if soft:
            ok = db.soft_delete(id)
        else:
            ok = db.purge_event(id)
        if not ok:
            abort(404)
        return '', 204

    @app.route('/events/<id>/undelete', methods=['POST'])
    def undelete(id):
        ok = db.undelete_event(id)
        if not ok:
            abort(404)
        return '', 204

    @app.route('/events/<id>/versions', methods=['GET'])
    def versions(id):
        vers = db.get_versions(id)
        if vers is None:
            abort(404)
        return jsonify({'versions': vers})

    @app.route('/events/<id>/versions/<int:ver>', methods=['POST'])
    def restore(id, ver):
        ev = db.restore_version(id, ver)
        if not ev:
            abort(404)
        return jsonify(ev)

    @app.route('/events', methods=['GET'])
    def query():
        campaign = request.args.get('campaign')
        start = request.args.get('start')
        end = request.args.get('end')
        res = db.query(campaign, start, end)
        return jsonify(res)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()
