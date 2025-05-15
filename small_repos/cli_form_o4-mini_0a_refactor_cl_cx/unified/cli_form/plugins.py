"""
Plugin System for cli_form

This module provides a plugin architecture for extending cli_form with custom
field types, renderers, and other components.
"""

import importlib
import inspect
import pkgutil
import sys
from typing import Dict, List, Callable, Any, Type, Optional


class PluginRegistry:
    """Registry of plugins for the form system."""
    
    def __init__(self):
        """Initialize an empty plugin registry."""
        self.field_types = {}
        self.renderers = {}
        self.validators = {}
        self.exporters = {}
        self.hooks = {}
    
    def register_field_type(self, name, field_class):
        """
        Register a custom field type.
        
        Args:
            name (str): Field type name
            field_class (type): Field class
            
        Returns:
            bool: True if registration succeeded
        """
        if name in self.field_types:
            return False
            
        self.field_types[name] = field_class
        return True
    
    def register_renderer(self, name, renderer_class):
        """
        Register a custom renderer.
        
        Args:
            name (str): Renderer name
            renderer_class (type): Renderer class
            
        Returns:
            bool: True if registration succeeded
        """
        if name in self.renderers:
            return False
            
        self.renderers[name] = renderer_class
        return True
    
    def register_validator(self, name, validator_func):
        """
        Register a custom validator function.
        
        Args:
            name (str): Validator name
            validator_func (callable): Validator function
            
        Returns:
            bool: True if registration succeeded
        """
        if name in self.validators:
            return False
            
        self.validators[name] = validator_func
        return True
    
    def register_exporter(self, name, exporter_func):
        """
        Register a custom exporter function.
        
        Args:
            name (str): Exporter name
            exporter_func (callable): Exporter function
            
        Returns:
            bool: True if registration succeeded
        """
        if name in self.exporters:
            return False
            
        self.exporters[name] = exporter_func
        return True
    
    def register_hook(self, event, hook_func):
        """
        Register a hook function for a specific event.
        
        Args:
            event (str): Event name
            hook_func (callable): Hook function
            
        Returns:
            bool: True if registration succeeded
        """
        if event not in self.hooks:
            self.hooks[event] = []
            
        self.hooks[event].append(hook_func)
        return True
    
    def get_field_type(self, name):
        """
        Get a field type by name.
        
        Args:
            name (str): Field type name
            
        Returns:
            type: Field class
        """
        return self.field_types.get(name)
    
    def get_renderer(self, name):
        """
        Get a renderer by name.
        
        Args:
            name (str): Renderer name
            
        Returns:
            type: Renderer class
        """
        return self.renderers.get(name)
    
    def get_validator(self, name):
        """
        Get a validator by name.
        
        Args:
            name (str): Validator name
            
        Returns:
            callable: Validator function
        """
        return self.validators.get(name)
    
    def get_exporter(self, name):
        """
        Get an exporter by name.
        
        Args:
            name (str): Exporter name
            
        Returns:
            callable: Exporter function
        """
        return self.exporters.get(name)
    
    def get_hooks(self, event):
        """
        Get all hooks for an event.
        
        Args:
            event (str): Event name
            
        Returns:
            list: List of hook functions
        """
        return self.hooks.get(event, [])
    
    def trigger_hooks(self, event, *args, **kwargs):
        """
        Trigger all hooks for an event.
        
        Args:
            event (str): Event name
            *args: Positional arguments for hooks
            **kwargs: Keyword arguments for hooks
            
        Returns:
            list: Results from all hooks
        """
        results = []
        for hook in self.get_hooks(event):
            results.append(hook(*args, **kwargs))
        return results


# Global plugin registry
_registry = PluginRegistry()


def get_registry():
    """
    Get the global plugin registry.
    
    Returns:
        PluginRegistry: The global registry
    """
    global _registry
    return _registry


def register_field_plugin(name, field_class):
    """
    Register a field type plugin.
    
    Args:
        name (str): Field type name
        field_class (type): Field class
        
    Returns:
        bool: True if registration succeeded
    """
    global _registry
    return _registry.register_field_type(name, field_class)


def register_renderer_plugin(name, renderer_class):
    """
    Register a renderer plugin.
    
    Args:
        name (str): Renderer name
        renderer_class (type): Renderer class
        
    Returns:
        bool: True if registration succeeded
    """
    global _registry
    return _registry.register_renderer(name, renderer_class)


def register_validator_plugin(name, validator_func):
    """
    Register a validator plugin.
    
    Args:
        name (str): Validator name
        validator_func (callable): Validator function
        
    Returns:
        bool: True if registration succeeded
    """
    global _registry
    return _registry.register_validator(name, validator_func)


def register_exporter_plugin(name, exporter_func):
    """
    Register an exporter plugin.
    
    Args:
        name (str): Exporter name
        exporter_func (callable): Exporter function
        
    Returns:
        bool: True if registration succeeded
    """
    global _registry
    return _registry.register_exporter(name, exporter_func)


def register_hook(event, hook_func):
    """
    Register a hook for an event.
    
    Args:
        event (str): Event name
        hook_func (callable): Hook function
        
    Returns:
        bool: True if registration succeeded
    """
    global _registry
    return _registry.register_hook(event, hook_func)


def discover_plugins(package_name):
    """
    Auto-discover plugins in a package.
    
    Args:
        package_name (str): Package name to scan
        
    Returns:
        int: Number of plugins discovered
    """
    try:
        package = importlib.import_module(package_name)
    except ImportError:
        return 0
        
    prefix = package.__name__ + "."
    count = 0
    
    for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__, prefix):
        if not is_pkg:
            try:
                module = importlib.import_module(module_name)
                
                # Look for plugin registration function
                if hasattr(module, 'register_plugins'):
                    module.register_plugins()
                    count += 1
                    
                # Auto-discover field types
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                            hasattr(obj, 'register_as_field_type') and 
                            getattr(obj, 'register_as_field_type', False)):
                        register_field_plugin(obj.field_type_name, obj)
                        count += 1
                        
            except ImportError:
                continue
                
    return count