"""
Logging setup module for translator tools.
Configures logging for translation operations.
"""

import os
import sys
import logging
import logging.handlers
from enum import Enum
from typing import Dict, List, Optional, Union


class LogLevel(Enum):
    """Standard log levels."""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class LogFormat(Enum):
    """Predefined log formats."""
    SIMPLE = "%(message)s"
    STANDARD = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DETAILED = "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d) - %(message)s"
    JSON = '{"time": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s"}'


class LoggingSetup:
    """
    Configures and manages logging for translation tools.
    Provides easy setup for common logging scenarios.
    """
    
    def __init__(self, 
                name: str = "translator",
                level: Union[LogLevel, str, int] = LogLevel.INFO,
                format: Union[LogFormat, str] = LogFormat.STANDARD,
                log_file: Optional[str] = None,
                console: bool = True,
                max_bytes: int = 10485760,  # 10 MB
                backup_count: int = 5):
        """
        Initialize logging setup.
        
        Args:
            name: Logger name
            level: Log level
            format: Log format
            log_file: Path to log file (None for no file logging)
            console: Whether to log to console
            max_bytes: Maximum log file size in bytes
            backup_count: Number of backup files to keep
        """
        self.name = name
        self.level = self._parse_level(level)
        self.format = self._parse_format(format)
        self.log_file = log_file
        self.console = console
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.logger = logging.getLogger(name)
        
        # Configure logging
        self._configure()
    
    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """
        Get a logger instance.
        
        Args:
            name: Logger name (appended to base name)
            
        Returns:
            Logger instance
        """
        if name:
            return logging.getLogger(f"{self.name}.{name}")
        return self.logger
    
    def set_level(self, level: Union[LogLevel, str, int]) -> None:
        """
        Set log level.
        
        Args:
            level: New log level
        """
        self.level = self._parse_level(level)
        self.logger.setLevel(self.level)
        
        # Update handler levels
        for handler in self.logger.handlers:
            handler.setLevel(self.level)
    
    def add_file_handler(self, 
                        log_file: str,
                        level: Optional[Union[LogLevel, str, int]] = None,
                        format: Optional[Union[LogFormat, str]] = None,
                        max_bytes: int = 10485760,
                        backup_count: int = 5) -> None:
        """
        Add a file handler.
        
        Args:
            log_file: Path to log file
            level: Log level for this handler
            format: Log format for this handler
            max_bytes: Maximum log file size in bytes
            backup_count: Number of backup files to keep
        """
        # Create directory if needed
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Create handler
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        
        # Set level
        if level is not None:
            handler.setLevel(self._parse_level(level))
        else:
            handler.setLevel(self.level)
        
        # Set formatter
        if format is not None:
            formatter = logging.Formatter(self._parse_format(format))
        else:
            formatter = logging.Formatter(self.format)
        
        handler.setFormatter(formatter)
        
        # Add to logger
        self.logger.addHandler(handler)
    
    def add_console_handler(self, 
                           level: Optional[Union[LogLevel, str, int]] = None,
                           format: Optional[Union[LogFormat, str]] = None) -> None:
        """
        Add a console handler.
        
        Args:
            level: Log level for this handler
            format: Log format for this handler
        """
        # Create handler
        handler = logging.StreamHandler(sys.stdout)
        
        # Set level
        if level is not None:
            handler.setLevel(self._parse_level(level))
        else:
            handler.setLevel(self.level)
        
        # Set formatter
        if format is not None:
            formatter = logging.Formatter(self._parse_format(format))
        else:
            formatter = logging.Formatter(self.format)
        
        handler.setFormatter(formatter)
        
        # Add to logger
        self.logger.addHandler(handler)
    
    def _configure(self) -> None:
        """Configure logging."""
        # Reset any existing configuration
        self.logger.handlers = []
        
        # Set level
        self.logger.setLevel(self.level)
        
        # Create formatter
        formatter = logging.Formatter(self.format)
        
        # Add console handler
        if self.console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.level)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # Add file handler
        if self.log_file:
            # Create directory if needed
            log_dir = os.path.dirname(self.log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                self.log_file,
                maxBytes=self.max_bytes,
                backupCount=self.backup_count
            )
            file_handler.setLevel(self.level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def _parse_level(self, level: Union[LogLevel, str, int]) -> int:
        """
        Parse log level to integer value.
        
        Args:
            level: Log level to parse
            
        Returns:
            Integer log level
        """
        if isinstance(level, LogLevel):
            return level.value
        elif isinstance(level, str):
            # Try to parse as level name
            upper_level = level.upper()
            if hasattr(logging, upper_level):
                return getattr(logging, upper_level)
            
            # Try to parse as LogLevel enum
            try:
                return LogLevel[upper_level].value
            except KeyError:
                # Try to parse as integer
                try:
                    return int(level)
                except ValueError:
                    # Default to INFO
                    return logging.INFO
        else:
            # Assume it's already an integer level
            return level
    
    def _parse_format(self, format: Union[LogFormat, str]) -> str:
        """
        Parse log format to string.
        
        Args:
            format: Log format to parse
            
        Returns:
            Format string
        """
        if isinstance(format, LogFormat):
            return format.value
        else:
            return format


# Create a global logging setup for convenience
_global_logging_setup = LoggingSetup()

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger from the global logging setup."""
    return _global_logging_setup.get_logger(name)

def set_level(level: Union[LogLevel, str, int]) -> None:
    """Set log level for the global logging setup."""
    _global_logging_setup.set_level(level)

def add_file_handler(log_file: str, 
                   level: Optional[Union[LogLevel, str, int]] = None,
                   format: Optional[Union[LogFormat, str]] = None,
                   max_bytes: int = 10485760,
                   backup_count: int = 5) -> None:
    """Add a file handler to the global logging setup."""
    _global_logging_setup.add_file_handler(log_file, level, format, max_bytes, backup_count)

def add_console_handler(level: Optional[Union[LogLevel, str, int]] = None,
                      format: Optional[Union[LogFormat, str]] = None) -> None:
    """Add a console handler to the global logging setup."""
    _global_logging_setup.add_console_handler(level, format)

def configure(name: str = "translator",
             level: Union[LogLevel, str, int] = LogLevel.INFO,
             format: Union[LogFormat, str] = LogFormat.STANDARD,
             log_file: Optional[str] = None,
             console: bool = True,
             max_bytes: int = 10485760,
             backup_count: int = 5) -> None:
    """Configure the global logging setup."""
    global _global_logging_setup
    _global_logging_setup = LoggingSetup(name, level, format, log_file, console, max_bytes, backup_count)


def setup_logging(json_format: bool = False, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a basic logger with console output.
    
    Args:
        json_format: Whether to use JSON format
        level: Log level
        
    Returns:
        Configured logger
    """
    # Create logger
    logger = logging.getLogger("translator")
    logger.setLevel(level)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    # Create formatter
    if json_format:
        formatter = logging.Formatter('{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}')
    else:
        formatter = logging.Formatter('%(levelname)s:%(message)s')
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger