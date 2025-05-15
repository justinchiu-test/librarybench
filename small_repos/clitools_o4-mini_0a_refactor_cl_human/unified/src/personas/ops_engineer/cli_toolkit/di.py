"""
Dependency injection container for the CLI Toolkit.
"""
from typing import Any, Dict, Optional, Callable, TypeVar, Type

T = TypeVar('T')

class DIContainer:
    """
    A simple dependency injection container.
    """
    
    def __init__(self):
        """Initialize a new DI container."""
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[[], Any]] = {}
        self._singleton_factories: Dict[str, Callable[[], Any]] = {}
        self._singleton_instances: Dict[str, Any] = {}
    
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
        Register a factory function that creates a service instance.
        
        Args:
            name: Service name
            factory: Factory function
        """
        self._factories[name] = factory
    
    def register_singleton(self, name: str, factory: Callable[[], Any]) -> None:
        """
        Register a singleton factory that creates a service instance once.
        
        Args:
            name: Service name
            factory: Factory function
        """
        self._singleton_factories[name] = factory
    
    def get(self, name: str) -> Optional[Any]:
        """
        Get a service instance by name.
        
        Args:
            name: Service name
            
        Returns:
            Service instance or None if not found
        """
        # Check for direct service
        if name in self._services:
            return self._services[name]
        
        # Check for singleton instance
        if name in self._singleton_instances:
            return self._singleton_instances[name]
        
        # Check for singleton factory
        if name in self._singleton_factories:
            instance = self._singleton_factories[name]()
            self._singleton_instances[name] = instance
            return instance
        
        # Check for factory
        if name in self._factories:
            return self._factories[name]()
        
        return None
    
    def get_typed(self, name: str, cls: Type[T]) -> Optional[T]:
        """
        Get a service instance by name and type.
        
        Args:
            name: Service name
            cls: Expected type
            
        Returns:
            Service instance or None if not found or not of expected type
        """
        instance = self.get(name)
        
        if instance is None:
            return None
        
        if not isinstance(instance, cls):
            return None
        
        return instance
    
    def has(self, name: str) -> bool:
        """
        Check if a service is registered.
        
        Args:
            name: Service name
            
        Returns:
            True if service is registered
        """
        return (
            name in self._services or
            name in self._factories or
            name in self._singleton_factories or
            name in self._singleton_instances
        )
    
    def remove(self, name: str) -> bool:
        """
        Remove a service.
        
        Args:
            name: Service name
            
        Returns:
            True if service was removed
        """
        removed = False
        
        if name in self._services:
            del self._services[name]
            removed = True
        
        if name in self._factories:
            del self._factories[name]
            removed = True
        
        if name in self._singleton_factories:
            del self._singleton_factories[name]
            removed = True
        
        if name in self._singleton_instances:
            del self._singleton_instances[name]
            removed = True
        
        return removed
    
    def clear(self) -> None:
        """Clear all services."""
        self._services.clear()
        self._factories.clear()
        self._singleton_factories.clear()
        self._singleton_instances.clear()

# Global container instance
_container = DIContainer()

def get_container() -> DIContainer:
    """
    Get the global DI container.
    
    Returns:
        Global DIContainer instance
    """
    return _container


class Container:
    """
    Simple dependency injection container for the OpsEngineer CLI toolkit.
    """
    
    def __init__(self):
        """Initialize a new Container."""
        self._registry = {}
        self._instances = {}
    
    def register(self, name: str, factory: Callable[['Container'], Any]) -> None:
        """
        Register a factory function for a component.
        
        Args:
            name: Component name
            factory: Factory function that takes a container instance and returns a component
        """
        self._registry[name] = factory
    
    def resolve(self, name: str) -> Any:
        """
        Resolve a component by name.
        
        Args:
            name: Component name
            
        Returns:
            Component instance
            
        Raises:
            KeyError: If component is not registered
        """
        # Return existing instance if already created
        if name in self._instances:
            return self._instances[name]
        
        # Check if factory exists
        if name not in self._registry:
            raise KeyError(f"Component not registered: {name}")
        
        # Create instance using factory
        factory = self._registry[name]
        instance = factory(self)
        
        # Cache the instance
        self._instances[name] = instance
        
        return instance