#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHANTOM Network Utilities

Network-related helper functions and utilities.
"""

import socket
import struct
import subprocess
from typing import Dict, Any, List, Optional, Tuple


class NetworkUtils:
    """Network utility functions"""
    
    @staticmethod
    def get_local_ip() -> str:
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    @staticmethod
    def get_public_ip() -> str:
        """Get public IP address"""
        try:
            import requests
            response = requests.get("https://api.ipify.org?format=json", timeout=5)
            return response.json().get("ip", "Unknown")
        except Exception:
            return "Unknown"
    
    @staticmethod
    def resolve_hostname(hostname: str) -> Optional[str]:
        """Resolve hostname to IP"""
        try:
            return socket.gethostbyname(hostname)
        except Exception:
            return None
    
    @staticmethod
    def reverse_dns(ip: str) -> Optional[str]:
        """Reverse DNS lookup"""
        try:
            return socket.gethostbyaddr(ip)[0]
        except Exception:
            return None
    
    @staticmethod
    def is_valid_ip(ip: str) -> bool:
        """Check if string is valid IP"""
        try:
            socket.inet_aton(ip)
            return True
        except Exception:
            return False
    
    @staticmethod
    def is_port_open(host: str, port: int, timeout: float = 2.0) -> bool:
        """Check if port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    @staticmethod
    def get_mac_address() -> str:
        """Get local MAC address"""
        try:
            import uuid
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                          for elements in range(0, 48, 8)][::-1])
            return mac
        except Exception:
            return "Unknown"
    
    @staticmethod
    def cidr_to_range(cidr: str) -> Tuple[str, str]:
        """Convert CIDR notation to IP range"""
        try:
            import ipaddress
            network = ipaddress.ip_network(cidr, strict=False)
            return str(network.network_address), str(network.broadcast_address)
        except Exception:
            return ("", "")
    
    @staticmethod
    def get_gateway() -> str:
        """Get default gateway"""
        try:
            result = subprocess.run(['ip', 'route', 'show', 'default'],
                                   capture_output=True, text=True)
            parts = result.stdout.split()
            if 'via' in parts:
                return parts[parts.index('via') + 1]
        except Exception:
            pass
        return ""
    
    @staticmethod
    def get_dns_servers() -> List[str]:
        """Get configured DNS servers"""
        servers = []
        try:
            with open('/etc/resolv.conf', 'r') as f:
                for line in f:
                    if line.startswith('nameserver'):
                        servers.append(line.split()[1])
        except Exception:
            pass
        return servers
