import pytest
from mock_server import MockServer, Response
from http_client import HttpClient

def test_retry_exceeds_limit():
    server = MockServer()
    client = HttpClient(server)
    def handler(req):
        raise ConnectionResetError()
    server.registerEndpoint('DELETE', '/del', handler)
    client.setRetryPolicy('DELETE', '/del', retries=2, backoff=0)
    with pytest.raises(ConnectionResetError):
        client.delete('/del')
