"""
Dependency Injection (DI) module for CLI tools.
Manages and injects dependencies for services and commands.
"""

import inspect
from typing import Any, Callable, Dict, Optional, Set, Type


class DependencyInjector:
    """
    Simple dependency injection container.
    Provides registration and resolution of dependencies.
    """
    
    def __init__(self):
        """Initialize a new dependency injector."""
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[..., Any]] = {}
        self._singletons: Set[str] = set()
    
    def register(self, 
                name: str, 
                service: Any, 
                singleton: bool = True) -> None:
        """
        Register a service instance directly.
        
        Args:
            name: Name to register the service under
            service: Service instance
            singleton: Whether this is a singleton service
        """
        self._services[name] = service
        if singleton:
            self._singletons.add(name)
    
    def register_factory(self, 
                        name: str, 
                        factory: Callable[..., Any], 
                        singleton: bool = True) -> None:
        """
        Register a factory function for a service.
        
        Args:
            name: Name to register the service under
            factory: Factory function that creates the service
            singleton: Whether to create only one instance
        """
        self._factories[name] = factory
        if singleton:
            self._singletons.add(name)
    
    def register_class(self, 
                      name: str, 
                      cls: Type, 
                      singleton: bool = True) -> None:
        """
        Register a class as a service.
        
        Args:
            name: Name to register the service under
            cls: Class to instantiate when requested
            singleton: Whether to create only one instance
        """
        def factory(**kwargs):
            return cls(**kwargs)
        
        self.register_factory(name, factory, singleton)
    
    def get(self, name: str, **kwargs) -> Any:
        """
        Get a service by name, instantiating it if needed.
        
        Args:
            name: Name of the service to get
            **kwargs: Additional arguments to pass to the factory
            
        Returns:
            The requested service
            
        Raises:
            KeyError: If the service is not registered
        """
        # Check if it's already instantiated
        if name in self._services:
            return self._services[name]
        
        # Check if it can be instantiated
        if name in self._factories:
            # Get the factory
            factory = self._factories[name]
            
            # Resolve dependencies for the factory
            factory_args = self._resolve_dependencies(factory, **kwargs)
            
            # Create the instance
            instance = factory(**factory_args)
            
            # Store if it's a singleton
            if name in self._singletons:
                self._services[name] = instance
            
            return instance
        
        raise KeyError(f"No service registered with name '{name}'")
    
    def _resolve_dependencies(self, 
                            factory: Callable[..., Any], 
                            **explicit_kwargs) -> Dict[str, Any]:
        """
        Resolve dependencies for a factory function.
        
        Args:
            factory: Factory function to resolve dependencies for
            **explicit_kwargs: Explicitly provided dependencies
            
        Returns:
            Dictionary of resolved dependencies
        """
        sig = inspect.signature(factory)
        args = {}
        
        for param_name, param in sig.parameters.items():
            # Skip *args and **kwargs
            if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
                continue
            
            # Use explicitly provided value if available
            if param_name in explicit_kwargs:
                args[param_name] = explicit_kwargs[param_name]
                continue
                
            # Try to resolve from container
            if param_name in self._services or param_name in self._factories:
                args[param_name] = self.get(param_name)
                continue
                
            # Check if parameter has a default value
            if param.default is not inspect.Parameter.empty:
                args[param_name] = param.default
                continue
                
            # Unable to resolve this dependency
            raise ValueError(f"Unable to resolve dependency '{param_name}'")
        
        return args
    
    def call_with_injection(self, func: Callable[..., Any], **kwargs) -> Any:
        """
        Call a function with its dependencies injected.
        
        Args:
            func: Function to call
            **kwargs: Explicit arguments to override
            
        Returns:
            Result of the function call
        """
        args = self._resolve_dependencies(func, **kwargs)
        return func(**args)


class Inject:
    """
    Decorator for dependency injection.
    Automatically injects dependencies when the function is called.
    """
    
    def __init__(self, container: Optional[DependencyInjector] = None):
        """
        Initialize the decorator.
        
        Args:
            container: DependencyInjector to use (default: global instance)
        """
        self.container = container or _global_container
    
    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Decorate a function for dependency injection.
        
        Args:
            func: Function to decorate
            
        Returns:
            Decorated function
        """
        def wrapper(*args, **kwargs):
            # Combine positional args with their param names
            sig = inspect.signature(func)
            bound_args = sig.bind_partial(*args)
            bound_args.apply_defaults()
            all_kwargs = dict(bound_args.arguments)
            
            # Add explicit kwargs
            all_kwargs.update(kwargs)
            
            # Call with remaining dependencies injected
            return self.container.call_with_injection(func, **all_kwargs)
        
        return wrapper


# Create a global container for convenience
_global_container = DependencyInjector()

# Convenience functions that use the global container
def register(name: str, service: Any, singleton: bool = True) -> None:
    """Register a service instance in the global container."""
    _global_container.register(name, service, singleton)

def register_factory(name: str, factory: Callable[..., Any], singleton: bool = True) -> None:
    """Register a factory function in the global container."""
    _global_container.register_factory(name, factory, singleton)

def register_class(name: str, cls: Type, singleton: bool = True) -> None:
    """Register a class in the global container."""
    _global_container.register_class(name, cls, singleton)

def get(name: str, **kwargs) -> Any:
    """Get a service from the global container."""
    return _global_container.get(name, **kwargs)

def call_with_injection(func: Callable[..., Any], **kwargs) -> Any:
    """Call a function with dependencies injected from the global container."""
    return _global_container.call_with_injection(func, **kwargs)

# Create a default decorator that uses the global container
inject = Inject()