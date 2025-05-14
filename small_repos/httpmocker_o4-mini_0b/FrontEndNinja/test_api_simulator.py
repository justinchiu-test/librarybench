import re
import pytest
import json
import urllib.parse
from api_simulator import (
    reset, startRequestRecording, httpClient, request_log, registerEndpoint,
    simulateError, assertHeader, assertRequestBody, configureCORS,
    setRetryPolicy, mockWebSocket, addDynamicCallback
)

def setup_function():
    reset()

def test_request_recording():
    registerEndpoint('/test', {'foo':'bar'})
    startRequestRecording()
    res = httpClient.get('/test')
    assert len(request_log) == 1
    entry = request_log[0]
    assert entry['method'] == 'GET'
    assert entry['url'] == '/test'

def test_get_json_response():
    registerEndpoint('/user', {'id':1,'name':'Alice'})
    res = httpClient.get('/user')
    assert res.status == 200
    assert res.json() == {'id':1,'name':'Alice'}

def test_post_html_response():
    html = '<h1>Hello</h1>'
    registerEndpoint('/page', html)
    res = httpClient.post('/page')
    assert res.status == 200
    assert res.text() == html
    assert res.headers['Content-Type'] == 'text/html'

def test_assert_header_success():
    headers = {'Authorization':'Bearer token123'}
    assertHeader(headers, 'Authorization', 'Bearer token123')
    pattern = re.compile(r'Bearer\s+\w+')
    assertHeader(headers, 'Authorization', pattern)

def test_assert_header_failure():
    headers = {'X-Test':'123'}
    with pytest.raises(AssertionError):
        assertHeader(headers, 'Missing', 'value')
    with pytest.raises(AssertionError):
        assertHeader(headers, 'X-Test', 'wrong')

def test_assert_request_body():
    body = '{"a":1,"b":"two"}'
    assertRequestBody(body, {'a':1,'b':'two'})
    with pytest.raises(AssertionError):
        assertRequestBody('notjson', {})
    with pytest.raises(AssertionError):
        assertRequestBody('{"a":2}', {'a':1})

def test_simulate_error_5xx():
    registerEndpoint('/err', {'ok':True})
    simulateError('/err', '5xx')
    res = httpClient.get('/err')
    assert res.status == 500

def test_simulate_error_network():
    simulateError('/net', 'network')
    with pytest.raises(ConnectionError):
        httpClient.get('/net')

def test_simulate_error_malformed():
    simulateError('/bad', 'malformed')
    registerEndpoint('/bad', {'ok':True})
    res = httpClient.get('/bad')
    assert res.status == 200
    with pytest.raises(ValueError):
        res.json()

def test_cors_headers_and_preflight():
    configureCORS()
    registerEndpoint('/cors', {'ok':True})
    res = httpClient.get('/cors')
    assert res.headers['Access-Control-Allow-Origin'] == '*'
    res2 = httpClient.request('OPTIONS', '/any')
    assert res2.status == 204
    assert 'Access-Control-Allow-Methods' in res2.headers

def test_retry_policy():
    count = {'cnt':0}
    def cb(req):
        if count['cnt'] == 0:
            count['cnt'] = 1
            raise ConnectionError('fail')
        return {'body': json.dumps({'ok':True}), 'status':200, 'headers':{'Content-Type':'application/json'}}
    addDynamicCallback('/retry', cb)
    setRetryPolicy(1, 0)
    res = httpClient.get('/retry')
    assert res.status == 200
    assert res.json() == {'ok':True}
    assert len(request_log) == 2

def test_dynamic_callback_random_id():
    import random
    def gen(req):
        return {'body': json.dumps({'id': random.randint(1,1000)}), 'status':200, 'headers':{'Content-Type':'application/json'}}
    addDynamicCallback('/id', gen)
    res1 = httpClient.get('/id')
    res2 = httpClient.get('/id')
    assert res1.json()['id'] != res2.json()['id']

def test_dynamic_pagination():
    def pager(req):
        url = req['url']
        q = urllib.parse.urlparse(url).query
        params = urllib.parse.parse_qs(q)
        page = int(params.get('page',['1'])[0])
        items = list(range((page-1)*5+1, page*5+1))
        return {'body': json.dumps({'items':items}), 'status':200, 'headers':{'Content-Type':'application/json'}}
    addDynamicCallback('/items', pager)
    res1 = httpClient.get('/items?page=1')
    res2 = httpClient.get('/items?page=2')
    assert res1.json()['items'] == [1,2,3,4,5]
    assert res2.json()['items'] == [6,7,8,9,10]

def test_mock_websocket():
    ws = mockWebSocket('ws://example')
    received = []
    ws.on_message(lambda m: received.append(m))
    ws.emit('hello')
    assert received == ['hello']
    ws.send('out')
    assert ws.messages_sent == ['out']
