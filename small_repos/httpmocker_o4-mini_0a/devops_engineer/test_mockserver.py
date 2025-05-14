import re
import pytest
from mockserver import MockServer

def test_register_endpoint():
    server = MockServer()
    def handler(req): return "ok"
    server.registerEndpoint('GET', '/test', handler)
    assert len(server.endpoints) == 1
    ep = server.endpoints[0]
    assert ep['method'] == 'GET'
    assert ep['path'] == '/test'
    assert ep['handler'] is handler

def test_register_endpoint_invalid_method():
    server = MockServer()
    with pytest.raises(TypeError):
        server.registerEndpoint(123, '/path', lambda x: x)

def test_register_endpoint_invalid_path():
    server = MockServer()
    with pytest.raises(TypeError):
        server.registerEndpoint('GET', 123, lambda x: x)

def test_register_endpoint_invalid_handler():
    server = MockServer()
    with pytest.raises(TypeError):
        server.registerEndpoint('GET', '/path', "not_callable")

def test_register_endpoint_regex():
    server = MockServer()
    pattern = re.compile(r'/item/\d+')
    def handler(req): return "ok"
    server.registerEndpoint('POST', pattern, handler)
    assert server.endpoints[0]['path'] is pattern

def test_assert_header_basic():
    server = MockServer()
    server.assertHeader('X-Test', value='val')
    assert len(server.header_assertions) == 1
    ha = server.header_assertions[0]
    assert ha['name'] == 'X-Test'
    assert ha['value'] == 'val'
    assert ha['pattern'] is None
    assert ha['predicate'] is None

def test_assert_header_invalid_name():
    server = MockServer()
    with pytest.raises(TypeError):
        server.assertHeader(123)

def test_assert_body():
    server = MockServer()
    schema = {'type': 'object'}
    pred = lambda b: True
    server.assertBody(schema=schema, predicate=pred)
    assert len(server.body_assertions) == 1
    ba = server.body_assertions[0]
    assert ba['schema'] is schema
    assert ba['predicate'] is pred

def test_configure_cors_defaults():
    server = MockServer()
    server.configureCORS()
    cors = server.cors_config
    assert cors['allow_origins'] == []
    assert cors['allow_methods'] == []
    assert cors['allow_headers'] == []
    assert cors['allow_credentials'] is False

def test_configure_cors_custom():
    server = MockServer()
    server.configureCORS(allow_origins=['*'], allow_methods=['GET'], allow_headers=['X'], allow_credentials=True)
    cors = server.cors_config
    assert cors == {
        'allow_origins': ['*'],
        'allow_methods': ['GET'],
        'allow_headers': ['X'],
        'allow_credentials': True
    }

def test_configure_cors_invalid_types():
    server = MockServer()
    with pytest.raises(TypeError):
        server.configureCORS(allow_origins='notalist')
    with pytest.raises(TypeError):
        server.configureCORS(allow_methods='notalist')
    with pytest.raises(TypeError):
        server.configureCORS(allow_headers='notalist')
    with pytest.raises(TypeError):
        server.configureCORS(allow_credentials='notabool')

def test_simulate_auth_basic():
    server = MockServer()
    creds = {'user': 'pass'}
    server.simulateAuth('Basic', credentials=creds)
    assert server.auth_simulations[0] == {'type': 'Basic', 'credentials': creds}

def test_simulate_auth_invalid():
    server = MockServer()
    with pytest.raises(ValueError):
        server.simulateAuth('Unknown')

def test_mock_websocket():
    server = MockServer()
    def ws_handler(msg): return msg
    server.mockWebSocket('/ws', ws_handler)
    assert '/ws' in server.ws_endpoints
    assert server.ws_endpoints['/ws'] is ws_handler

def test_mock_websocket_invalid():
    server = MockServer()
    with pytest.raises(TypeError):
        server.mockWebSocket(123, lambda x: x)
    with pytest.raises(TypeError):
        server.mockWebSocket('/ws', "not_callable")

def test_hot_reload_handlers():
    server = MockServer()
    def h1(req): pass
    server.registerEndpoint('GET', '/a', h1)
    new = [{'method': 'POST', 'path': '/b', 'handler': h1}]
    server.hotReloadHandlers(new)
    assert server.endpoints == new

def test_hot_reload_handlers_invalid():
    server = MockServer()
    with pytest.raises(TypeError):
        server.hotReloadHandlers("notalist")
    with pytest.raises(TypeError):
        server.hotReloadHandlers([123])
    with pytest.raises(ValueError):
        server.hotReloadHandlers([{'method': 'GET'}])

def test_simulate_rate_limiting():
    server = MockServer()
    server.simulateRateLimiting(10, 5)
    rl = server.rate_limit
    assert rl['quota'] == 10
    assert rl['per_seconds'] == 5
    assert rl['retry_after'] == 5

def test_simulate_rate_limiting_invalid_types():
    server = MockServer()
    with pytest.raises(TypeError):
        server.simulateRateLimiting('10', 5)
    with pytest.raises(TypeError):
        server.simulateRateLimiting(10, '5')

def test_simulate_rate_limiting_invalid_values():
    server = MockServer()
    with pytest.raises(ValueError):
        server.simulateRateLimiting(-1, 5)
    with pytest.raises(ValueError):
        server.simulateRateLimiting(5, 0)

def test_assert_query_param():
    server = MockServer()
    server.assertQueryParam('q', value='test')
    assert len(server.query_param_assertions) == 1
    qp = server.query_param_assertions[0]
    assert qp['name'] == 'q'
    assert qp['value'] == 'test'
    assert qp['pattern'] is None
    assert qp['predicate'] is None

def test_assert_query_param_invalid_name():
    server = MockServer()
    with pytest.raises(TypeError):
        server.assertQueryParam(123)

def test_simulate_chunked_transfer():
    server = MockServer()
    chunks = ['a', 'b', 'c']
    server.simulateChunkedTransfer(chunks, 0.1)
    assert len(server.chunked_transfers) == 1
    ct = server.chunked_transfers[0]
    assert ct['chunks'] == chunks
    assert ct['delay'] == 0.1

def test_simulate_chunked_transfer_invalid():
    server = MockServer()
    with pytest.raises(TypeError):
        server.simulateChunkedTransfer('notalist', 0.1)
    with pytest.raises(TypeError):
        server.simulateChunkedTransfer([], 'notanumber')
