"""
Dependency injection for operations engineer CLI tools.
"""

from typing import Dict, Any, Callable, Optional


class Container:
    """Dependency injection container."""
    
    def __init__(self):
        """Initialize an empty container."""
        self._services: Dict[str, Callable] = {}
        self._instances: Dict[str, Any] = {}
    
    def register(self, service_name: str, factory: Callable) -> None:
        """
        Register a service factory.
        
        Args:
            service_name (str): Service name.
            factory (Callable): Factory function that creates the service.
        """
        self._services[service_name] = factory
    
    def resolve(self, service_name: str) -> Any:
        """
        Resolve a service.
        
        Args:
            service_name (str): Service name.
            
        Returns:
            Any: Service instance.
            
        Raises:
            KeyError: If service is not registered.
        """
        # Check if already instantiated
        if service_name in self._instances:
            return self._instances[service_name]
        
        # Check if service is registered
        if service_name not in self._services:
            raise KeyError(f"Service not registered: {service_name}")
        
        # Create instance
        factory = self._services[service_name]
        instance = factory(self)
        
        # Cache instance
        self._instances[service_name] = instance
        
        return instance