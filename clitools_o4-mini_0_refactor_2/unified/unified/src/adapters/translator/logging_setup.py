"""
Logging setup for Translator CLI adapter.
"""
import logging

def setup_logging(json_format=False, level=logging.INFO):
    logger = logging.getLogger()
    logger.setLevel(level)
    # Remove existing handlers
    for h in logger.handlers[:]:
        logger.removeHandler(h)
    import sys
    ch = logging.StreamHandler(sys.stdout)
    if json_format:
        import json
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                return json.dumps({"level": record.levelname, "message": record.getMessage()})
        ch.setFormatter(JsonFormatter())
    else:
        fmt = logging.Formatter("%(levelname)s:%(message)s")
        ch.setFormatter(fmt)
    logger.addHandler(ch)
    return logger