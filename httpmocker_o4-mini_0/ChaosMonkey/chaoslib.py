import random
import time
import re
import json
from urllib.parse import urlparse

# Global state
request_recording = []
_recording_enabled = False

simulate_config = {'rules': []}
endpoint_registry = []
cors_config = None
dynamic_callbacks = []
retry_policy = {'retries': 0, 'backoff': lambda attempt: 0.0}


# Exceptions
class ChaosError(Exception):
    pass

class HTTP5xxError(ChaosError):
    pass

class TimeoutError(ChaosError):
    pass

class ConnectionResetError(ChaosError):
    pass

class BrokenPayloadError(ChaosError):
    pass


# Response object
class Response:
    def __init__(self, status_code=200, body="OK", headers=None):
        self.status_code = status_code
        self.body = body
        self.headers = headers or {}


def startRequestRecording():
    """
    Begin a fresh recording session; also reset simulation, CORS, retry policy, and dynamic callbacks.
    """
    global request_recording, _recording_enabled, simulate_config, cors_config, dynamic_callbacks, retry_policy
    # clear existing recorded requests
    request_recording.clear()
    _recording_enabled = True

    # reset simulate error rules
    simulate_config['rules'].clear()

    # reset CORS
    cors_config = None

    # reset dynamic callbacks
    dynamic_callbacks.clear()

    # reset retry policy to defaults
    retry_policy['retries'] = 0
    retry_policy['backoff'] = lambda attempt: 0.0


def simulateError(error_type, probability=1.0, times=None):
    """
    Register an error simulation rule.
    error_type: '5xx', 'timeout', 'connection', 'broken_payload'
    probability: float between 0 and 1
    times: int or None for infinite
    """
    simulate_config['rules'].append({
        'error_type': error_type,
        'probability': probability,
        'times': times
    })


def assertHeader(name, request):
    headers = request.get('headers', {})
    if name not in headers:
        raise AssertionError(f"Missing header: {name}")


def assertRequestBody(validator, request):
    body = request.get('body', None)
    if not validator(body):
        raise AssertionError("Request body validation failed")


def registerEndpoint(pattern, handler):
    """
    pattern: exact path or wildcard ending with '*'
    handler: function(method, path, headers, body) -> Response
    """
    endpoint_registry.append((pattern, handler))


def configureCORS(allow_origins, allow_methods, allow_headers):
    global cors_config
    cors_config = {
        'allow_origins': allow_origins,
        'allow_methods': allow_methods,
        'allow_headers': allow_headers
    }


def setRetryPolicy(retries, backoff):
    retry_policy['retries'] = retries
    retry_policy['backoff'] = backoff


def addDynamicCallback(callback):
    dynamic_callbacks.append(callback)


def _apply_simulate_rules(method, url, headers, body):
    for rule in simulate_config['rules']:
        if rule['times'] is not None and rule['times'] <= 0:
            continue
        if random.random() < rule['probability']:
            # decrement counter if applicable
            if rule['times'] is not None:
                rule['times'] -= 1
            et = rule['error_type']
            if et == '5xx':
                raise HTTP5xxError("Simulated 5xx error")
            if et == 'timeout':
                raise TimeoutError("Simulated timeout")
            if et == 'connection':
                raise ConnectionResetError("Simulated connection reset")
            if et == 'broken_payload':
                raise BrokenPayloadError("Simulated broken payload")
    return


def _match_endpoint(path):
    for pattern, handler in endpoint_registry:
        if pattern.endswith('*'):
            prefix = pattern[:-1]
            if path.startswith(prefix):
                return handler
        else:
            if path == pattern:
                return handler
    return None


class httpClient:
    @classmethod
    def get(cls, url, headers=None, body=None):
        return cls.request('GET', url, headers=headers, body=body)

    @classmethod
    def post(cls, url, headers=None, body=None):
        return cls.request('POST', url, headers=headers, body=body)

    @classmethod
    def put(cls, url, headers=None, body=None):
        return cls.request('PUT', url, headers=headers, body=body)

    @classmethod
    def delete(cls, url, headers=None, body=None):
        return cls.request('DELETE', url, headers=headers, body=body)

    @classmethod
    def request(cls, method, url, headers=None, body=None):
        headers = headers.copy() if headers else {}
        attempt = 0
        last_exc = None

        # Handle CORS preflight
        if method.upper() == 'OPTIONS' and cors_config:
            origin = headers.get('Origin')
            if origin not in cors_config['allow_origins'] and '*' not in cors_config['allow_origins']:
                return Response(status_code=403, body="CORS Denied", headers={})
            # Build CORS headers
            return Response(
                status_code=200,
                body="",
                headers={
                    'Access-Control-Allow-Origin': origin,
                    'Access-Control-Allow-Methods': ','.join(cors_config['allow_methods']),
                    'Access-Control-Allow-Headers': ','.join(cors_config['allow_headers'])
                }
            )

        while attempt <= retry_policy['retries']:
            try:
                # Simulate errors
                _apply_simulate_rules(method, url, headers, body)

                # Parse path
                path = urlparse(url).path

                # Custom endpoint handling
                handler = _match_endpoint(path)
                if handler:
                    resp = handler(method, path, headers, body)
                else:
                    resp = Response()

                # Record request
                if _recording_enabled:
                    request_recording.append({
                        'method': method.upper(),
                        'url': url,
                        'headers': headers.copy(),
                        'body': body
                    })

                # Apply dynamic callbacks only when recording is enabled
                if _recording_enabled:
                    for cb in dynamic_callbacks:
                        cb({
                            'method': method.upper(),
                            'url': url,
                            'headers': headers,
                            'body': body
                        }, resp)

                return resp

            except BrokenPayloadError:
                # Treated as fatal
                raise
            except HTTP5xxError:
                # Do not retry 5xx errors
                raise
            except (TimeoutError, ConnectionResetError) as e:
                last_exc = e
                if attempt < retry_policy['retries']:
                    backoff_time = retry_policy['backoff'](attempt)
                    time.sleep(backoff_time)
                    attempt += 1
                    continue
                raise

        # Should not reach here
        if last_exc:
            raise last_exc
        return Response()


# Mock WebSocket
class MockWebSocketConnection:
    def __init__(self, drop_rate, malformed_rate):
        self.drop_rate = drop_rate
        self.malformed_rate = malformed_rate

    def send(self, message):
        pass

    def receive(self):
        # Simulate drop
        if random.random() < self.drop_rate:
            return None
        # Simulate malformed
        if random.random() < self.malformed_rate:
            return "MALFORMED_PAYLOAD"
        # Otherwise return valid JSON
        msg = {'message': 'hello'}
        return json.dumps(msg)


class MockWebSocketServer:
    def __init__(self, drop_rate=0.0, malformed_rate=0.0):
        self.drop_rate = drop_rate
        self.malformed_rate = malformed_rate

    def connect(self):
        return MockWebSocketConnection(self.drop_rate, self.malformed_rate)


def mockWebSocket(drop_rate=0.0, malformed_rate=0.0):
    return MockWebSocketServer(drop_rate, malformed_rate)
