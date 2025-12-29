#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHANTOM Network Analyzer Module

Real-time network traffic analysis, packet inspection,
and network mapping capabilities.
"""

import os
import socket
import struct
import threading
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
from datetime import datetime
import subprocess


@dataclass
class PacketInfo:
    """Container for packet information"""
    timestamp: str
    src_ip: str
    dst_ip: str
    protocol: str
    length: int
    data: bytes = field(default=b'', repr=False)


@dataclass
class HostInfo:
    """Container for discovered host information"""
    ip: str
    mac: str = ""
    hostname: str = ""
    os_fingerprint: str = ""
    open_ports: List[int] = field(default_factory=list)
    services: Dict[int, str] = field(default_factory=dict)
    last_seen: str = ""


class ARPScanner:
    """ARP-based network scanner"""
    
    def scan_network(self, network: str = "192.168.1.0/24") -> List[HostInfo]:
        """Scan network for live hosts using ARP"""
        hosts = []
        
        try:
            # Use arp-scan if available
            result = subprocess.run(
                ['arp-scan', network],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            for line in result.stdout.split('\n'):
                if '\t' in line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        hosts.append(HostInfo(
                            ip=parts[0].strip(),
                            mac=parts[1].strip() if len(parts) > 1 else "",
                            last_seen=datetime.now().isoformat()
                        ))
        except Exception:
            # Fallback to ping sweep
            hosts = self._ping_sweep(network)
        
        return hosts
    
    def _ping_sweep(self, network: str) -> List[HostInfo]:
        """Fallback ping sweep"""
        hosts = []
        base_ip = '.'.join(network.split('.')[:-1])
        
        for i in range(1, 255):
            ip = f"{base_ip}.{i}"
            try:
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', '1', ip],
                    capture_output=True,
                    timeout=2
                )
                if result.returncode == 0:
                    hosts.append(HostInfo(
                        ip=ip,
                        last_seen=datetime.now().isoformat()
                    ))
            except Exception:
                continue
        
        return hosts


class TrafficAnalyzer:
    """Network traffic analysis engine"""
    
    PROTOCOLS = {
        1: 'ICMP',
        6: 'TCP',
        17: 'UDP',
    }
    
    def __init__(self):
        self.packets: List[PacketInfo] = []
        self.stats: Dict[str, int] = defaultdict(int)
        self.running = False
        self._lock = threading.Lock()
    
    def parse_ip_header(self, data: bytes) -> Tuple[str, str, int]:
        """Parse IP header from raw packet"""
        version_ihl = data[0]
        ihl = (version_ihl & 0xF) * 4
        protocol = data[9]
        
        src_ip = socket.inet_ntoa(data[12:16])
        dst_ip = socket.inet_ntoa(data[16:20])
        
        return src_ip, dst_ip, protocol
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get traffic statistics"""
        with self._lock:
            return {
                'total_packets': len(self.packets),
                'protocol_distribution': dict(self.stats),
                'unique_sources': len(set(p.src_ip for p in self.packets)),
                'unique_destinations': len(set(p.dst_ip for p in self.packets)),
            }


class BandwidthMonitor:
    """Network bandwidth monitoring"""
    
    def __init__(self, interface: str = "eth0"):
        self.interface = interface
        self.history: List[Dict[str, Any]] = []
    
    def get_current_bandwidth(self) -> Dict[str, int]:
        """Get current bandwidth usage"""
        try:
            with open(f'/sys/class/net/{self.interface}/statistics/rx_bytes', 'r') as f:
                rx_bytes = int(f.read().strip())
            with open(f'/sys/class/net/{self.interface}/statistics/tx_bytes', 'r') as f:
                tx_bytes = int(f.read().strip())
            
            return {
                'rx_bytes': rx_bytes,
                'tx_bytes': tx_bytes,
                'timestamp': datetime.now().isoformat()
            }
        except Exception:
            return {'rx_bytes': 0, 'tx_bytes': 0, 'error': 'Could not read interface stats'}
    
    def get_interface_list(self) -> List[str]:
        """Get list of network interfaces"""
        try:
            interfaces = os.listdir('/sys/class/net/')
            return [iface for iface in interfaces if iface != 'lo']
        except Exception:
            return []


class RouteTracer:
    """Trace route to target"""
    
    def trace(self, target: str, max_hops: int = 30) -> List[Dict[str, Any]]:
        """Trace route to target"""
        hops = []
        
        try:
            result = subprocess.run(
                ['traceroute', '-n', '-m', str(max_hops), target],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            for line in result.stdout.split('\n')[1:]:
                parts = line.split()
                if parts:
                    hop_num = parts[0] if parts[0].isdigit() else None
                    if hop_num:
                        hops.append({
                            'hop': int(hop_num),
                            'data': ' '.join(parts[1:])
                        })
        except Exception as e:
            hops.append({'error': str(e)})
        
        return hops


class NetworkMapper:
    """Network topology mapping"""
    
    def __init__(self):
        self.arp_scanner = ARPScanner()
        self.route_tracer = RouteTracer()
    
    def map_local_network(self, network: str = "192.168.1.0/24") -> Dict[str, Any]:
        """Map local network topology"""
        print(f"[*] Mapping network: {network}")
        
        hosts = self.arp_scanner.scan_network(network)
        
        return {
            'network': network,
            'discovered_hosts': len(hosts),
            'hosts': [vars(h) for h in hosts],
            'scan_time': datetime.now().isoformat()
        }
    
    def trace_to_target(self, target: str) -> Dict[str, Any]:
        """Trace route to remote target"""
        print(f"[*] Tracing route to: {target}")
        
        hops = self.route_tracer.trace(target)
        
        return {
            'target': target,
            'hops': hops,
            'total_hops': len(hops),
            'trace_time': datetime.now().isoformat()
        }


class NetworkAnalyzer:
    """
    Master Network Analysis Module
    
    Provides comprehensive network analysis including:
    - Host discovery
    - Traffic analysis
    - Bandwidth monitoring
    - Route tracing
    - Network mapping
    """
    
    def __init__(self):
        self.mapper = NetworkMapper()
        self.traffic_analyzer = TrafficAnalyzer()
        self.bandwidth_monitor = BandwidthMonitor()
    
    def discover_hosts(self, network: str = "192.168.1.0/24") -> List[HostInfo]:
        """Discover hosts on network"""
        return self.mapper.arp_scanner.scan_network(network)
    
    def get_network_map(self, network: str = "192.168.1.0/24") -> Dict[str, Any]:
        """Get complete network map"""
        return self.mapper.map_local_network(network)
    
    def trace_route(self, target: str) -> Dict[str, Any]:
        """Trace route to target"""
        return self.mapper.trace_to_target(target)
    
    def get_bandwidth_stats(self, interface: str = "eth0") -> Dict[str, Any]:
        """Get bandwidth statistics"""
        self.bandwidth_monitor.interface = interface
        return self.bandwidth_monitor.get_current_bandwidth()
    
    def get_interfaces(self) -> List[str]:
        """Get available network interfaces"""
        return self.bandwidth_monitor.get_interface_list()
    
    def get_traffic_stats(self) -> Dict[str, Any]:
        """Get traffic statistics"""
        return self.traffic_analyzer.get_statistics()
