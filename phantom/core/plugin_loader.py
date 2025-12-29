#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHANTOM Plugin Manager

Extensible plugin architecture for adding custom modules
and extending framework capabilities.
"""

import os
import sys
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, Any, List, Optional, Type
from dataclasses import dataclass, field
from abc import ABC, abstractmethod


@dataclass
class PluginMetadata:
    """Plugin metadata container"""
    name: str
    version: str
    author: str
    description: str
    category: str
    dependencies: List[str] = field(default_factory=list)
    enabled: bool = True


class PluginManager:
    """
    PHANTOM Plugin Management System
    
    Handles:
    - Plugin discovery
    - Dynamic loading
    - Dependency resolution
    - Lifecycle management
    """
    
    def __init__(self, plugin_dirs: Optional[List[str]] = None):
        self.plugin_dirs = plugin_dirs or [
            str(Path.home() / ".phantom" / "plugins"),
            str(Path(__file__).parent.parent / "plugins"),
        ]
        self._plugins: Dict[str, Any] = {}
        self._metadata: Dict[str, PluginMetadata] = {}
        self._hooks: Dict[str, List[callable]] = {}
    
    def discover_plugins(self) -> List[str]:
        """Discover available plugins"""
        discovered = []
        
        for plugin_dir in self.plugin_dirs:
            if not os.path.exists(plugin_dir):
                continue
            
            for item in os.listdir(plugin_dir):
                item_path = os.path.join(plugin_dir, item)
                
                # Check for plugin module
                if item.endswith('.py') and item != '__init__.py':
                    plugin_name = item[:-3]
                    discovered.append(plugin_name)
                
                # Check for plugin package
                elif os.path.isdir(item_path):
                    init_file = os.path.join(item_path, '__init__.py')
                    if os.path.exists(init_file):
                        discovered.append(item)
        
        return discovered
    
    def load_plugin(self, plugin_name: str) -> bool:
        """Load a specific plugin"""
        for plugin_dir in self.plugin_dirs:
            # Try module file
            module_path = os.path.join(plugin_dir, f"{plugin_name}.py")
            if os.path.exists(module_path):
                return self._load_module(plugin_name, module_path)
            
            # Try package directory
            package_path = os.path.join(plugin_dir, plugin_name)
            if os.path.isdir(package_path):
                init_path = os.path.join(package_path, "__init__.py")
                if os.path.exists(init_path):
                    return self._load_package(plugin_name, package_path)
        
        return False
    
    def _load_module(self, name: str, path: str) -> bool:
        """Load plugin from module file"""
        try:
            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            
            # Look for plugin class
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and hasattr(attr, 'PLUGIN_INFO'):
                    self._register_plugin(name, attr)
                    return True
            
            return False
        except Exception as e:
            print(f"[!] Error loading plugin {name}: {e}")
            return False
    
    def _load_package(self, name: str, path: str) -> bool:
        """Load plugin from package directory"""
        try:
            init_path = os.path.join(path, "__init__.py")
            return self._load_module(name, init_path)
        except Exception as e:
            print(f"[!] Error loading plugin package {name}: {e}")
            return False
    
    def _register_plugin(self, name: str, plugin_class: Type):
        """Register a loaded plugin"""
        info = plugin_class.PLUGIN_INFO
        
        metadata = PluginMetadata(
            name=info.get('name', name),
            version=info.get('version', '1.0.0'),
            author=info.get('author', 'Unknown'),
            description=info.get('description', ''),
            category=info.get('category', 'general'),
            dependencies=info.get('dependencies', []),
        )
        
        self._metadata[name] = metadata
        self._plugins[name] = plugin_class()
        
        # Register hooks
        if hasattr(plugin_class, 'HOOKS'):
            for hook_name, callback in plugin_class.HOOKS.items():
                self.register_hook(hook_name, callback)
    
    def load_all_plugins(self):
        """Load all discovered plugins"""
        discovered = self.discover_plugins()
        loaded = 0
        
        for plugin_name in discovered:
            if self.load_plugin(plugin_name):
                loaded += 1
        
        return loaded
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin"""
        if plugin_name in self._plugins:
            plugin = self._plugins[plugin_name]
            
            # Call cleanup if available
            if hasattr(plugin, 'cleanup'):
                plugin.cleanup()
            
            del self._plugins[plugin_name]
            del self._metadata[plugin_name]
            
            return True
        
        return False
    
    def get_plugin(self, plugin_name: str) -> Optional[Any]:
        """Get a loaded plugin instance"""
        return self._plugins.get(plugin_name)
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all loaded plugins"""
        return [
            {
                'name': meta.name,
                'version': meta.version,
                'author': meta.author,
                'description': meta.description,
                'category': meta.category,
                'enabled': meta.enabled,
            }
            for meta in self._metadata.values()
        ]
    
    def register_hook(self, hook_name: str, callback: callable):
        """Register a hook callback"""
        if hook_name not in self._hooks:
            self._hooks[hook_name] = []
        self._hooks[hook_name].append(callback)
    
    def trigger_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Trigger all callbacks for a hook"""
        results = []
        
        for callback in self._hooks.get(hook_name, []):
            try:
                result = callback(*args, **kwargs)
                results.append(result)
            except Exception as e:
                print(f"[!] Hook error in {hook_name}: {e}")
        
        return results
    
    def get_plugins_by_category(self, category: str) -> List[str]:
        """Get plugins in a specific category"""
        return [
            name for name, meta in self._metadata.items()
            if meta.category == category
        ]
