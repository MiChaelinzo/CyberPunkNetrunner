#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHANTOM Logger - Advanced Logging System

Provides comprehensive logging with colorized output,
file rotation, and forensic-grade audit trails.
"""

import os
import sys
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from enum import Enum
from logging.handlers import RotatingFileHandler


class LogLevel(Enum):
    """Log severity levels"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
    AUDIT = 25  # Custom level for security auditing


class ColorFormatter(logging.Formatter):
    """Custom formatter with color support"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'AUDIT': '\033[94m',      # Light Blue
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        record.msg = f"{color}{record.msg}{self.RESET}"
        return super().format(record)


class AuditFormatter(logging.Formatter):
    """JSON formatter for audit logs"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
        }
        
        if hasattr(record, 'extra_data'):
            log_data['extra'] = record.extra_data
        
        return json.dumps(log_data)


class PhantomLogger:
    """
    Advanced Logging System for PHANTOM
    
    Features:
    - Colorized console output
    - Rotating file logs
    - JSON audit trails
    - Performance metrics
    - Security event tracking
    """
    
    _instances: Dict[str, 'PhantomLogger'] = {}
    
    def __init__(self, name: str = "PHANTOM", log_dir: Optional[str] = None):
        self.name = name
        self.log_dir = log_dir or str(Path.home() / ".phantom" / "logs")
        self._setup_logging()
    
    @classmethod
    def get_logger(cls, name: str = "PHANTOM") -> 'PhantomLogger':
        """Get or create a logger instance"""
        if name not in cls._instances:
            cls._instances[name] = cls(name)
        return cls._instances[name]
    
    def _setup_logging(self):
        """Initialize logging configuration"""
        # Create log directory
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Create custom AUDIT level
        logging.addLevelName(LogLevel.AUDIT.value, 'AUDIT')
        
        # Get or create logger
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        self.logger.handlers = []
        
        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(ColorFormatter(
            '[%(asctime)s] %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        ))
        self.logger.addHandler(console_handler)
        
        # File handler with rotation
        file_handler = RotatingFileHandler(
            os.path.join(self.log_dir, 'phantom.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(module)s:%(lineno)d] - %(message)s'
        ))
        self.logger.addHandler(file_handler)
        
        # Audit log handler (JSON format)
        audit_handler = RotatingFileHandler(
            os.path.join(self.log_dir, 'audit.json'),
            maxBytes=50*1024*1024,  # 50MB
            backupCount=10
        )
        audit_handler.setLevel(LogLevel.AUDIT.value)
        audit_handler.setFormatter(AuditFormatter())
        self.logger.addHandler(audit_handler)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, extra={'extra_data': kwargs} if kwargs else {})
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, extra={'extra_data': kwargs} if kwargs else {})
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, extra={'extra_data': kwargs} if kwargs else {})
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.logger.error(message, extra={'extra_data': kwargs} if kwargs else {})
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self.logger.critical(message, extra={'extra_data': kwargs} if kwargs else {})
    
    def audit(self, message: str, **kwargs):
        """Log security audit event"""
        self.logger.log(LogLevel.AUDIT.value, message, extra={'extra_data': kwargs})
    
    def operation_start(self, operation: str, target: str = ""):
        """Log start of an operation"""
        self.audit(f"Operation started: {operation}", target=target, status="started")
    
    def operation_end(self, operation: str, success: bool, details: str = ""):
        """Log end of an operation"""
        status = "success" if success else "failed"
        self.audit(f"Operation ended: {operation}", status=status, details=details)
    
    def security_event(self, event_type: str, details: Dict[str, Any]):
        """Log a security-relevant event"""
        self.audit(f"Security Event: {event_type}", **details)


# Global logger instance
logger = PhantomLogger.get_logger()
