"""Log formatting utilities for query language interpreters."""

import logging
from typing import Any, Dict, Optional
import json
from datetime import datetime


class LogFormatter:
    """Formatter for log messages."""

    def __init__(
        self,
        format_string: Optional[str] = None,
        include_timestamp: bool = True,
        include_level: bool = True,
        include_name: bool = True,
        json_format: bool = False,
    ):
        """Initialize a log formatter.

        Args:
            format_string: Custom log format string (None for default)
            include_timestamp: Whether to include timestamp
            include_level: Whether to include log level
            include_name: Whether to include logger name
            json_format: Whether to format logs as JSON
        """
        self.format_string = format_string
        self.include_timestamp = include_timestamp
        self.include_level = include_level
        self.include_name = include_name
        self.json_format = json_format

    def get_formatter(self) -> logging.Formatter:
        """Get a logging.Formatter instance.

        Returns:
            logging.Formatter: Formatter instance
        """
        if self.format_string:
            return logging.Formatter(self.format_string)

        if self.json_format:
            return JsonFormatter(
                include_timestamp=self.include_timestamp,
                include_level=self.include_level,
                include_name=self.include_name,
            )

        # Build format string
        format_parts = []

        if self.include_timestamp:
            format_parts.append("%(asctime)s")

        if self.include_level:
            format_parts.append("%(levelname)s")

        if self.include_name:
            format_parts.append("%(name)s")

        format_parts.append("%(message)s")

        format_string = " | ".join(format_parts)
        return logging.Formatter(format_string)


class JsonFormatter(logging.Formatter):
    """Format log records as JSON."""

    def __init__(
        self,
        include_timestamp: bool = True,
        include_level: bool = True,
        include_name: bool = True,
    ):
        """Initialize a JSON formatter.

        Args:
            include_timestamp: Whether to include timestamp
            include_level: Whether to include log level
            include_name: Whether to include logger name
        """
        super().__init__()
        self.include_timestamp = include_timestamp
        self.include_level = include_level
        self.include_name = include_name

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as JSON.

        Args:
            record: Log record to format

        Returns:
            str: JSON-formatted log message
        """
        log_data: Dict[str, Any] = {}

        # Include standard fields if requested
        if self.include_timestamp:
            log_data["timestamp"] = self.formatTime(record)

        if self.include_level:
            log_data["level"] = record.levelname

        if self.include_name:
            log_data["logger"] = record.name

        # Always include the message
        log_data["message"] = record.getMessage()

        # Include exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Include all extra attributes
        for key, value in record.__dict__.items():
            if key not in {
                "args",
                "asctime",
                "created",
                "exc_info",
                "exc_text",
                "filename",
                "funcName",
                "id",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "msg",
                "name",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "thread",
                "threadName",
            }:
                log_data[key] = value

        return json.dumps(log_data, default=str)
