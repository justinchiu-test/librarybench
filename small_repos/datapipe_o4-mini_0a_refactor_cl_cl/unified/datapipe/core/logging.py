"""
Logging setup and configuration.
"""
import logging
import sys

def setup_logging(level=logging.DEBUG, name="datapipe"):
    """
    Configure logging for the application.
    
    Args:
        level: The logging level to use
        name: The logger name
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Only add handlers if they don't already exist
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    logger.setLevel(level)
    return logger