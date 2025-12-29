#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHANTOM Crypto Analyzer Module

Cryptographic analysis, hash cracking,
and encryption/decryption utilities.
"""

import hashlib
import base64
import string
import itertools
from typing import Dict, Any, List, Optional, Generator
from dataclasses import dataclass
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed


class HashType(Enum):
    """Supported hash types"""
    MD5 = "md5"
    SHA1 = "sha1"
    SHA256 = "sha256"
    SHA512 = "sha512"
    NTLM = "ntlm"
    BCRYPT = "bcrypt"


@dataclass
class HashInfo:
    """Hash information container"""
    hash_value: str
    hash_type: HashType
    cracked: bool = False
    plaintext: str = ""


class HashIdentifier:
    """Identify hash types"""
    
    PATTERNS = {
        HashType.MD5: (32, r'^[a-fA-F0-9]{32}$'),
        HashType.SHA1: (40, r'^[a-fA-F0-9]{40}$'),
        HashType.SHA256: (64, r'^[a-fA-F0-9]{64}$'),
        HashType.SHA512: (128, r'^[a-fA-F0-9]{128}$'),
        HashType.NTLM: (32, r'^[a-fA-F0-9]{32}$'),
        HashType.BCRYPT: (60, r'^\$2[ayb]\$.+'),
    }
    
    def identify(self, hash_value: str) -> List[HashType]:
        """Identify possible hash types"""
        import re
        
        possible_types = []
        hash_len = len(hash_value)
        
        for hash_type, (expected_len, pattern) in self.PATTERNS.items():
            if hash_len == expected_len:
                if re.match(pattern, hash_value):
                    possible_types.append(hash_type)
        
        return possible_types


class HashCracker:
    """Hash cracking engine"""
    
    def __init__(self, threads: int = 4):
        self.threads = threads
        self.found = False
        self.result = ""
    
    def _hash_string(self, plaintext: str, hash_type: HashType) -> str:
        """Hash a string"""
        if hash_type == HashType.MD5:
            return hashlib.md5(plaintext.encode()).hexdigest()
        elif hash_type == HashType.SHA1:
            return hashlib.sha1(plaintext.encode()).hexdigest()
        elif hash_type == HashType.SHA256:
            return hashlib.sha256(plaintext.encode()).hexdigest()
        elif hash_type == HashType.SHA512:
            return hashlib.sha512(plaintext.encode()).hexdigest()
        elif hash_type == HashType.NTLM:
            return hashlib.new('md4', plaintext.encode('utf-16le')).hexdigest()
        return ""
    
    def dictionary_attack(self, hash_value: str, hash_type: HashType, wordlist_path: str) -> Optional[str]:
        """Crack hash using dictionary attack"""
        hash_value = hash_value.lower()
        
        try:
            with open(wordlist_path, 'r', errors='ignore') as f:
                for line in f:
                    word = line.strip()
                    if self._hash_string(word, hash_type) == hash_value:
                        return word
        except Exception as e:
            print(f"[-] Error reading wordlist: {e}")
        
        return None
    
    def brute_force(self, hash_value: str, hash_type: HashType, charset: str = None, min_len: int = 1, max_len: int = 6) -> Optional[str]:
        """Crack hash using brute force"""
        hash_value = hash_value.lower()
        charset = charset or string.ascii_lowercase + string.digits
        
        for length in range(min_len, max_len + 1):
            print(f"[*] Trying length {length}...")
            for attempt in itertools.product(charset, repeat=length):
                plaintext = ''.join(attempt)
                if self._hash_string(plaintext, hash_type) == hash_value:
                    return plaintext
        
        return None
    
    def rainbow_lookup(self, hash_value: str) -> Optional[str]:
        """Lookup hash in online rainbow tables"""
        # Note: This would require external API access
        # Placeholder for demonstration
        return None


class Encoder:
    """Encoding and decoding utilities"""
    
    @staticmethod
    def base64_encode(data: str) -> str:
        """Base64 encode"""
        return base64.b64encode(data.encode()).decode()
    
    @staticmethod
    def base64_decode(data: str) -> str:
        """Base64 decode"""
        try:
            return base64.b64decode(data).decode()
        except Exception:
            return ""
    
    @staticmethod
    def hex_encode(data: str) -> str:
        """Hex encode"""
        return data.encode().hex()
    
    @staticmethod
    def hex_decode(data: str) -> str:
        """Hex decode"""
        try:
            return bytes.fromhex(data).decode()
        except Exception:
            return ""
    
    @staticmethod
    def rot13(data: str) -> str:
        """ROT13 cipher"""
        result = []
        for char in data:
            if char.isalpha():
                shift = 13
                if char.isupper():
                    result.append(chr((ord(char) - ord('A') + shift) % 26 + ord('A')))
                else:
                    result.append(chr((ord(char) - ord('a') + shift) % 26 + ord('a')))
            else:
                result.append(char)
        return ''.join(result)
    
    @staticmethod
    def caesar_cipher(data: str, shift: int) -> str:
        """Caesar cipher"""
        result = []
        for char in data:
            if char.isalpha():
                if char.isupper():
                    result.append(chr((ord(char) - ord('A') + shift) % 26 + ord('A')))
                else:
                    result.append(chr((ord(char) - ord('a') + shift) % 26 + ord('a')))
            else:
                result.append(char)
        return ''.join(result)
    
    @staticmethod
    def xor_cipher(data: str, key: str) -> str:
        """XOR cipher"""
        result = []
        key_len = len(key)
        for i, char in enumerate(data):
            result.append(chr(ord(char) ^ ord(key[i % key_len])))
        return ''.join(result)


class KeyGenerator:
    """Cryptographic key generation"""
    
    @staticmethod
    def generate_random_bytes(length: int = 32) -> bytes:
        """Generate random bytes"""
        import os
        return os.urandom(length)
    
    @staticmethod
    def generate_password(length: int = 16, use_special: bool = True) -> str:
        """Generate secure password"""
        import secrets
        
        charset = string.ascii_letters + string.digits
        if use_special:
            charset += string.punctuation
        
        return ''.join(secrets.choice(charset) for _ in range(length))
    
    @staticmethod
    def generate_uuid() -> str:
        """Generate UUID"""
        import uuid
        return str(uuid.uuid4())


class SteganographyAnalyzer:
    """Analyze files for hidden data"""
    
    def detect_hidden_data(self, filepath: str) -> Dict[str, Any]:
        """Detect potential hidden data in file"""
        results = {
            'file': filepath,
            'suspicious_indicators': [],
            'entropy': 0.0
        }
        
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
            
            # Calculate entropy
            results['entropy'] = self._calculate_entropy(data)
            
            # Check for known steganography signatures
            if results['entropy'] > 7.9:
                results['suspicious_indicators'].append("High entropy - possible encryption or compression")
            
            # Check for appended data after file end
            results['suspicious_indicators'].extend(self._check_appended_data(data, filepath))
            
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy"""
        import math
        from collections import Counter
        
        if not data:
            return 0.0
        
        counter = Counter(data)
        length = len(data)
        
        entropy = 0.0
        for count in counter.values():
            if count > 0:
                prob = count / length
                entropy -= prob * math.log2(prob)
        
        return entropy
    
    def _check_appended_data(self, data: bytes, filepath: str) -> List[str]:
        """Check for appended data after file end"""
        indicators = []
        
        # Check for JPEG
        if filepath.lower().endswith(('.jpg', '.jpeg')):
            end_marker = data.rfind(b'\xff\xd9')
            if end_marker != -1 and end_marker < len(data) - 2:
                indicators.append(f"Data found after JPEG end marker ({len(data) - end_marker - 2} bytes)")
        
        # Check for PNG
        if filepath.lower().endswith('.png'):
            end_marker = data.rfind(b'IEND')
            if end_marker != -1 and end_marker < len(data) - 12:
                indicators.append(f"Data found after PNG IEND chunk")
        
        return indicators


class CryptoAnalyzer:
    """
    Master Crypto Analysis Module
    
    Provides:
    - Hash identification
    - Hash cracking
    - Encoding/decoding
    - Key generation
    - Steganography detection
    """
    
    def __init__(self):
        self.hash_identifier = HashIdentifier()
        self.hash_cracker = HashCracker()
        self.encoder = Encoder()
        self.key_generator = KeyGenerator()
        self.steg_analyzer = SteganographyAnalyzer()
    
    def identify_hash(self, hash_value: str) -> List[str]:
        """Identify possible hash types"""
        types = self.hash_identifier.identify(hash_value)
        return [t.value for t in types]
    
    def crack_hash(self, hash_value: str, method: str = "dictionary", **kwargs) -> Optional[str]:
        """Crack a hash"""
        types = self.hash_identifier.identify(hash_value)
        if not types:
            print("[-] Could not identify hash type")
            return None
        
        hash_type = types[0]
        
        if method == "dictionary":
            wordlist = kwargs.get('wordlist', '/usr/share/wordlists/rockyou.txt')
            return self.hash_cracker.dictionary_attack(hash_value, hash_type, wordlist)
        elif method == "bruteforce":
            return self.hash_cracker.brute_force(
                hash_value, hash_type,
                min_len=kwargs.get('min_len', 1),
                max_len=kwargs.get('max_len', 6)
            )
        
        return None
    
    def encode(self, data: str, encoding: str) -> str:
        """Encode data"""
        encodings = {
            'base64': self.encoder.base64_encode,
            'hex': self.encoder.hex_encode,
            'rot13': self.encoder.rot13,
        }
        
        func = encodings.get(encoding.lower())
        if func:
            return func(data)
        return ""
    
    def decode(self, data: str, encoding: str) -> str:
        """Decode data"""
        decodings = {
            'base64': self.encoder.base64_decode,
            'hex': self.encoder.hex_decode,
            'rot13': self.encoder.rot13,
        }
        
        func = decodings.get(encoding.lower())
        if func:
            return func(data)
        return ""
    
    def generate_password(self, length: int = 16) -> str:
        """Generate secure password"""
        return self.key_generator.generate_password(length)
    
    def analyze_for_stego(self, filepath: str) -> Dict[str, Any]:
        """Analyze file for steganography"""
        return self.steg_analyzer.detect_hidden_data(filepath)
    
    def hash_string(self, data: str, algorithm: str = "sha256") -> str:
        """Hash a string"""
        algorithms = {
            'md5': hashlib.md5,
            'sha1': hashlib.sha1,
            'sha256': hashlib.sha256,
            'sha512': hashlib.sha512,
        }
        
        func = algorithms.get(algorithm.lower())
        if func:
            return func(data.encode()).hexdigest()
        return ""
