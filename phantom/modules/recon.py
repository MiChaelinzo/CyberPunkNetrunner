#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHANTOM Reconnaissance Module

Advanced information gathering with neural network
powered analysis and multi-source intelligence.
"""

import os
import socket
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
from abc import ABC, abstractmethod

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


@dataclass
class ReconResult:
    """Container for reconnaissance results"""
    target: str
    scan_type: str
    timestamp: str
    data: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error: str = ""


class BaseScanner(ABC):
    """Abstract base class for scanners"""
    
    @abstractmethod
    def scan(self, target: str) -> ReconResult:
        """Execute scan on target"""
        pass


class PortScanner(BaseScanner):
    """Fast multi-threaded port scanner"""
    
    COMMON_PORTS = [
        21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445,
        993, 995, 1723, 3306, 3389, 5900, 8080, 8443, 8888, 9090
    ]
    
    def __init__(self, timeout: float = 1.0, threads: int = 50):
        self.timeout = timeout
        self.threads = threads
    
    def scan(self, target: str, ports: Optional[List[int]] = None) -> ReconResult:
        """Scan target for open ports"""
        from datetime import datetime
        
        ports = ports or self.COMMON_PORTS
        open_ports = []
        
        def check_port(port: int) -> Optional[int]:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.timeout)
                result = sock.connect_ex((target, port))
                sock.close()
                return port if result == 0 else None
            except Exception:
                return None
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(check_port, port): port for port in ports}
            for future in as_completed(futures):
                result = future.result()
                if result:
                    open_ports.append(result)
        
        return ReconResult(
            target=target,
            scan_type="port_scan",
            timestamp=datetime.now().isoformat(),
            data={
                "open_ports": sorted(open_ports),
                "total_scanned": len(ports),
                "total_open": len(open_ports)
            }
        )


class DNSEnumerator(BaseScanner):
    """DNS enumeration and zone transfer attempts"""
    
    RECORD_TYPES = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA', 'CNAME']
    
    def scan(self, target: str) -> ReconResult:
        """Enumerate DNS records"""
        from datetime import datetime
        import subprocess
        
        results = {}
        
        for record_type in self.RECORD_TYPES:
            try:
                output = subprocess.run(
                    ['nslookup', '-type=' + record_type, target],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                results[record_type] = output.stdout
            except Exception as e:
                results[record_type] = str(e)
        
        return ReconResult(
            target=target,
            scan_type="dns_enum",
            timestamp=datetime.now().isoformat(),
            data={"records": results}
        )


class SubdomainFinder(BaseScanner):
    """Subdomain enumeration using multiple techniques"""
    
    DEFAULT_WORDLIST = [
        'www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp', 'pop',
        'ns1', 'ns2', 'dns', 'dns1', 'dns2', 'mx', 'mx1', 'mx2',
        'blog', 'dev', 'stage', 'staging', 'test', 'testing', 'api',
        'cdn', 'static', 'assets', 'img', 'images', 'js', 'css',
        'admin', 'administrator', 'cpanel', 'webadmin', 'portal',
        'vpn', 'remote', 'gateway', 'proxy', 'secure', 'ssl',
        'db', 'database', 'mysql', 'postgres', 'redis', 'mongo',
        'app', 'apps', 'mobile', 'm', 'beta', 'alpha', 'demo',
        'shop', 'store', 'cart', 'checkout', 'pay', 'payment',
        'support', 'help', 'docs', 'documentation', 'wiki', 'forum'
    ]
    
    def __init__(self, timeout: float = 2.0, threads: int = 20):
        self.timeout = timeout
        self.threads = threads
    
    def scan(self, target: str, wordlist: Optional[List[str]] = None) -> ReconResult:
        """Find subdomains for target domain"""
        from datetime import datetime
        
        wordlist = wordlist or self.DEFAULT_WORDLIST
        found_subdomains = []
        
        def check_subdomain(sub: str) -> Optional[str]:
            subdomain = f"{sub}.{target}"
            try:
                socket.gethostbyname(subdomain)
                return subdomain
            except Exception:
                return None
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(check_subdomain, sub): sub for sub in wordlist}
            for future in as_completed(futures):
                result = future.result()
                if result:
                    found_subdomains.append(result)
        
        return ReconResult(
            target=target,
            scan_type="subdomain_enum",
            timestamp=datetime.now().isoformat(),
            data={
                "subdomains": sorted(found_subdomains),
                "wordlist_size": len(wordlist),
                "found_count": len(found_subdomains)
            }
        )


class TechFingerprint(BaseScanner):
    """Web technology fingerprinting"""
    
    TECH_SIGNATURES = {
        'WordPress': ['/wp-content/', '/wp-includes/', 'wp-json'],
        'Drupal': ['/sites/default/', 'Drupal.settings'],
        'Joomla': ['/components/', '/modules/', 'com_content'],
        'Django': ['csrfmiddlewaretoken', '__admin__'],
        'Flask': ['Werkzeug'],
        'Express': ['X-Powered-By: Express'],
        'Rails': ['X-Runtime', 'csrf-token'],
        'Laravel': ['laravel_session', 'XSRF-TOKEN'],
        'ASP.NET': ['__VIEWSTATE', 'ASP.NET'],
        'React': ['react', '_reactRoot'],
        'Angular': ['ng-version', 'ng-app'],
        'Vue.js': ['vue', 'v-cloak'],
    }
    
    def scan(self, target: str) -> ReconResult:
        """Fingerprint web technologies"""
        from datetime import datetime
        
        if not REQUESTS_AVAILABLE:
            return ReconResult(
                target=target,
                scan_type="tech_fingerprint",
                timestamp=datetime.now().isoformat(),
                success=False,
                error="requests library not installed"
            )
        
        detected = []
        headers_info = {}
        
        try:
            url = target if target.startswith('http') else f'http://{target}'
            response = requests.get(url, timeout=10, allow_redirects=True)
            
            headers_info = dict(response.headers)
            content = response.text.lower()
            
            # Check signatures
            for tech, signatures in self.TECH_SIGNATURES.items():
                for sig in signatures:
                    if sig.lower() in content or sig.lower() in str(headers_info).lower():
                        if tech not in detected:
                            detected.append(tech)
                        break
            
            # Check server header
            server = headers_info.get('Server', '')
            if server:
                detected.append(f"Server: {server}")
            
        except Exception as e:
            return ReconResult(
                target=target,
                scan_type="tech_fingerprint",
                timestamp=datetime.now().isoformat(),
                success=False,
                error=str(e)
            )
        
        return ReconResult(
            target=target,
            scan_type="tech_fingerprint",
            timestamp=datetime.now().isoformat(),
            data={
                "technologies": detected,
                "headers": headers_info
            }
        )


class OSINTGatherer(BaseScanner):
    """Open Source Intelligence gathering"""
    
    def scan(self, target: str) -> ReconResult:
        """Gather OSINT data"""
        from datetime import datetime
        
        results = {
            "whois": self._get_whois(target),
            "ip_info": self._get_ip_info(target),
        }
        
        return ReconResult(
            target=target,
            scan_type="osint",
            timestamp=datetime.now().isoformat(),
            data=results
        )
    
    def _get_whois(self, target: str) -> Dict[str, Any]:
        """Get WHOIS information"""
        import subprocess
        try:
            result = subprocess.run(
                ['whois', target],
                capture_output=True,
                text=True,
                timeout=10
            )
            return {"raw": result.stdout}
        except Exception as e:
            return {"error": str(e)}
    
    def _get_ip_info(self, target: str) -> Dict[str, Any]:
        """Get IP geolocation info"""
        try:
            ip = socket.gethostbyname(target)
            return {"ip": ip}
        except Exception as e:
            return {"error": str(e)}


class ReconnaissanceModule:
    """
    Master Reconnaissance Module
    
    Orchestrates all recon scanners and provides
    unified interface for intelligence gathering.
    """
    
    def __init__(self):
        self.port_scanner = PortScanner()
        self.dns_enum = DNSEnumerator()
        self.subdomain_finder = SubdomainFinder()
        self.tech_fingerprint = TechFingerprint()
        self.osint = OSINTGatherer()
        self.results: List[ReconResult] = []
    
    def full_scan(self, target: str) -> Dict[str, ReconResult]:
        """Execute full reconnaissance scan"""
        results = {}
        
        print(f"\n[*] Starting full reconnaissance on {target}")
        
        # Port scan
        print("[*] Running port scan...")
        results['ports'] = self.port_scanner.scan(target)
        
        # DNS enumeration
        print("[*] Enumerating DNS records...")
        results['dns'] = self.dns_enum.scan(target)
        
        # Subdomain discovery
        print("[*] Finding subdomains...")
        results['subdomains'] = self.subdomain_finder.scan(target)
        
        # Technology fingerprinting
        print("[*] Fingerprinting technologies...")
        results['tech'] = self.tech_fingerprint.scan(target)
        
        # OSINT
        print("[*] Gathering OSINT...")
        results['osint'] = self.osint.scan(target)
        
        self.results.extend(results.values())
        return results
    
    def quick_scan(self, target: str) -> Dict[str, ReconResult]:
        """Execute quick reconnaissance scan"""
        results = {}
        
        print(f"\n[*] Starting quick scan on {target}")
        
        results['ports'] = self.port_scanner.scan(target)
        results['tech'] = self.tech_fingerprint.scan(target)
        
        self.results.extend(results.values())
        return results
    
    def export_results(self, format: str = "json") -> str:
        """Export results in specified format"""
        if format == "json":
            return json.dumps(
                [vars(r) for r in self.results],
                indent=2
            )
        return ""
