import logging

def setup_logging():
    """
    Configure and return a logger for the scheduler system.
    Logs include timestamp, level, and message.
    """
    logger = logging.getLogger("scheduler")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger
