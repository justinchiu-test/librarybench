import pytest
import requests
from watcher.plugins.gitlab_ci import GitLabCIPlugin

class DummyResponse:
    pass

def test_on_event(monkeypatch):
    sent = []
    def fake_post(url, data):
        sent.append((url, data))
        return DummyResponse()
    monkeypatch.setattr(requests, 'post', fake_post)
    plugin = GitLabCIPlugin('proj', 'tok')
    plugin.on_event('/f', 'create')
    assert sent
    url, data = sent[0]
    assert 'proj' in url
    assert data['token'] == 'tok'
    assert data['variables[FILE]'] == '/f'
    assert data['variables[EVENT]'] == 'create'
