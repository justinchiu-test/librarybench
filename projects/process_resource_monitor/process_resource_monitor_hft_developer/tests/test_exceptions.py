import pytest

from hft_resource_monitor.exceptions import (
    MonitorError, ConfigurationError, PermissionError,
    ProcessNotFoundError, HardwareNotSupportedError
)


class TestExceptions:
    """Test custom exception classes"""
    
    def test_monitor_error_base(self):
        """Test base MonitorError exception"""
        with pytest.raises(MonitorError) as exc_info:
            raise MonitorError("Base monitor error")
        
        assert str(exc_info.value) == "Base monitor error"
        assert isinstance(exc_info.value, Exception)
    
    def test_configuration_error(self):
        """Test ConfigurationError exception"""
        with pytest.raises(ConfigurationError) as exc_info:
            raise ConfigurationError("Invalid configuration")
        
        assert str(exc_info.value) == "Invalid configuration"
        assert isinstance(exc_info.value, MonitorError)
        assert isinstance(exc_info.value, Exception)
    
    def test_permission_error(self):
        """Test PermissionError exception"""
        with pytest.raises(PermissionError) as exc_info:
            raise PermissionError("Insufficient permissions")
        
        assert str(exc_info.value) == "Insufficient permissions"
        assert isinstance(exc_info.value, MonitorError)
    
    def test_process_not_found_error(self):
        """Test ProcessNotFoundError exception"""
        with pytest.raises(ProcessNotFoundError) as exc_info:
            raise ProcessNotFoundError("Process 12345 not found")
        
        assert str(exc_info.value) == "Process 12345 not found"
        assert isinstance(exc_info.value, MonitorError)
    
    def test_hardware_not_supported_error(self):
        """Test HardwareNotSupportedError exception"""
        with pytest.raises(HardwareNotSupportedError) as exc_info:
            raise HardwareNotSupportedError("CPU does not support performance counters")
        
        assert str(exc_info.value) == "CPU does not support performance counters"
        assert isinstance(exc_info.value, MonitorError)
    
    def test_exception_inheritance(self):
        """Test that all custom exceptions inherit from MonitorError"""
        # All custom exceptions should be catchable as MonitorError
        exceptions = [
            ConfigurationError("test"),
            PermissionError("test"),
            ProcessNotFoundError("test"),
            HardwareNotSupportedError("test")
        ]
        
        for exc in exceptions:
            assert isinstance(exc, MonitorError)
            assert isinstance(exc, Exception)
    
    def test_exception_context(self):
        """Test exception can carry context information"""
        try:
            # Simulate a configuration error with context
            invalid_value = -10
            if invalid_value < 0:
                raise ConfigurationError(
                    f"Sampling interval must be positive, got {invalid_value}"
                )
        except ConfigurationError as e:
            assert "-10" in str(e)
            assert "positive" in str(e)