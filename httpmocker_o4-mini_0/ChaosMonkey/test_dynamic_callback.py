import chaoslib

def add_custom_header(request, response):
    response.headers['X-Custom'] = 'Injected'

def test_dynamic_callback_adds_header():
    chaoslib.startRequestRecording()
    chaoslib.addDynamicCallback(add_custom_header)
    resp = chaoslib.httpClient.get("http://service/dyncb")
    assert resp.headers.get('X-Custom') == 'Injected'
