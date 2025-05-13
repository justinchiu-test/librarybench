import logging
import requests
import threading
import sys

class HTTPLogHandler(logging.Handler):
    def __init__(self, url, timeout=5):
        super().__init__()
        self.url = url
        self.timeout = timeout

    def emit(self, record):
        try:
            msg = self.format(record)
            # Use the handler's formatter (or a default one) to format time
            formatter = self.formatter or logging.Formatter()
            time_str = formatter.formatTime(record)
            payload = {
                'name': record.name,
                'level': record.levelname,
                'message': msg,
                'time': time_str
            }
            thread = threading.Thread(target=self._post, args=(payload,), daemon=True)
            thread.start()
        except Exception:
            self.handleError(record)

    def _post(self, payload):
        try:
            requests.post(self.url, json=payload, timeout=self.timeout)
        except Exception:
            pass

def setup_logging(name='config_watcher', level=logging.INFO, log_file=None, remote_url=None):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
    # Send console logs to stdout so capsys captures them in out
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(level)
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    if log_file:
        fh = logging.FileHandler(log_file)
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    if remote_url:
        hh = HTTPLogHandler(remote_url)
        hh.setLevel(level)
        hh.setFormatter(formatter)
        logger.addHandler(hh)
    return logger
