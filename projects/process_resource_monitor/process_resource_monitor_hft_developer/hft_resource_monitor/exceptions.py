class MonitorError(Exception):
    """Base exception for HFT Resource Monitor"""
    pass


class ConfigurationError(MonitorError):
    """Raised when monitor configuration is invalid"""
    pass


class PermissionError(MonitorError):
    """Raised when insufficient permissions for hardware access"""
    pass


class ProcessNotFoundError(MonitorError):
    """Raised when target process cannot be found"""
    pass


class HardwareNotSupportedError(MonitorError):
    """Raised when required hardware features are not available"""
    pass