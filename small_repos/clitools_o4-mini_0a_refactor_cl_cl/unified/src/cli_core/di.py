"""
Dependency Injection module for CLI tools.

This module provides a simple DI container for managing service dependencies.
"""
import functools
import inspect


class DIContainer:
    """
    Simple dependency injection container.

    Manages service registration and resolution with singleton support.
    """

    def __init__(self, dependencies=None):
        """
        Initialize the DI container with optional dependencies.

        Args:
            dependencies (dict): Dictionary mapping service names to their classes or factory functions.
        """
        self._dependencies = dependencies or {}
        self._instances = {}

    def register(self, name, dependency):
        """
        Register a dependency.

        Args:
            name (str): The name of the dependency.
            dependency: The class or factory function for the dependency.
        """
        self._dependencies[name] = dependency

    def resolve(self, name):
        """
        Resolve a dependency.

        Args:
            name (str): The name of the dependency to resolve.

        Returns:
            The dependency instance.

        Raises:
            KeyError: If the dependency is not registered.
        """
        if name not in self._dependencies:
            raise KeyError(f"Dependency '{name}' not registered")

        # Return existing instance if available (singleton pattern)
        if name in self._instances:
            return self._instances[name]

        # Create new instance
        dependency = self._dependencies[name]
        instance = dependency() if callable(dependency) else dependency

        # Cache instance
        self._instances[name] = instance
        return instance

    def get_all_dependencies(self):
        """
        Get all registered dependencies.

        Returns:
            dict: Dictionary of all registered dependencies.
        """
        return self._dependencies.copy()


# Global DI container
_container = None


def init_di(dependencies=None):
    """
    Initialize the global DI container with the given dependencies.

    Args:
        dependencies (dict): Dictionary mapping service names to their classes or factory functions.

    Returns:
        DIContainer: Initialized DI container.
    """
    global _container
    _container = DIContainer(dependencies)
    return _container


def inject(func):
    """
    Decorator that injects dependencies into a function based on parameter names.

    Args:
        func: The function to inject dependencies into.

    Returns:
        A wrapped function with dependencies automatically injected.

    Example:
        @inject
        def process_data(data_service, logger):
            # data_service and logger will be automatically injected
            # from the DI container based on parameter names
            data_service.process()
            logger.info("Data processed")
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        global _container
        if _container is None:
            _container = DIContainer()

        # Get the function's parameter names
        sig = inspect.signature(func)
        param_names = list(sig.parameters.keys())[len(args):]

        # Inject dependencies for parameters not provided in args or kwargs
        for name in param_names:
            if name not in kwargs and name in _container._dependencies:
                kwargs[name] = _container.resolve(name)

        return func(*args, **kwargs)

    return wrapper