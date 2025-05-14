"""
Dependency injection for translator CLI tools.
"""

from typing import Dict, Any, Optional


class DependencyInjector:
    """Simple dependency injector."""
    
    def __init__(self):
        """Initialize an empty dependency injector."""
        self._registry = {}
    
    def register(self, name: str, instance: Any) -> None:
        """
        Register a service instance.
        
        Args:
            name (str): Service name.
            instance (Any): Service instance.
        """
        self._registry[name] = instance
    
    def resolve(self, name: str) -> Any:
        """
        Resolve a service by name.
        
        Args:
            name (str): Service name.
            
        Returns:
            Any: Service instance.
            
        Raises:
            KeyError: If service is not registered.
        """
        if name not in self._registry:
            raise KeyError(f"Service not registered: {name}")
        
        return self._registry[name]