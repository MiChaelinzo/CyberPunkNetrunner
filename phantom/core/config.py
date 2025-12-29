#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHANTOM Configuration Manager

Handles all system configuration, settings persistence,
and environment management.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum


class LogLevel(Enum):
    """Logging verbosity levels"""
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


@dataclass
class NetworkConfig:
    """Network-related configuration"""
    proxy_enabled: bool = False
    proxy_host: str = ""
    proxy_port: int = 8080
    proxy_type: str = "http"
    timeout: int = 30
    max_retries: int = 3
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


@dataclass
class SecurityConfig:
    """Security-related configuration"""
    anonymity_mode: bool = False
    tor_enabled: bool = False
    tor_port: int = 9050
    vpn_check: bool = True
    dns_leak_protection: bool = True
    mac_spoofing: bool = False


@dataclass
class DisplayConfig:
    """Display and UI configuration"""
    color_enabled: bool = True
    banner_enabled: bool = True
    verbose_output: bool = True
    animation_enabled: bool = True
    theme: str = "cyberpunk"


@dataclass
class PhantomConfig:
    """
    Master Configuration Container for PHANTOM
    
    Manages all system settings and provides persistence
    through JSON/YAML configuration files.
    """
    
    # Core settings
    version: str = "3.0.0"
    codename: str = "PHANTOM"
    operations_dir: str = field(default_factory=lambda: str(Path.home() / "phantom_ops"))
    log_level: str = "INFO"
    log_file: str = field(default_factory=lambda: str(Path.home() / ".phantom" / "phantom.log"))
    
    # Sub-configurations
    network: NetworkConfig = field(default_factory=NetworkConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    display: DisplayConfig = field(default_factory=DisplayConfig)
    
    # Runtime settings
    last_session: str = ""
    installed_modules: list = field(default_factory=list)
    custom_scripts: list = field(default_factory=list)
    api_keys: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "PhantomConfig":
        """Load configuration from file"""
        if config_path is None:
            config_path = str(Path.home() / ".phantom" / "config.yaml")
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                        data = yaml.safe_load(f)
                    else:
                        data = json.load(f)
                
                return cls._from_dict(data)
            except Exception as e:
                print(f"[!] Error loading config: {e}")
                return cls()
        
        return cls()
    
    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> "PhantomConfig":
        """Create config from dictionary"""
        config = cls()
        
        for key, value in data.items():
            if hasattr(config, key):
                if key == 'network' and isinstance(value, dict):
                    setattr(config, key, NetworkConfig(**value))
                elif key == 'security' and isinstance(value, dict):
                    setattr(config, key, SecurityConfig(**value))
                elif key == 'display' and isinstance(value, dict):
                    setattr(config, key, DisplayConfig(**value))
                else:
                    setattr(config, key, value)
        
        return config
    
    def save(self, config_path: Optional[str] = None):
        """Save configuration to file"""
        if config_path is None:
            config_path = str(Path.home() / ".phantom" / "config.yaml")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # Convert to dictionary
        data = self._to_dict()
        
        with open(config_path, 'w') as f:
            if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                yaml.dump(data, f, default_flow_style=False)
            else:
                json.dump(data, f, indent=2)
    
    def _to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        data = {}
        for key, value in self.__dict__.items():
            if hasattr(value, '__dict__'):
                data[key] = asdict(value)
            else:
                data[key] = value
        return data
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        keys = key.split('.')
        value = self
        
        for k in keys:
            if hasattr(value, k):
                value = getattr(value, k)
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value by key"""
        keys = key.split('.')
        obj = self
        
        for k in keys[:-1]:
            if hasattr(obj, k):
                obj = getattr(obj, k)
            else:
                return False
        
        if hasattr(obj, keys[-1]):
            setattr(obj, keys[-1], value)
            return True
        
        return False
    
    def reset_to_defaults(self):
        """Reset configuration to default values"""
        default = PhantomConfig()
        for key in self.__dict__:
            setattr(self, key, getattr(default, key))
    
    def validate(self) -> bool:
        """Validate configuration values"""
        errors = []
        
        # Validate operations directory
        if not self.operations_dir:
            errors.append("Operations directory not set")
        
        # Validate network settings
        if self.network.proxy_enabled and not self.network.proxy_host:
            errors.append("Proxy enabled but no host specified")
        
        # Validate security settings
        if self.security.tor_enabled and self.security.tor_port < 1:
            errors.append("Invalid TOR port")
        
        if errors:
            for error in errors:
                print(f"[!] Config Error: {error}")
            return False
        
        return True


# Default configuration instance
DEFAULT_CONFIG = PhantomConfig()
