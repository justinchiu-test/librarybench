import time

class HTTPAdapter:
    def __init__(self, session, retries=3, backoff=0.1):
        self.session = session
        self.retries = retries
        self.backoff = backoff

    def get(self, url):
        attempt = 0
        while True:
            try:
                resp = self.session.get(url)
                if getattr(resp, 'status_code', None) == 200:
                    return resp
                raise Exception(f"Status {resp.status_code}")
            except Exception:
                attempt += 1
                if attempt >= self.retries:
                    raise
                time.sleep(self.backoff)

    def post(self, url, data):
        attempt = 0
        while True:
            try:
                resp = self.session.post(url, data=data)
                if getattr(resp, 'status_code', None) in (200, 201):
                    return resp
                raise Exception(f"Status {resp.status_code}")
            except Exception:
                attempt += 1
                if attempt >= self.retries:
                    raise
                time.sleep(self.backoff)
