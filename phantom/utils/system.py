#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHANTOM System Utilities

System-level helper functions and utilities.
"""

import os
import sys
import platform
import subprocess
import shutil
from typing import Dict, Any, List, Optional
from pathlib import Path


class SystemUtils:
    """System utility functions"""
    
    @staticmethod
    def get_system_info() -> Dict[str, str]:
        """Get system information"""
        return {
            'os': platform.system(),
            'os_release': platform.release(),
            'os_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'hostname': platform.node(),
            'user': os.getenv('USER', 'unknown'),
        }
    
    @staticmethod
    def is_root() -> bool:
        """Check if running as root"""
        return os.geteuid() == 0 if hasattr(os, 'geteuid') else False
    
    @staticmethod
    def check_command_exists(command: str) -> bool:
        """Check if command exists"""
        return shutil.which(command) is not None
    
    @staticmethod
    def run_command(command: str, timeout: int = 30) -> Dict[str, Any]:
        """Run shell command and return result"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Command timed out'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_env_var(name: str, default: str = "") -> str:
        """Get environment variable"""
        return os.getenv(name, default)
    
    @staticmethod
    def set_env_var(name: str, value: str):
        """Set environment variable"""
        os.environ[name] = value
    
    @staticmethod
    def get_home_dir() -> str:
        """Get user home directory"""
        return str(Path.home())
    
    @staticmethod
    def ensure_dir(path: str) -> bool:
        """Ensure directory exists"""
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_file_size(filepath: str) -> int:
        """Get file size in bytes"""
        try:
            return os.path.getsize(filepath)
        except Exception:
            return 0
    
    @staticmethod
    def read_file(filepath: str) -> str:
        """Read file contents"""
        try:
            with open(filepath, 'r') as f:
                return f.read()
        except Exception:
            return ""
    
    @staticmethod
    def write_file(filepath: str, content: str) -> bool:
        """Write content to file"""
        try:
            with open(filepath, 'w') as f:
                f.write(content)
            return True
        except Exception:
            return False
    
    @staticmethod
    def clear_screen():
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def get_terminal_size() -> tuple:
        """Get terminal size"""
        try:
            size = shutil.get_terminal_size()
            return (size.columns, size.lines)
        except Exception:
            return (80, 24)
    
    @staticmethod
    def install_package(package: str, pip_cmd: str = "pip3") -> bool:
        """Install Python package"""
        try:
            subprocess.run([pip_cmd, 'install', package], check=True)
            return True
        except Exception:
            return False
    
    @staticmethod
    def check_dependencies(packages: List[str]) -> Dict[str, bool]:
        """Check if Python packages are installed"""
        results = {}
        for package in packages:
            try:
                __import__(package)
                results[package] = True
            except ImportError:
                results[package] = False
        return results
