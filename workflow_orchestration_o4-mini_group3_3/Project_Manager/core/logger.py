import logging
import sys
from utils import create_handler

LOG_FILE = "task_system.log"
FMT = "%(asctime)s %(levelname)s %(name)s: %(message)s"

def setup_logger():
    logger = logging.getLogger("task_system")
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        fh = create_handler(logging.FileHandler, LOG_FILE,
                            level=logging.DEBUG, fmt_str=FMT)
        ch = create_handler(logging.StreamHandler, sys.stdout,
                            level=logging.INFO, fmt_str=FMT)
        logger.addHandler(fh)
        logger.addHandler(ch)
    return logger

logger = setup_logger()
