"""
Dependency injection container for Data Pipeline CLI.
"""
from typing import Dict, Any, Optional, Callable, TypeVar, Type, get_type_hints
import functools
import inspect

T = TypeVar('T')

class DIContainer:
    """
    Simple dependency injection container.
    """
    
    def __init__(self):
        """Initialize a new DI container."""
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[[], Any]] = {}
        self._singletons: Dict[str, bool] = {}
    
    def register(self, name: str, instance: Any) -> None:
        """
        Register a service instance.
        
        Args:
            name: Service name
            instance: Service instance
        """
        self._services[name] = instance
    
    def register_factory(self, name: str, factory: Callable[[], Any]) -> None:
        """
        Register a factory function that creates a service.
        
        Args:
            name: Service name
            factory: Factory function
        """
        self._factories[name] = factory
        self._singletons[name] = False
    
    def register_singleton(self, name: str, factory: Callable[[], Any]) -> None:
        """
        Register a singleton factory.
        
        Args:
            name: Service name
            factory: Factory function
        """
        self._factories[name] = factory
        self._singletons[name] = True
    
    def get(self, name: str) -> Optional[Any]:
        """
        Get a service by name.
        
        Args:
            name: Service name
            
        Returns:
            Service instance or None if not found
        """
        # Return existing service if registered
        if name in self._services:
            return self._services[name]
        
        # Create service from factory if registered
        if name in self._factories:
            instance = self._factories[name]()
            
            # Cache singleton instances
            if self._singletons.get(name, False):
                self._services[name] = instance
            
            return instance
        
        return None
    
    def get_typed(self, name: str, cls: Type[T]) -> Optional[T]:
        """
        Get a service by name and type.
        
        Args:
            name: Service name
            cls: Expected service type
            
        Returns:
            Service instance or None if not found or not of expected type
            
        Raises:
            TypeError: If service is not of expected type
        """
        service = self.get(name)
        
        if service is None:
            return None
        
        if not isinstance(service, cls):
            raise TypeError(f"Service '{name}' is not of type {cls.__name__}")
        
        return service
    
    def remove(self, name: str) -> bool:
        """
        Remove a service by name.
        
        Args:
            name: Service name
            
        Returns:
            True if service was removed, False if not found
        """
        removed = False
        
        if name in self._services:
            del self._services[name]
            removed = True
        
        if name in self._factories:
            del self._factories[name]
            removed = True
        
        if name in self._singletons:
            del self._singletons[name]
            removed = True
        
        return removed

# Global container instance
_container = DIContainer()

def get_container() -> DIContainer:
    """
    Get the global container instance.
    
    Returns:
        Global DIContainer instance
    """
    return _container


def init_di(services: Dict[str, Any]) -> None:
    """
    Initialize the global DI container with services.
    
    Args:
        services: Dictionary of service name to service instance
    """
    container = get_container()
    for name, service in services.items():
        container.register(name, service)


def inject(func: Callable) -> Callable:
    """
    Decorator for dependency injection.
    
    Args:
        func: Function to inject dependencies into
        
    Returns:
        Wrapped function with dependencies injected
    """
    sig = inspect.signature(func)
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        container = get_container()
        
        # Create a dictionary to hold arguments to pass to the function
        call_args = {}
        
        # Add positional arguments
        positional_params = list(sig.parameters.keys())[:len(args)]
        for i, arg in enumerate(args):
            call_args[positional_params[i]] = arg
        
        # Add keyword arguments
        call_args.update(kwargs)
        
        # Inject missing dependencies from container
        for param_name in sig.parameters:
            if param_name not in call_args:
                # Inject the dependency
                service = container.get(param_name)
                if service is not None:
                    call_args[param_name] = service
        
        return func(**call_args)
    
    return wrapper