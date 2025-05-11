import pytest
from charlie_game_dev.game_service.server import app
from charlie_game_dev.game_service.storage import GameStore

@pytest.fixture(autouse=True)
def client(tmp_path, monkeypatch):
    new_store = GameStore(str(tmp_path))
    monkeypatch.setattr('game_service.server.store', new_store)
    return app.test_client()

def test_create_profile(client):
    resp = client.post('/profile', json={'id': 'u1'})
    assert resp.status_code == 201
    data = resp.get_json()
    assert 'inventory' in data

def test_duplicate_profile(client):
    client.post('/profile', json={'id': 'u1'})
    resp = client.post('/profile', json={'id': 'u1'})
    assert resp.status_code == 400

def test_leaderboard(client):
    client.post('/profile', json={'id': 'u1', 'initial': {'stats': {'score': 10}}})
    client.post('/profile', json={'id': 'u2', 'initial': {'stats': {'score': 5}}})
    resp = client.get('/leaderboard')
    lb = resp.get_json()
    assert lb[0][0] == 'u1'

def test_admin_settings(client):
    settings = {'mode': 'hard'}
    resp = client.put('/admin/settings', json=settings)
    assert resp.status_code == 200
    assert resp.get_json() == settings
