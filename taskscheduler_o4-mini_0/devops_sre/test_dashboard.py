import pytest
from scheduler.dashboard import app, add_upcoming, add_history, add_retry

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

def test_empty_dashboard(client):
    resp = client.get('/jobs')
    assert resp.status_code == 200
    assert resp.get_json() == []
    resp = client.get('/history')
    assert resp.get_json() == []
    resp = client.get('/retries')
    assert resp.get_json() == []

def test_add_and_get_dashboard(client):
    add_upcoming({'job':'u1'})
    add_history({'job':'h1'})
    add_retry({'job':'r1'})
    assert client.get('/jobs').get_json() == [{'job':'u1'}]
    assert client.get('/history').get_json() == [{'job':'h1'}]
    assert client.get('/retries').get_json() == [{'job':'r1'}]
