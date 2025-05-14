import re

Pattern = getattr(re, 'Pattern', type(re.compile('')))

class MockServer:
    def __init__(self):
        self.endpoints = []
        self.header_assertions = []
        self.body_assertions = []
        self.cors_config = {}
        self.auth_simulations = []
        self.ws_endpoints = {}
        self.rate_limit = {}
        self.query_param_assertions = []
        self.chunked_transfers = []

    def registerEndpoint(self, method, path, handler):
        if not isinstance(method, str):
            raise TypeError("Method must be a string")
        if not (isinstance(path, str) or isinstance(path, Pattern)):
            raise TypeError("Path must be a string or regex pattern")
        if not callable(handler):
            raise TypeError("Handler must be callable")
        self.endpoints.append({
            'method': method,
            'path': path,
            'handler': handler
        })

    def assertHeader(self, name, value=None, pattern=None, predicate=None):
        if not isinstance(name, str):
            raise TypeError("Header name must be a string")
        self.header_assertions.append({
            'name': name,
            'value': value,
            'pattern': pattern,
            'predicate': predicate
        })

    def assertBody(self, schema=None, predicate=None):
        self.body_assertions.append({
            'schema': schema,
            'predicate': predicate
        })

    def configureCORS(self, allow_origins=None, allow_methods=None, allow_headers=None, allow_credentials=False):
        if allow_origins is not None and not isinstance(allow_origins, (list, tuple)):
            raise TypeError("allow_origins must be a list or tuple")
        if allow_methods is not None and not isinstance(allow_methods, (list, tuple)):
            raise TypeError("allow_methods must be a list or tuple")
        if allow_headers is not None and not isinstance(allow_headers, (list, tuple)):
            raise TypeError("allow_headers must be a list or tuple")
        if not isinstance(allow_credentials, bool):
            raise TypeError("allow_credentials must be a boolean")
        self.cors_config = {
            'allow_origins': allow_origins or [],
            'allow_methods': allow_methods or [],
            'allow_headers': allow_headers or [],
            'allow_credentials': allow_credentials
        }

    def simulateAuth(self, auth_type, credentials=None):
        if auth_type not in ('Basic', 'Digest', 'Bearer'):
            raise ValueError("Unsupported auth type")
        self.auth_simulations.append({
            'type': auth_type,
            'credentials': credentials
        })

    def mockWebSocket(self, path, handler):
        if not isinstance(path, str):
            raise TypeError("WebSocket path must be a string")
        if not callable(handler):
            raise TypeError("WebSocket handler must be callable")
        self.ws_endpoints[path] = handler

    def hotReloadHandlers(self, new_handlers):
        if not isinstance(new_handlers, list):
            raise TypeError("new_handlers must be a list")
        for nh in new_handlers:
            if not isinstance(nh, dict):
                raise TypeError("Each handler definition must be a dict")
            if 'method' not in nh or 'path' not in nh or 'handler' not in nh:
                raise ValueError("Each handler must have 'method', 'path', and 'handler'")
        self.endpoints = new_handlers.copy()

    def simulateRateLimiting(self, quota, per_seconds):
        if not isinstance(quota, int) or not isinstance(per_seconds, (int, float)):
            raise TypeError("Invalid types for quota or per_seconds")
        if quota < 0 or per_seconds <= 0:
            raise ValueError("Quota must be >=0 and per_seconds >0")
        self.rate_limit = {
            'quota': quota,
            'per_seconds': per_seconds,
            'retry_after': int(per_seconds)
        }

    def assertQueryParam(self, name, value=None, pattern=None, predicate=None):
        if not isinstance(name, str):
            raise TypeError("Query parameter name must be a string")
        self.query_param_assertions.append({
            'name': name,
            'value': value,
            'pattern': pattern,
            'predicate': predicate
        })

    def simulateChunkedTransfer(self, chunks, delay):
        if not isinstance(chunks, list):
            raise TypeError("Chunks must be a list")
        if not isinstance(delay, (int, float)):
            raise TypeError("Delay must be a number")
        self.chunked_transfers.append({
            'chunks': chunks,
            'delay': delay
        })
