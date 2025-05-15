class DependencyInjector:
    """
    Simple dependency injection container
    """
    
    def __init__(self):
        """Initialize with empty container"""
        self.services = {}
        
    def register(self, name, instance):
        """
        Register a service with the container
        
        Args:
            name: Service name
            instance: Service instance
        """
        self.services[name] = instance
        
    def resolve(self, name):
        """
        Resolve a service by name
        
        Args:
            name: Service name
            
        Returns:
            The registered service instance
            
        Raises:
            KeyError: If the service is not registered
        """
        if name not in self.services:
            raise KeyError(f"Service '{name}' not registered")
            
        return self.services[name]