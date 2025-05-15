import functools
import inspect

# Global dependency container
_dependencies = {}

def init_di(dependencies):
    """
    Initialize the dependency injection container
    
    Args:
        dependencies: Dictionary of service names to service instances
    """
    global _dependencies
    _dependencies = dependencies

def inject(func):
    """
    Decorator to inject dependencies into a function based on parameter names
    
    Args:
        func: The function to inject dependencies into
        
    Returns:
        Wrapped function with dependencies injected
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get the function signature
        sig = inspect.signature(func)
        
        # Create a dict of dependencies to inject
        to_inject = {}
        
        # For each parameter in the function signature
        for param_name in sig.parameters:
            # If it's not already in kwargs and it's in the dependency container
            if param_name not in kwargs and param_name in _dependencies:
                to_inject[param_name] = _dependencies[param_name]
                
        # Update kwargs with the dependencies
        kwargs.update(to_inject)
        
        # Call the original function with the injected dependencies
        return func(*args, **kwargs)
        
    return wrapper