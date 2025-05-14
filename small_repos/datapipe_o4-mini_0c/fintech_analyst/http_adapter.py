import requests
import time

class HTTPAdapter:
    def __init__(self, retries=3, backoff=0.1):
        self.retries = retries
        self.backoff = backoff

    def fetch(self, url):
        last_exc = None
        for attempt in range(self.retries):
            try:
                r = requests.get(url)
                if r.status_code == 200:
                    return r.json()
                last_exc = RuntimeError(f"Status {r.status_code}")
            except Exception as e:
                last_exc = e
            time.sleep(self.backoff * (2 ** attempt))
        raise last_exc

    def submit(self, url, data):
        last_exc = None
        for attempt in range(self.retries):
            try:
                r = requests.post(url, json=data)
                if r.status_code == 200:
                    return r.json()
                last_exc = RuntimeError(f"Status {r.status_code}")
            except Exception as e:
                last_exc = e
            time.sleep(self.backoff * (2 ** attempt))
        raise last_exc
