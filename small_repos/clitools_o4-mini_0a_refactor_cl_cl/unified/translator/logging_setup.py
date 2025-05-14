"""
Logging setup for translator CLI tools.
"""

import json
import logging
import sys
from typing import Dict, Any, Optional


class JSONFormatter(logging.Formatter):
    """JSON formatter for logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record as JSON.
        
        Args:
            record (logging.LogRecord): Log record.
            
        Returns:
            str: JSON-formatted log entry.
        """
        log_data = {
            'level': record.levelname,
            'message': record.getMessage(),
            'timestamp': self.formatTime(record),
            'module': record.module,
            'function': record.funcName,
        }
        
        # Add exception info if available
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


class SimpleFormatter(logging.Formatter):
    """Simple text formatter for logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record as simple text.
        
        Args:
            record (logging.LogRecord): Log record.
            
        Returns:
            str: Formatted log entry.
        """
        return f"{record.levelname}:{record.getMessage()}"


def setup_logging(json_format: bool = False, level: int = logging.INFO) -> logging.Logger:
    """
    Set up logging with the specified format and level.
    
    Args:
        json_format (bool): Whether to use JSON format.
        level (int): Logging level.
        
    Returns:
        logging.Logger: Configured logger.
    """
    # Create logger
    logger = logging.getLogger('translator')
    logger.setLevel(level)
    logger.handlers = []  # Remove existing handlers
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    # Set formatter
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = SimpleFormatter()
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger