import re
import time
import pytest
from mockserver import MockServer, Response

def test_register_and_handle():
    srv = MockServer()
    def handler(req):
        return Response(body=b"ok", headers={"Content-Type": "text/plain"})
    srv.registerEndpoint('GET', '/test', handler)
    resp = srv.handle_request('GET', '/test')
    assert resp.status_code == 200
    assert resp.body == b"ok"
    assert resp.headers["Content-Type"] == "text/plain"

def test_regex_path():
    srv = MockServer()
    def handler(req):
        return Response(body=b"num")
    srv.registerEndpoint('GET', re.compile(r"^/items/\d+$"), handler)
    resp = srv.handle_request('GET', '/items/123')
    assert resp.status_code == 200
    assert resp.body == b"num"
    resp2 = srv.handle_request('GET', '/items/abc')
    assert resp2.status_code == 404

def test_assert_header_and_query():
    srv = MockServer()
    def handler(req):
        MockServer.assertHeader(req.headers, 'X-Test', 'value')
        MockServer.assertQueryParam(req.query, 'q', re.compile(r'\d+'))
        return Response()
    srv.registerEndpoint('POST', '/h', handler)
    headers = {'X-Test': 'value'}
    resp = srv.handle_request('POST', '/h?q=123', headers=headers)
    assert resp.status_code == 200
    with pytest.raises(AssertionError):
        srv.handle_request('POST', '/h?q=abc', headers=headers)
    with pytest.raises(AssertionError):
        srv.handle_request('POST', '/h?q=123')

def test_assert_body():
    srv = MockServer()
    def handler(req):
        MockServer.assertBody(req.body, lambda b: isinstance(b, dict) and b.get('x')==1)
        return Response()
    srv.registerEndpoint('PUT', '/b', handler)
    resp = srv.handle_request('PUT', '/b', body={'x':1})
    assert resp.status_code == 200
    with pytest.raises(AssertionError):
        srv.handle_request('PUT', '/b', body={'x':2})

def test_cors_and_options():
    srv = MockServer()
    srv.configureCORS(origin='http://a', methods=['GET','POST'], headers=['X'], max_age=10)
    def h(req): return Response(body=b'd')
    srv.registerEndpoint('GET', '/c', h)
    opt = srv.handle_request('OPTIONS', '/c')
    assert opt.status_code == 200
    assert opt.headers['Access-Control-Allow-Origin']=='http://a'
    get = srv.handle_request('GET', '/c')
    assert get.headers['Access-Control-Allow-Methods']=='GET,POST'
    assert get.body == b'd'

def test_basic_auth():
    srv = MockServer()
    def valid(tok):
        return tok=='user:pass'
    srv.simulateAuth('basic', valid)
    def h(req): return Response(body=b'ok')
    srv.registerEndpoint('GET', '/a', h)
    r1 = srv.handle_request('GET', '/a', headers={'Authorization':'Basic user:pass'})
    assert r1.status_code==200
    r2 = srv.handle_request('GET', '/a', headers={'Authorization':'Basic wrong'})
    assert r2.status_code==403
    r3 = srv.handle_request('GET', '/a', headers={})
    assert r3.status_code==401

def test_rate_limiting():
    srv = MockServer()
    def h(req): return Response(body=b'1')
    srv.registerEndpoint('GET', '/r', h)
    srv.simulateRateLimiting('GET', '/r', limit=2, window=1)
    assert srv.handle_request('GET','/r').status_code==200
    assert srv.handle_request('GET','/r').status_code==200
    r = srv.handle_request('GET','/r')
    assert r.status_code==429
    assert 'Retry-After' in r.headers
    time.sleep(1)
    assert srv.handle_request('GET','/r').status_code==200

def test_hot_reload():
    srv = MockServer()
    def h1(req): return Response(body=b'1')
    def h2(req): return Response(body=b'2')
    srv.registerEndpoint('GET','/h',h1)
    assert srv.handle_request('GET','/h').body==b'1'
    srv.hotReloadHandlers([('GET','/h',h2)])
    assert srv.handle_request('GET','/h').body==b'2'

def test_chunked_transfer():
    srv = MockServer()
    def h(req):
        return Response(chunks=[b'a',b'b',b'c'])
    srv.registerEndpoint('GET','/ch',h)
    r = srv.handle_request('GET','/ch')
    data = b''.join(r.iter_chunks())
    assert data==b'abc'
