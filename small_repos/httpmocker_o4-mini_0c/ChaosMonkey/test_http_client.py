import chaoslib

def test_default_http_methods():
    # Ensure basic methods work and return default Response
    resp_get = chaoslib.httpClient.get("http://service/xyz")
    resp_post = chaoslib.httpClient.post("http://service/xyz")
    resp_put = chaoslib.httpClient.put("http://service/xyz")
    resp_delete = chaoslib.httpClient.delete("http://service/xyz")
    for resp in [resp_get, resp_post, resp_put, resp_delete]:
        assert isinstance(resp, chaoslib.Response)
        assert resp.status_code == 200
        assert resp.body == "OK"
