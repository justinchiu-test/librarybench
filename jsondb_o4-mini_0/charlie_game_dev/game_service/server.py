from flask import Flask, request, jsonify
from .storage import GameStore

app = Flask(__name__)
store = GameStore('store', encryption_key=None, enable_journal=True)

@app.route('/profile', methods=['POST'])
def create_profile():
    content = request.json or {}
    pid = content.get('id')
    if not pid:
        return jsonify({'error': 'id required'}), 400
    data = store.load()
    if pid in data:
        return jsonify({'error': 'exists'}), 400
    data[pid] = {'inventory': [], 'stats': {}, 'achievements': []}
    initial = content.get('initial', {})
    data[pid].update(initial)
    store.save(data)
    return jsonify(data[pid]), 201

@app.route('/leaderboard', methods=['GET'])
def leaderboard():
    data = store.load()
    lb = sorted(
        ((pid, info.get('stats', {}).get('score', 0)) for pid, info in data.items()),
        key=lambda x: -x[1]
    )
    return jsonify(lb), 200

@app.route('/admin/settings', methods=['PUT'])
def admin_settings():
    settings = request.json or {}
    data = store.load()
    data['_settings'] = settings
    store.save(data)
    return jsonify(settings), 200

if __name__ == '__main__':
    app.run()
