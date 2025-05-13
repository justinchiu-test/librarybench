import re
import json
import time

# globals
request_log = []
endpoints = []
errors = []
cors_enabled = False
cors_headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
    'Access-Control-Allow-Headers': '*'
}
retry_policy = {'retries': 0, 'backoff_factor': 0}

class Response:
    def __init__(self, status, headers, body, malformed=False):
        self.status = status
        self.headers = headers or {}
        self._body = body
        self._malformed = malformed
    def text(self):
        return self._body
    def json(self):
        if self._malformed:
            raise ValueError('Malformed JSON')
        return json.loads(self._body)

def reset():
    global request_log, endpoints, errors, cors_enabled, retry_policy
    # clear in-place so imported references stay valid
    request_log.clear()
    endpoints.clear()
    errors.clear()
    cors_enabled = False
    retry_policy = {'retries': 0, 'backoff_factor': 0}

def startRequestRecording():
    # clear in-place so imported references stay valid
    request_log.clear()

def registerEndpoint(pattern, response, status=200, headers=None):
    # pattern can be string or compiled regex
    endpoints.append({
        'pattern': pattern,
        'response': response,
        'status': status,
        'headers': headers or {}
    })

def addDynamicCallback(pattern, callback):
    endpoints.append({'pattern': pattern, 'dynamic': callback})

def simulateError(pattern, errorType):
    errors.append({'pattern': pattern, 'type': errorType})

def configureCORS():
    global cors_enabled
    cors_enabled = True

def setRetryPolicy(retries, backoff_factor):
    retry_policy['retries'] = retries
    retry_policy['backoff_factor'] = backoff_factor

def assertHeader(headers, name, expected):
    if name not in headers:
        raise AssertionError(f'Header {name} not found')
    val = headers[name]
    # if expected is a regex
    if hasattr(expected, 'match'):
        if not expected.match(val):
            raise AssertionError(f'Header {name} value {val} does not match pattern')
    else:
        if val != expected:
            raise AssertionError(f'Header {name} value {val} != expected {expected}')

def assertRequestBody(body, expected):
    if isinstance(body, str):
        try:
            data = json.loads(body)
        except:
            raise AssertionError('Body is not valid JSON')
    else:
        data = body
    if data != expected:
        raise AssertionError(f'Body {data} != expected {expected}')

def _match_pattern(pat, url):
    if isinstance(pat, str):
        # exact path or with query parameters
        return url == pat or url.startswith(pat + '?')
    else:
        return bool(pat.match(url))

class httpClient:
    @staticmethod
    def request(method, url, headers=None, body=None):
        global request_log
        headers = headers or {}
        request_log.append({'method': method, 'url': url, 'headers': headers, 'body': body})
        # CORS preflight
        if cors_enabled and method == 'OPTIONS':
            return Response(204, cors_headers.copy(), '')
        # simulate errors
        for err in errors:
            pat = err['pattern']
            if _match_pattern(pat, url):
                etype = err['type']
                if etype == '5xx':
                    return Response(500, {}, '')
                if etype == 'network':
                    raise ConnectionError('Network reset')
                if etype == 'malformed':
                    return Response(200, {}, '', malformed=True)
        # find endpoints
        for ep in endpoints:
            pat = ep['pattern']
            if _match_pattern(pat, url):
                if 'dynamic' in ep:
                    resp = ep['dynamic']({
                        'method': method,
                        'url': url,
                        'headers': headers,
                        'body': body
                    })
                    status = resp.get('status', 200)
                    rheaders = resp.get('headers', {}).copy()
                    data = resp.get('body', resp.get('response', ''))
                else:
                    status = ep.get('status', 200)
                    rheaders = ep.get('headers', {}).copy()
                    resp_content = ep['response']
                    if isinstance(resp_content, (dict, list)):
                        data = json.dumps(resp_content)
                        rheaders.setdefault('Content-Type', 'application/json')
                    else:
                        data = resp_content
                        rheaders.setdefault('Content-Type', 'text/html')
                if cors_enabled:
                    rheaders.update(cors_headers)
                return Response(status, rheaders, data)
        # no match
        raise ValueError(f'No endpoint registered for URL {url}')

    @staticmethod
    def _withRetry(method, url, headers, body):
        attempts = 0
        retries = retry_policy['retries']
        backoff = retry_policy['backoff_factor']
        while True:
            try:
                return httpClient.request(method, url, headers, body)
            except Exception as e:
                if attempts < retries and isinstance(e, ConnectionError):
                    attempts += 1
                    time.sleep(backoff * attempts)
                    continue
                raise

    @staticmethod
    def get(url, headers=None):
        return httpClient._withRetry('GET', url, headers, None)

    @staticmethod
    def post(url, headers=None, body=None):
        return httpClient._withRetry('POST', url, headers, body)

    @staticmethod
    def put(url, headers=None, body=None):
        return httpClient._withRetry('PUT', url, headers, body)

    @staticmethod
    def delete(url, headers=None):
        return httpClient._withRetry('DELETE', url, headers, None)

class MockWebSocket:
    def __init__(self, url):
        self.url = url
        self.messages_sent = []
        self.handlers = []
    def send(self, message):
        self.messages_sent.append(message)
    def on_message(self, handler):
        self.handlers.append(handler)
    def emit(self, message):
        for h in self.handlers:
            h(message)
    def close(self):
        self.handlers = []
        self.messages_sent = []

def mockWebSocket(url):
    return MockWebSocket(url)
