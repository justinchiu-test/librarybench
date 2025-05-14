import urllib.request
import urllib.error
import time

class HTTPAdapter:
    def __init__(self, headers=None, timeout=5, retries=3, retry_delay=1):
        self.headers = headers or {}
        self.timeout = timeout
        self.retries = retries
        self.retry_delay = retry_delay

    def get(self, url):
        # Allow URLs without scheme by defaulting to http://
        full_url = url if "://" in url else f"http://{url}"
        req = urllib.request.Request(full_url, headers=self.headers, method='GET')
        for attempt in range(self.retries):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    return resp.read()
            except (urllib.error.URLError, urllib.error.HTTPError):
                if attempt < self.retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise

    def post(self, url, data):
        # Allow URLs without scheme by defaulting to http://
        full_url = url if "://" in url else f"http://{url}"
        data_bytes = data.encode('utf-8') if isinstance(data, str) else data
        req = urllib.request.Request(full_url, data=data_bytes, headers=self.headers, method='POST')
        for attempt in range(self.retries):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    return resp.read()
            except (urllib.error.URLError, urllib.error.HTTPError):
                if attempt < self.retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise
