import re

class Response:
    def __init__(self, status_code=200, headers=None, body=None):
        self.status_code = status_code
        self.headers = headers or {}
        self.body = body

class MockServer:
    def __init__(self):
        self.recording = False
        self.recorded_requests = []
        self.endpoints = []  # list of dicts with keys: method, pattern, response
        self.error_simulations = {}  # key: (method, pattern) -> status_code
        self.required_headers = {}  # key: (method, pattern) -> dict of headers
        self.body_validators = {}  # key: (method, pattern) -> callable
        self.dynamic_callbacks = {}  # key: (method, pattern) -> callable
        self.cors_options = {}
        self.ws_handlers = {}  # pattern -> handler
        self.retry_policy = None

    def startRequestRecording(self):
        self.recording = True
        self.recorded_requests = []

    def registerEndpoint(self, method, path_pattern, response):
        # response: tuple(status_code, headers, body)
        self.endpoints.append({
            'method': method.upper(),
            'pattern': path_pattern,
            'response': response
        })

    def simulateError(self, method, path_pattern, status_code):
        self.error_simulations[(method.upper(), path_pattern)] = status_code

    def assertHeader(self, method, path_pattern, headers):
        # headers: dict of required header names to expected values or None
        self.required_headers[(method.upper(), path_pattern)] = headers

    def assertRequestBody(self, method, path_pattern, validator):
        self.body_validators[(method.upper(), path_pattern)] = validator

    def addDynamicCallback(self, method, path_pattern, callback):
        self.dynamic_callbacks[(method.upper(), path_pattern)] = callback

    def configureCORS(self, **options):
        self.cors_options = options

    def mockWebSocket(self, path_pattern, handler):
        self.ws_handlers[path_pattern] = handler

    def setRetryPolicy(self, policy):
        self.retry_policy = policy

    def _match_endpoint(self, method, path):
        for ep in self.endpoints:
            if ep['method'] != method:
                continue
            pat = ep['pattern']
            if pat == path or (hasattr(pat, 'fullmatch') and pat.fullmatch(path)):
                return ep
        return None

    def handle_request(self, method, path, headers=None, body=None):
        headers = headers or {}
        if self.recording:
            self.recorded_requests.append({
                'method': method,
                'path': path,
                'headers': headers,
                'body': body
            })
        # Check error simulation
        for (m, pat), code in self.error_simulations.items():
            if m == method and (pat == path or (hasattr(pat, 'fullmatch') and pat.fullmatch(path))):
                return Response(status_code=code, headers={}, body=f"Error {code}")
        # Check header requirements
        for (m, pat), req in self.required_headers.items():
            if m == method and (pat == path or (hasattr(pat, 'fullmatch') and pat.fullmatch(path))):
                for h, val in req.items():
                    if h not in headers or (val is not None and headers.get(h) != val):
                        return Response(status_code=400, headers={}, body=f"Missing or invalid header {h}")
        # Check body validator
        for (m, pat), validator in self.body_validators.items():
            if m == method and (pat == path or (hasattr(pat, 'fullmatch') and pat.fullmatch(path))):
                try:
                    if not validator(body):
                        return Response(status_code=400, headers={}, body="Invalid request body")
                except Exception:
                    return Response(status_code=400, headers={}, body="Invalid request body")
        # Check dynamic callback
        for (m, pat), cb in self.dynamic_callbacks.items():
            if m == method and (pat == path or (hasattr(pat, 'fullmatch') and pat.fullmatch(path))):
                try:
                    result = cb({
                        'method': method,
                        'path': path,
                        'headers': headers,
                        'body': body
                    })
                    if isinstance(result, Response):
                        return result
                    elif isinstance(result, tuple) and len(result) == 3:
                        return Response(status_code=result[0], headers=result[1], body=result[2])
                    else:
                        return Response(body=result)
                except Exception as e:
                    return Response(status_code=500, headers={}, body=str(e))
        # Static endpoint
        ep = self._match_endpoint(method, path)
        if ep:
            status, hdrs, bd = ep['response']
            return Response(status_code=status, headers=hdrs, body=bd)
        # No endpoint
        return Response(status_code=404, headers={}, body="Not Found")

class HttpClient:
    def __init__(self, server):
        self.server = server

    def get(self, path, headers=None):
        return self.server.handle_request('GET', path, headers=headers, body=None)

    def post(self, path, headers=None, body=None):
        return self.server.handle_request('POST', path, headers=headers, body=body)

    def put(self, path, headers=None, body=None):
        return self.server.handle_request('PUT', path, headers=headers, body=body)

    def delete(self, path, headers=None):
        return self.server.handle_request('DELETE', path, headers=headers, body=None)
