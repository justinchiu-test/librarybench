"""Function decorators for configuration injection."""
import inspect
import functools
from typing import Dict, Any, Optional, Callable, TypeVar, cast

from ..core.config_manager import ConfigManager
from ..utils.type_converter import convert_value

T = TypeVar('T')


def with_config(config_path: Optional[str] = None):
    """Decorator for injecting configuration values into function arguments.
    
    Args:
        config_path: Path to the configuration file or section
        
    Returns:
        A decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if config_path is not None and '.' not in config_path and config_path not in ConfigManager._config:
                # Assume it's a file path
                ConfigManager.load(config_path)
                
            # Get the signature of the function
            sig = inspect.signature(func)
            params = sig.parameters
            
            # Check if the first parameter is self
            has_self = False
            skip_first = False
            
            if params:
                first_param = next(iter(params.values()))
                if first_param.name == 'self' and args:
                    has_self = True
                    skip_first = True
                    
            # Prepare arguments to inject
            injected_kwargs = {}
            
            for name, param in params.items():
                if skip_first:
                    skip_first = False
                    continue
                    
                if name in kwargs:
                    # Parameter already provided
                    continue
                    
                # Calculate the config path to check
                check_path = name
                if config_path is not None:
                    # If config_path doesn't contain dots, assume it's a section
                    if '.' not in config_path and config_path in ConfigManager._config:
                        check_path = f"{config_path}.{name}"
                    elif config_path in ConfigManager._config:
                        check_path = config_path
                
                # Special case: if the parameter is named 'config' or 'cfg', inject the ConfigManager
                if name in ('config', 'cfg') and name not in kwargs:
                    if config_path is not None:
                        if '.' in config_path or config_path not in ConfigManager._config:
                            # Assume it's a file path - create a ConfigManager for it
                            try:
                                cm = ConfigManager(config_path)
                                injected_kwargs[name] = cm
                                continue
                            except Exception:
                                pass
                        else:
                            # Assume it's a section
                            try:
                                section_data = ConfigManager.get(config_path)
                                cm = ConfigManager(config_data=section_data)
                                injected_kwargs[name] = cm
                                continue
                            except Exception:
                                pass
                                
                    # Default: inject a ConfigManager with the current config
                    injected_kwargs[name] = ConfigManager(config_data=ConfigManager._config)
                    continue
                
                # Try to get the value from the configuration
                try:
                    value = ConfigManager.get(check_path)
                    
                    # Try to convert the value to the expected type
                    if param.annotation != inspect.Parameter.empty:
                        try:
                            value = convert_value(value, param.annotation)
                        except (ValueError, TypeError):
                            # If conversion fails, use the value as-is
                            pass
                            
                    injected_kwargs[name] = value
                except KeyError:
                    # Value not found in configuration, but the parameter might have a default
                    if param.default != inspect.Parameter.empty:
                        continue
                        
                    # No default, prompt for the value
                    from ..interactive.prompt import prompt_for_value
                    value = prompt_for_value(name, param.annotation)
                    
                    if param.annotation != inspect.Parameter.empty:
                        try:
                            value = convert_value(value, param.annotation)
                        except (ValueError, TypeError):
                            # If conversion fails, use the value as-is
                            pass
                            
                    ConfigManager.set(check_path, value)
                    injected_kwargs[name] = value
                    
            # Call the function with the injected arguments
            if has_self:
                return func(args[0], **{**injected_kwargs, **kwargs})
            else:
                return func(*args, **{**injected_kwargs, **kwargs})
                
        return wrapper
        
    # Handle the case where the decorator is used without arguments
    if callable(config_path):
        func = config_path
        config_path = None
        return decorator(func)
        
    return decorator