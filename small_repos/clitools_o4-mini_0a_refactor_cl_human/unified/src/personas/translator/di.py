"""
Dependency injection module for the Translator persona.
"""
from typing import Dict, Any, Optional, Type


class DIContainer:
    """
    Simple dependency injection container implementation.
    """
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, callable] = {}
        self._singletons: Dict[str, Any] = {}

    def register(self, name: str, instance: Any) -> None:
        """
        Register a service instance.
        
        Args:
            name: Service identifier
            instance: Service instance
        """
        self._services[name] = instance

    def register_factory(self, name: str, factory: callable) -> None:
        """
        Register a factory function for a service.
        
        Args:
            name: Service identifier
            factory: Factory function that creates the service
        """
        self._factories[name] = factory

    def register_singleton(self, name: str, factory: callable) -> None:
        """
        Register a singleton factory.
        
        Args:
            name: Service identifier
            factory: Factory function that creates the singleton
        """
        self._factories[name] = factory
        # Mark it as a singleton but don't create it yet
        self._singletons[name] = None

    def get(self, name: str) -> Optional[Any]:
        """
        Get a service by name.
        
        Args:
            name: Service identifier
            
        Returns:
            The requested service or None if not found
        """
        # Direct service
        if name in self._services:
            return self._services[name]
        
        # Singleton that needs to be created
        if name in self._singletons:
            if self._singletons[name] is None:
                self._singletons[name] = self._factories[name]()
            return self._singletons[name]
        
        # Factory-created service
        if name in self._factories:
            return self._factories[name]()
        
        return None

    def remove(self, name: str) -> bool:
        """
        Remove a service by name.
        
        Args:
            name: Service identifier
            
        Returns:
            True if service was removed, False otherwise
        """
        if name in self._services:
            del self._services[name]
            return True
        
        if name in self._factories:
            del self._factories[name]
            if name in self._singletons:
                del self._singletons[name]
            return True
        
        return False


# Global container instance
_container = DIContainer()


def get_container() -> DIContainer:
    """
    Get the global DI container.
    
    Returns:
        Global DIContainer instance
    """
    return _container


class DependencyInjector:
    """
    Simple dependency injector for the Translator tool.
    """
    
    def __init__(self):
        """Initialize a new dependency injector."""
        self._registry = {}
    
    def register(self, name: str, service: Any) -> None:
        """
        Register a service.
        
        Args:
            name: Service name
            service: Service instance
        """
        self._registry[name] = service
    
    def resolve(self, name: str) -> Any:
        """
        Resolve a service by name.
        
        Args:
            name: Service name
            
        Returns:
            Service instance
            
        Raises:
            KeyError: If service is not registered
        """
        if name not in self._registry:
            raise KeyError(f"Service not registered: {name}")
        
        return self._registry[name]