import threading
import time

# Exceptions
class HTTPError(Exception):
    def __init__(self, status_code, message="HTTP Error"):
        self.status_code = status_code
        super().__init__(f"{message}: {status_code}")

class WSConnectionError(Exception):
    pass

class WSDisconnectError(Exception):
    pass

# Global state
http_endpoints = {}
http_record = []
http_errors = {'status_code': None, 'times': 0}
cors_config = {'origins': None, 'headers': None}
retry_policy = {'retries': 0, 'backoff': 0}

ws_channels = {}  # channel_name -> list of clients
ws_record = []
ws_errors = {'connect_failures': 0, 'disconnect_after': None}
ws_dynamic_callbacks = {}

# HTTP request object
class HTTPRequest:
    def __init__(self, method, path, headers=None, body=None):
        self.method = method
        self.path = path
        self.headers = headers or {}
        self.body = body

# WebSocket client mock
class MockWebSocketClient:
    def __init__(self, channel, headers=None):
        self.channel = channel
        self.headers = headers or {}
        self.inbox = []
        self.connected = False
        self.send_count = 0
        self._connect()

    def _connect(self):
        # Simulate connect failures
        attempts = 0
        while True:
            if ws_errors.get('connect_failures', 0) > 0:
                ws_errors['connect_failures'] -= 1
                attempts += 1
                if attempts > retry_policy['retries']:
                    raise WSConnectionError("Failed to connect to WebSocket")
                time.sleep(0)  # no real wait
                continue
            break
        # Record handshake
        ws_record.append({'channel': self.channel, 'headers': self.headers})
        # Register client
        ws_channels.setdefault(self.channel, []).append(self)
        self.connected = True

    def send(self, message):
        if not self.connected:
            raise WSDisconnectError("WebSocket is disconnected")
        self.send_count += 1
        # Simulate mid-stream disconnect
        da = ws_errors.get('disconnect_after')
        if da is not None and self.send_count > da:
            self.disconnect()
            raise WSDisconnectError("WebSocket disconnected mid-stream")
        # Broadcast to other clients
        for client in ws_channels.get(self.channel, []):
            if client is not self:
                client.inbox.append({'from': self, 'message': message})
        # Dynamic callbacks
        for cb in ws_dynamic_callbacks.get(self.channel, []):
            response = cb(message)
            if response is not None:
                self.inbox.append({'from': None, 'message': response})

    def receive(self):
        msgs = list(self.inbox)
        self.inbox.clear()
        return msgs

    def ping(self):
        # respond with pong
        return "pong"

    def disconnect(self):
        if self.connected and self in ws_channels.get(self.channel, []):
            ws_channels[self.channel].remove(self)
        self.connected = False

# Public API

def startRequestRecording():
    http_record.clear()
    ws_record.clear()

class HTTPClient:
    def get(self, path, headers=None):
        return self._request('GET', path, headers=headers)

    def post(self, path, headers=None, body=None):
        return self._request('POST', path, headers=headers, body=body)

    def put(self, path, headers=None, body=None):
        return self._request('PUT', path, headers=headers, body=body)

    def delete(self, path, headers=None):
        return self._request('DELETE', path, headers=headers)

    def _request(self, method, path, headers=None, body=None):
        headers = headers or {}
        req = HTTPRequest(method, path, headers, body)
        # Record each request invocation
        http_record.append(req)

        # Determine how many attempts to make:
        # Use at least one attempt; if retry_policy['retries'] > 0, use that number of attempts.
        attempts = retry_policy.get('retries', 0)
        attempts = attempts if attempts > 0 else 1

        last_error = None
        for attempt in range(attempts):
            try:
                # Simulate error
                if http_errors.get('times', 0) > 0:
                    http_errors['times'] -= 1
                    raise HTTPError(http_errors.get('status_code', 500))

                # Endpoint handler
                handler = http_endpoints.get((method.upper(), path))
                if handler:
                    status, res_headers, res_body = handler(req)
                else:
                    status, res_headers, res_body = 404, {}, "Not Found"

                # CORS
                origin = req.headers.get('Origin')
                if cors_config['origins'] and origin in cors_config['origins']:
                    # ensure we're not modifying the handler's dict
                    res_headers = res_headers.copy()
                    res_headers['Access-Control-Allow-Origin'] = origin
                    res_headers['Access-Control-Allow-Headers'] = ','.join(cors_config['headers'] or [])

                if status >= 400:
                    raise HTTPError(status)

                return {'status': status, 'headers': res_headers, 'body': res_body}

            except HTTPError as e:
                last_error = e
                # If this was our last allowed attempt, re-raise
                if attempt == attempts - 1:
                    raise
                # Otherwise, wait backoff and retry
                backoff = retry_policy.get('backoff', 0)
                if backoff:
                    time.sleep(backoff)
                continue

httpClient = HTTPClient()

def simulateError(err_type, config):
    if err_type == 'http':
        http_errors['status_code'] = config.get('status_code', 500)
        http_errors['times'] = config.get('times', 1)
    elif err_type == 'ws':
        # config can have connect_failures or disconnect_after
        if 'connect_failures' in config:
            ws_errors['connect_failures'] = config['connect_failures']
        if 'disconnect_after' in config:
            ws_errors['disconnect_after'] = config['disconnect_after']

def assertHeader(request, header_name, expected_value=None):
    actual = request.headers.get(header_name)
    if actual is None:
        raise AssertionError(f"Header '{header_name}' not found")
    if expected_value is not None and actual != expected_value:
        raise AssertionError(f"Header '{header_name}' value '{actual}' != expected '{expected_value}'")

def registerEndpoint(method, path, handler):
    http_endpoints[(method.upper(), path)] = handler

def configureCORS(origins, headers):
    cors_config['origins'] = origins
    cors_config['headers'] = headers

def mockWebSocket(channel_name, headers=None):
    return MockWebSocketClient(channel_name, headers=headers)

def setRetryPolicy(retries, backoff):
    retry_policy['retries'] = retries
    retry_policy['backoff'] = backoff

def addDynamicCallback(channel_name, callback):
    ws_dynamic_callbacks.setdefault(channel_name, []).append(callback)

def assertRequestBody(request, validator):
    if not validator(request.body):
        raise AssertionError("Request body validation failed")
