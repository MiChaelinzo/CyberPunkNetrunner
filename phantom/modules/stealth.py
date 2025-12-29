#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHANTOM Stealth Operations Module

Anonymization, evasion techniques, and
operational security capabilities.
"""

import os
import subprocess
import random
import hashlib
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProxyConfig:
    """Proxy configuration"""
    host: str
    port: int
    proxy_type: str = "socks5"
    username: str = ""
    password: str = ""


class TORManager:
    """Manage TOR network connections"""
    
    def __init__(self, control_port: int = 9051, socks_port: int = 9050):
        self.control_port = control_port
        self.socks_port = socks_port
        self.active = False
    
    def start_tor(self) -> bool:
        """Start TOR service"""
        try:
            subprocess.run(['systemctl', 'start', 'tor'], check=True)
            self.active = True
            print("[+] TOR service started")
            return True
        except subprocess.CalledProcessError:
            try:
                subprocess.run(['service', 'tor', 'start'], check=True)
                self.active = True
                return True
            except Exception:
                print("[-] Failed to start TOR service")
                return False
    
    def stop_tor(self) -> bool:
        """Stop TOR service"""
        try:
            subprocess.run(['systemctl', 'stop', 'tor'], check=True)
            self.active = False
            print("[+] TOR service stopped")
            return True
        except Exception:
            return False
    
    def get_new_identity(self) -> bool:
        """Request new TOR circuit"""
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('127.0.0.1', self.control_port))
            s.send(b'AUTHENTICATE ""\r\nSIGNAL NEWNYM\r\nQUIT\r\n')
            response = s.recv(1024)
            s.close()
            print("[+] New TOR identity requested")
            return True
        except Exception as e:
            print(f"[-] Failed to get new identity: {e}")
            return False
    
    def get_exit_ip(self) -> str:
        """Get current exit node IP"""
        try:
            import requests
            proxies = {
                'http': f'socks5://127.0.0.1:{self.socks_port}',
                'https': f'socks5://127.0.0.1:{self.socks_port}'
            }
            response = requests.get('https://check.torproject.org/api/ip', proxies=proxies, timeout=10)
            return response.json().get('IP', 'Unknown')
        except Exception:
            return "Unable to determine"


class MACSpoofer:
    """MAC address manipulation"""
    
    def __init__(self, interface: str = "eth0"):
        self.interface = interface
        self.original_mac = self._get_current_mac()
    
    def _get_current_mac(self) -> str:
        """Get current MAC address"""
        try:
            with open(f'/sys/class/net/{self.interface}/address', 'r') as f:
                return f.read().strip()
        except Exception:
            return ""
    
    def _generate_random_mac(self) -> str:
        """Generate random MAC address"""
        mac = [random.randint(0x00, 0xff) for _ in range(6)]
        mac[0] = (mac[0] & 0xfe) | 0x02  # Set locally administered bit
        return ':'.join(f'{octet:02x}' for octet in mac)
    
    def spoof_mac(self, new_mac: Optional[str] = None) -> bool:
        """Change MAC address"""
        new_mac = new_mac or self._generate_random_mac()
        
        try:
            # Bring interface down
            subprocess.run(['ip', 'link', 'set', self.interface, 'down'], check=True)
            
            # Change MAC
            subprocess.run(['ip', 'link', 'set', self.interface, 'address', new_mac], check=True)
            
            # Bring interface up
            subprocess.run(['ip', 'link', 'set', self.interface, 'up'], check=True)
            
            print(f"[+] MAC changed to: {new_mac}")
            return True
            
        except Exception as e:
            print(f"[-] Failed to change MAC: {e}")
            return False
    
    def restore_mac(self) -> bool:
        """Restore original MAC address"""
        if self.original_mac:
            return self.spoof_mac(self.original_mac)
        return False


class ProxyChain:
    """Proxy chain management"""
    
    def __init__(self):
        self.proxies: List[ProxyConfig] = []
        self.config_path = "/etc/proxychains.conf"
    
    def add_proxy(self, host: str, port: int, proxy_type: str = "socks5"):
        """Add proxy to chain"""
        proxy = ProxyConfig(host=host, port=port, proxy_type=proxy_type)
        self.proxies.append(proxy)
    
    def clear_chain(self):
        """Clear all proxies from chain"""
        self.proxies = []
    
    def generate_config(self) -> str:
        """Generate proxychains configuration"""
        config = """# ProxyChains Configuration - Generated by PHANTOM
strict_chain
proxy_dns
remote_dns_subnet 224
tcp_read_time_out 15000
tcp_connect_time_out 8000

[ProxyList]
"""
        for proxy in self.proxies:
            config += f"{proxy.proxy_type} {proxy.host} {proxy.port}"
            if proxy.username:
                config += f" {proxy.username} {proxy.password}"
            config += "\n"
        
        return config
    
    def apply_config(self) -> bool:
        """Apply configuration"""
        try:
            config = self.generate_config()
            with open(self.config_path, 'w') as f:
                f.write(config)
            print("[+] Proxy chain configuration applied")
            return True
        except Exception as e:
            print(f"[-] Failed to apply config: {e}")
            return False


class LogCleaner:
    """System log manipulation for anti-forensics"""
    
    LOG_PATHS = [
        '/var/log/auth.log',
        '/var/log/syslog',
        '/var/log/messages',
        '/var/log/secure',
        '/var/log/wtmp',
        '/var/log/btmp',
        '/var/log/lastlog',
        '~/.bash_history',
        '~/.zsh_history',
    ]
    
    def list_logs(self) -> List[str]:
        """List available log files"""
        existing_logs = []
        for log_path in self.LOG_PATHS:
            path = os.path.expanduser(log_path)
            if os.path.exists(path):
                existing_logs.append(path)
        return existing_logs
    
    def clear_history(self) -> bool:
        """Clear shell history"""
        try:
            history_files = [
                os.path.expanduser('~/.bash_history'),
                os.path.expanduser('~/.zsh_history'),
            ]
            
            for hist_file in history_files:
                if os.path.exists(hist_file):
                    open(hist_file, 'w').close()
            
            # Clear in-memory history
            os.system('history -c 2>/dev/null')
            print("[+] Shell history cleared")
            return True
        except Exception as e:
            print(f"[-] Failed to clear history: {e}")
            return False
    
    def shred_file(self, filepath: str, passes: int = 3) -> bool:
        """Securely delete a file"""
        try:
            subprocess.run(['shred', '-vfzu', '-n', str(passes), filepath], check=True)
            print(f"[+] File shredded: {filepath}")
            return True
        except Exception as e:
            print(f"[-] Failed to shred file: {e}")
            return False


class StealthOperations:
    """
    Master Stealth Operations Module
    
    Provides:
    - TOR integration
    - MAC spoofing
    - Proxy chaining
    - Log cleaning
    - Anti-forensics
    """
    
    def __init__(self):
        self.tor_manager = TORManager()
        self.mac_spoofer = MACSpoofer()
        self.proxy_chain = ProxyChain()
        self.log_cleaner = LogCleaner()
    
    def enable_anonymity(self) -> bool:
        """Enable full anonymity mode"""
        print("[*] Enabling anonymity mode...")
        
        # Start TOR
        tor_ok = self.tor_manager.start_tor()
        
        # Spoof MAC
        mac_ok = self.mac_spoofer.spoof_mac()
        
        # Clear history
        self.log_cleaner.clear_history()
        
        if tor_ok and mac_ok:
            print("[+] Anonymity mode enabled")
            return True
        
        print("[-] Partial anonymity mode")
        return False
    
    def disable_anonymity(self) -> bool:
        """Disable anonymity mode and restore settings"""
        print("[*] Disabling anonymity mode...")
        
        self.tor_manager.stop_tor()
        self.mac_spoofer.restore_mac()
        
        print("[+] Anonymity mode disabled")
        return True
    
    def get_current_ip(self) -> str:
        """Get current public IP"""
        try:
            import requests
            response = requests.get('https://api.ipify.org?format=json', timeout=5)
            return response.json().get('ip', 'Unknown')
        except Exception:
            return "Unable to determine"
    
    def check_anonymity_status(self) -> Dict[str, Any]:
        """Check current anonymity status"""
        return {
            'tor_active': self.tor_manager.active,
            'current_ip': self.get_current_ip(),
            'tor_exit_ip': self.tor_manager.get_exit_ip() if self.tor_manager.active else None,
            'current_mac': self.mac_spoofer._get_current_mac(),
            'original_mac': self.mac_spoofer.original_mac,
            'proxy_count': len(self.proxy_chain.proxies)
        }
