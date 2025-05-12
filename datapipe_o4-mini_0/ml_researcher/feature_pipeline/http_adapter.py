import requests
import time

class HTTPAdapter:
    def __init__(self, base_url, retries=3, backoff=0.1):
        self.base_url = base_url
        self.retries = retries
        self.backoff = backoff

    def get(self, path):
        url = self.base_url.rstrip("/") + "/" + path.lstrip("/")
        last_exc = None
        for attempt in range(1, self.retries + 1):
            try:
                response = requests.get(url)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                last_exc = e
                time.sleep(self.backoff * attempt)
        raise last_exc
