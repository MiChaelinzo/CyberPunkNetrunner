#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHANTOM Crypto Utilities

Cryptographic helper functions and utilities.
"""

import hashlib
import base64
import secrets
import string
from typing import Optional


class CryptoUtils:
    """Cryptographic utility functions"""
    
    @staticmethod
    def md5(data: str) -> str:
        """Calculate MD5 hash"""
        return hashlib.md5(data.encode()).hexdigest()
    
    @staticmethod
    def sha1(data: str) -> str:
        """Calculate SHA1 hash"""
        return hashlib.sha1(data.encode()).hexdigest()
    
    @staticmethod
    def sha256(data: str) -> str:
        """Calculate SHA256 hash"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def sha512(data: str) -> str:
        """Calculate SHA512 hash"""
        return hashlib.sha512(data.encode()).hexdigest()
    
    @staticmethod
    def base64_encode(data: str) -> str:
        """Base64 encode"""
        return base64.b64encode(data.encode()).decode()
    
    @staticmethod
    def base64_decode(data: str) -> Optional[str]:
        """Base64 decode"""
        try:
            return base64.b64decode(data).decode()
        except Exception:
            return None
    
    @staticmethod
    def hex_encode(data: str) -> str:
        """Hex encode"""
        return data.encode().hex()
    
    @staticmethod
    def hex_decode(data: str) -> Optional[str]:
        """Hex decode"""
        try:
            return bytes.fromhex(data).decode()
        except Exception:
            return None
    
    @staticmethod
    def generate_random_string(length: int = 32) -> str:
        """Generate random string"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def generate_password(length: int = 16, special: bool = True) -> str:
        """Generate secure password"""
        chars = string.ascii_letters + string.digits
        if special:
            chars += string.punctuation
        return ''.join(secrets.choice(chars) for _ in range(length))
    
    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Generate secure token"""
        return secrets.token_hex(length // 2)
    
    @staticmethod
    def constant_time_compare(a: str, b: str) -> bool:
        """Constant-time string comparison"""
        return secrets.compare_digest(a, b)
    
    @staticmethod
    def file_md5(filepath: str) -> str:
        """Calculate MD5 of file"""
        hash_md5 = hashlib.md5()
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""
    
    @staticmethod
    def file_sha256(filepath: str) -> str:
        """Calculate SHA256 of file"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return ""
