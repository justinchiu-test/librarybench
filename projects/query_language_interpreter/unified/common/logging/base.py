"""Base logging functionality for query language interpreters."""

import logging
from typing import Any, Dict, List, Optional, Set, Union
import os
import sys
from datetime import datetime

from common.logging.formatter import LogFormatter


class LogLevel:
    """Log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class BaseLogger:
    """Base class for logging systems."""

    def __init__(
        self,
        name: str,
        log_file: Optional[str] = None,
        console: bool = True,
        level: str = LogLevel.INFO,
    ):
        """Initialize a base logger.

        Args:
            name: Logger name
            log_file: Path to log file (None for no file logging)
            console: Whether to log to console
            level: Minimum log level
        """
        self.name = name
        self.log_file = log_file
        self.console = console
        self.level = level

        # Create the logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self._get_log_level(level))
        self.logger.handlers = []  # Clear any existing handlers

        # Create formatter
        formatter = LogFormatter().get_formatter()

        # Add file handler if log_file is specified
        if log_file:
            # Ensure directory exists
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)

            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        # Add console handler if console is True
        if console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def _get_log_level(self, level: str) -> int:
        """Convert string log level to logging module constant.

        Args:
            level: String log level

        Returns:
            int: Logging module log level constant
        """
        level_map = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.CRITICAL: logging.CRITICAL,
        }
        return level_map.get(level.upper(), logging.INFO)

    def log(self, level: str, message: str, **kwargs) -> None:
        """Log a message with the specified level.

        Args:
            level: Log level
            message: Message to log
            **kwargs: Additional log context
        """
        log_method = getattr(self.logger, level.lower(), self.logger.info)

        # Format with kwargs if provided
        if kwargs:
            context_str = " ".join(f"{k}={v}" for k, v in kwargs.items())
            message = f"{message} [{context_str}]"

        log_method(message)

    def debug(self, message: str, **kwargs) -> None:
        """Log a debug message.

        Args:
            message: Message to log
            **kwargs: Additional log context
        """
        self.log(LogLevel.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log an info message.

        Args:
            message: Message to log
            **kwargs: Additional log context
        """
        self.log(LogLevel.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log a warning message.

        Args:
            message: Message to log
            **kwargs: Additional log context
        """
        self.log(LogLevel.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log an error message.

        Args:
            message: Message to log
            **kwargs: Additional log context
        """
        self.log(LogLevel.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """Log a critical message.

        Args:
            message: Message to log
            **kwargs: Additional log context
        """
        self.log(LogLevel.CRITICAL, message, **kwargs)

    def set_level(self, level: str) -> None:
        """Set the log level.

        Args:
            level: New log level
        """
        self.level = level
        self.logger.setLevel(self._get_log_level(level))
