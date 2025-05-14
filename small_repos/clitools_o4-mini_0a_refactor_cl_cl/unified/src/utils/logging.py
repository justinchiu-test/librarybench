"""
Logging utilities for CLI applications.

This module provides enhanced logging functionality with configurable output formats.
"""

import os
import sys
import logging
import json
from typing import Dict, Any, Optional, Union, List


class LogFormatter(logging.Formatter):
    """
    Custom formatter with color support and optional JSON formatting.
    """
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[94m',      # Blue
        'INFO': '\033[92m',       # Green
        'WARNING': '\033[93m',    # Yellow
        'ERROR': '\033[91m',      # Red
        'CRITICAL': '\033[95m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def __init__(self, fmt: Optional[str] = None, 
                color_enabled: bool = True,
                json_enabled: bool = False):
        """
        Initialize the formatter.
        
        Args:
            fmt (str, optional): Format string.
            color_enabled (bool): Whether to enable color output.
            json_enabled (bool): Whether to enable JSON output.
        """
        self.color_enabled = color_enabled
        self.json_enabled = json_enabled
        
        if fmt is None:
            if json_enabled:
                # No format needed for JSON
                fmt = ""
            else:
                fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        
        super().__init__(fmt)
    
    def format(self, record):
        """
        Format a log record.
        
        Args:
            record: Log record to format.
            
        Returns:
            str: Formatted log message.
        """
        if self.json_enabled:
            # Format as JSON
            log_data = {
                'timestamp': self.formatTime(record),
                'level': record.levelname,
                'name': record.name,
                'message': record.getMessage()
            }
            
            # Add exception info if available
            if record.exc_info:
                log_data['exception'] = self.formatException(record.exc_info)
            
            return json.dumps(log_data)
        
        # Standard formatting
        result = super().format(record)
        
        # Apply colors if enabled
        if self.color_enabled and record.levelname in self.COLORS:
            color_code = self.COLORS[record.levelname]
            reset_code = self.COLORS['RESET']
            
            # Wrap the levelname in color codes
            result = result.replace(
                f"[{record.levelname}]",
                f"[{color_code}{record.levelname}{reset_code}]"
            )
        
        return result


def setup_logging(level: int = logging.INFO, 
                 log_file: Optional[str] = None,
                 json_format: bool = False,
                 color_enabled: bool = True,
                 logger_name: Optional[str] = None) -> logging.Logger:
    """
    Set up logging with customizable configuration.
    
    Args:
        level (int): Logging level.
        log_file (str, optional): File to write logs to.
        json_format (bool): Whether to use JSON format.
        color_enabled (bool): Whether to enable colored output.
        logger_name (str, optional): Name for the logger.
        
    Returns:
        logging.Logger: Configured logger.
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    
    # Clear any existing handlers
    logger.handlers = []
    
    # Set up console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = LogFormatter(color_enabled=color_enabled, json_enabled=json_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Set up file handler if specified
    if log_file:
        # Ensure directory exists
        log_dir = os.path.dirname(os.path.abspath(log_file))
        os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_formatter = LogFormatter(color_enabled=False, json_enabled=json_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = None, level: int = logging.INFO) -> logging.Logger:
    """
    Get a logger with basic configuration.
    
    Args:
        name (str, optional): Logger name.
        level (int): Logging level.
        
    Returns:
        logging.Logger: Configured logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Add handler if no handlers exist
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(LogFormatter())
        logger.addHandler(handler)
    
    return logger