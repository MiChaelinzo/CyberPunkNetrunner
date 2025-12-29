#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHANTOM Base Plugin Class

Template for creating custom PHANTOM plugins.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BasePlugin(ABC):
    """
    Base class for PHANTOM plugins
    
    All custom plugins should inherit from this class
    and implement the required methods.
    
    Example:
    ```python
    class MyPlugin(BasePlugin):
        PLUGIN_INFO = {
            'name': 'My Plugin',
            'version': '1.0.0',
            'author': 'Your Name',
            'description': 'Plugin description',
            'category': 'recon'
        }
        
        def initialize(self):
            print("Plugin initialized")
            return True
        
        def execute(self, target, **options):
            # Your plugin logic here
            return {'success': True, 'data': {}}
        
        def cleanup(self):
            print("Cleaning up")
    ```
    """
    
    # Plugin information - override in subclass
    PLUGIN_INFO: Dict[str, Any] = {
        'name': 'Base Plugin',
        'version': '1.0.0',
        'author': 'PHANTOM Team',
        'description': 'Base plugin class',
        'category': 'general',
        'dependencies': [],
    }
    
    # Optional hook definitions
    HOOKS: Dict[str, callable] = {}
    
    def __init__(self):
        """Initialize plugin"""
        self.initialized = False
        self.options: Dict[str, Any] = {}
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the plugin
        
        Called when the plugin is loaded. Use this to set up
        any required resources.
        
        Returns:
            bool: True if initialization successful
        """
        pass
    
    @abstractmethod
    def execute(self, target: str, **options) -> Dict[str, Any]:
        """
        Execute the plugin's main functionality
        
        Args:
            target: The target to operate on
            **options: Additional options
        
        Returns:
            dict: Results of the execution
        """
        pass
    
    def cleanup(self):
        """
        Cleanup plugin resources
        
        Called when the plugin is unloaded or PHANTOM exits.
        Override to clean up any resources.
        """
        pass
    
    def set_option(self, key: str, value: Any):
        """Set a plugin option"""
        self.options[key] = value
    
    def get_option(self, key: str, default: Any = None) -> Any:
        """Get a plugin option"""
        return self.options.get(key, default)
    
    def log(self, message: str, level: str = "info"):
        """Log a message"""
        icons = {
            "info": "[*]",
            "success": "[+]",
            "warning": "[!]",
            "error": "[-]",
            "debug": "[#]"
        }
        icon = icons.get(level, "[*]")
        print(f"{icon} [{self.PLUGIN_INFO['name']}] {message}")
    
    def require_root(self) -> bool:
        """Check if running as root"""
        import os
        return os.geteuid() == 0 if hasattr(os, 'geteuid') else False
    
    def check_dependencies(self) -> bool:
        """Check if all dependencies are available"""
        for dep in self.PLUGIN_INFO.get('dependencies', []):
            try:
                __import__(dep)
            except ImportError:
                self.log(f"Missing dependency: {dep}", "error")
                return False
        return True
    
    def get_info(self) -> Dict[str, Any]:
        """Get plugin information"""
        return self.PLUGIN_INFO.copy()
    
    def __str__(self) -> str:
        """String representation"""
        return f"{self.PLUGIN_INFO['name']} v{self.PLUGIN_INFO['version']}"
    
    def __repr__(self) -> str:
        """Detailed representation"""
        return f"<Plugin: {self.PLUGIN_INFO['name']}>"
