import requests
import time

class HTTPAdapter:
    def __init__(self, retries=3, backoff=1, headers=None):
        self.retries = retries
        self.backoff = backoff
        self.headers = headers or {}

    def get(self, url):
        return self._request('get', url)

    def post(self, url, data):
        return self._request('post', url, data)

    def _request(self, method, url, data=None):
        for attempt in range(self.retries):
            try:
                resp = getattr(requests, method)(url, json=data, headers=self.headers)
                resp.raise_for_status()
                return resp
            except Exception:
                if attempt < self.retries - 1:
                    time.sleep(self.backoff * (2 ** attempt))
                else:
                    raise
