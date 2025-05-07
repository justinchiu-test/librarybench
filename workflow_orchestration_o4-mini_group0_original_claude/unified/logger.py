"""
Logging utilities for the unified workflow orchestration system.
"""
import logging
import os
import sys
from typing import Optional


def configure_logger(
    name: str = "workflow_orchestration",
    log_level: int = logging.INFO,
    log_file: Optional[str] = None,
    console_output: bool = True,
    format_string: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
) -> logging.Logger:
    """
    Configure and return a logger instance.

    :param name: Logger name
    :param log_level: Logging level (default: INFO)
    :param log_file: Optional file path to write logs to
    :param console_output: Whether to output logs to console
    :param format_string: Format string for log messages
    :return: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Clear existing handlers if any
    if logger.handlers:
        logger.handlers.clear()
    
    formatter = logging.Formatter(format_string)
    
    # Add file handler if log_file is specified
    if log_file:
        # Create directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Add console handler if console_output is True
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


def get_default_logger() -> logging.Logger:
    """
    Get a default logger instance.

    :return: Default logger instance
    """
    return configure_logger()


# Create a default logger for use throughout the module
default_logger = get_default_logger()