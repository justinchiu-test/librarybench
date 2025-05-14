"""Adapter for translator.logging_setup."""

import logging
from typing import Optional
from ...utils.logging import setup_logging

def configure_logging(log_file: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    """Configure logging with specified settings.
    
    Args:
        log_file (str, optional): File to log to
        level (int): Logging level
    
    Returns:
        logging.Logger: Configured logger
    """
    return setup_logging(level=level, log_file=log_file)
