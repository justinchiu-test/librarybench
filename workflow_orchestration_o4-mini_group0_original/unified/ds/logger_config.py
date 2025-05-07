import logging

def configure_logger(log_file='task_manager.log'):
    """
    Configure a logger for the task management system.
    Logs DEBUG+ to file and INFO+ to console.
    """
    logger = logging.getLogger('task_manager')
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        # File handler for detailed debug logs
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.DEBUG)
        # Console handler for higher-level info
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(fmt)
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)
    return logger