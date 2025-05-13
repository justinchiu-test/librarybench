import pytest
from scheduler.api import start_api_server

@pytest.fixture
def client():
    app = start_api_server()
    app.testing = True
    return app.test_client()

def test_health_endpoint(client):
    resp = client.get('/health')
    assert resp.status_code == 200
    assert resp.data == b'ok'
