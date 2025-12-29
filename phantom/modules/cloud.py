#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHANTOM Cloud Security Scanner Module

Cloud infrastructure security assessment for
AWS, Azure, GCP, and container environments.
"""

import os
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


@dataclass
class CloudResource:
    """Cloud resource container"""
    provider: str
    resource_type: str
    identifier: str
    region: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    vulnerabilities: List[str] = field(default_factory=list)


@dataclass
class CloudScanResult:
    """Cloud scan result container"""
    provider: str
    scan_type: str
    resources: List[CloudResource] = field(default_factory=list)
    findings: List[Dict[str, Any]] = field(default_factory=list)
    scan_time: str = field(default_factory=lambda: datetime.now().isoformat())


class S3BucketScanner:
    """AWS S3 bucket enumeration and security checking"""
    
    COMMON_BUCKET_FORMATS = [
        "{name}",
        "{name}-backup",
        "{name}-backups",
        "{name}-dev",
        "{name}-development",
        "{name}-prod",
        "{name}-production",
        "{name}-stage",
        "{name}-staging",
        "{name}-test",
        "{name}-data",
        "{name}-files",
        "{name}-logs",
        "{name}-uploads",
        "{name}-assets",
        "{name}-static",
        "{name}-media",
        "{name}-public",
        "{name}-private",
        "{name}-internal",
        "backup-{name}",
        "dev-{name}",
        "prod-{name}",
        "staging-{name}",
    ]
    
    def __init__(self):
        self.found_buckets: List[CloudResource] = []
    
    def enumerate_buckets(self, company_name: str) -> List[CloudResource]:
        """Enumerate S3 buckets based on company name"""
        if not REQUESTS_AVAILABLE:
            return []
        
        found = []
        
        for format_str in self.COMMON_BUCKET_FORMATS:
            bucket_name = format_str.format(name=company_name.lower().replace(' ', '-'))
            
            if self._check_bucket_exists(bucket_name):
                resource = CloudResource(
                    provider="aws",
                    resource_type="s3_bucket",
                    identifier=bucket_name,
                    metadata={'url': f"https://{bucket_name}.s3.amazonaws.com"}
                )
                
                # Check permissions
                permissions = self._check_bucket_permissions(bucket_name)
                if permissions.get('public_read'):
                    resource.vulnerabilities.append("Public read access enabled")
                if permissions.get('public_write'):
                    resource.vulnerabilities.append("Public write access enabled")
                
                found.append(resource)
        
        self.found_buckets = found
        return found
    
    def _check_bucket_exists(self, bucket_name: str) -> bool:
        """Check if S3 bucket exists"""
        try:
            response = requests.head(
                f"https://{bucket_name}.s3.amazonaws.com",
                timeout=5
            )
            return response.status_code != 404
        except Exception:
            return False
    
    def _check_bucket_permissions(self, bucket_name: str) -> Dict[str, bool]:
        """Check bucket permissions"""
        permissions = {'public_read': False, 'public_write': False}
        
        try:
            # Check read access
            response = requests.get(
                f"https://{bucket_name}.s3.amazonaws.com",
                timeout=5
            )
            if response.status_code == 200 and '<?xml' in response.text:
                permissions['public_read'] = True
            
            # Check write access (don't actually write)
            # This is a passive check only
            
        except Exception:
            pass
        
        return permissions


class AWSScanner:
    """AWS security scanner"""
    
    def __init__(self):
        self.s3_scanner = S3BucketScanner()
    
    def enumerate_s3(self, company_name: str) -> CloudScanResult:
        """Enumerate S3 buckets"""
        buckets = self.s3_scanner.enumerate_buckets(company_name)
        
        findings = []
        for bucket in buckets:
            if bucket.vulnerabilities:
                findings.append({
                    'resource': bucket.identifier,
                    'issues': bucket.vulnerabilities,
                    'severity': 'HIGH' if 'write' in str(bucket.vulnerabilities) else 'MEDIUM'
                })
        
        return CloudScanResult(
            provider="aws",
            scan_type="s3_enumeration",
            resources=buckets,
            findings=findings
        )
    
    def check_metadata_service(self, target_url: str) -> Dict[str, Any]:
        """Check for exposed metadata service"""
        if not REQUESTS_AVAILABLE:
            return {'error': 'requests not available'}
        
        metadata_endpoints = [
            "http://169.254.169.254/latest/meta-data/",
            "http://169.254.169.254/latest/user-data/",
            "http://169.254.169.254/latest/dynamic/instance-identity/document"
        ]
        
        results = {'exposed': False, 'data': []}
        
        for endpoint in metadata_endpoints:
            try:
                # Try SSRF via target
                ssrf_url = f"{target_url}?url={endpoint}"
                response = requests.get(ssrf_url, timeout=5)
                
                if response.status_code == 200 and len(response.text) > 10:
                    results['exposed'] = True
                    results['data'].append({
                        'endpoint': endpoint,
                        'data_preview': response.text[:200]
                    })
            except Exception:
                continue
        
        return results


class AzureScanner:
    """Azure security scanner"""
    
    BLOB_SUFFIXES = [
        '.blob.core.windows.net',
        '.file.core.windows.net',
        '.queue.core.windows.net',
        '.table.core.windows.net'
    ]
    
    def enumerate_storage(self, company_name: str) -> CloudScanResult:
        """Enumerate Azure storage accounts"""
        if not REQUESTS_AVAILABLE:
            return CloudScanResult(provider="azure", scan_type="storage_enum")
        
        resources = []
        findings = []
        
        storage_names = [
            company_name.lower().replace(' ', ''),
            f"{company_name.lower().replace(' ', '')}storage",
            f"{company_name.lower().replace(' ', '')}blob",
            f"{company_name.lower().replace(' ', '')}files",
        ]
        
        for name in storage_names:
            for suffix in self.BLOB_SUFFIXES:
                url = f"https://{name}{suffix}"
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code != 404:
                        resource = CloudResource(
                            provider="azure",
                            resource_type="storage_account",
                            identifier=name,
                            metadata={'url': url, 'type': suffix}
                        )
                        
                        if response.status_code == 200:
                            resource.vulnerabilities.append("Potentially public access")
                            findings.append({
                                'resource': name,
                                'issues': ['Public access possible'],
                                'severity': 'MEDIUM'
                            })
                        
                        resources.append(resource)
                except Exception:
                    continue
        
        return CloudScanResult(
            provider="azure",
            scan_type="storage_enum",
            resources=resources,
            findings=findings
        )


class GCPScanner:
    """Google Cloud Platform security scanner"""
    
    def enumerate_storage(self, project_name: str) -> CloudScanResult:
        """Enumerate GCP storage buckets"""
        if not REQUESTS_AVAILABLE:
            return CloudScanResult(provider="gcp", scan_type="storage_enum")
        
        resources = []
        bucket_patterns = [
            project_name.lower().replace(' ', '-'),
            f"{project_name.lower().replace(' ', '-')}-backup",
            f"{project_name.lower().replace(' ', '-')}-data",
            f"{project_name.lower().replace(' ', '-')}-logs",
        ]
        
        for bucket_name in bucket_patterns:
            url = f"https://storage.googleapis.com/{bucket_name}"
            try:
                response = requests.get(url, timeout=5)
                if response.status_code != 404:
                    resource = CloudResource(
                        provider="gcp",
                        resource_type="storage_bucket",
                        identifier=bucket_name,
                        metadata={'url': url}
                    )
                    
                    if response.status_code == 200:
                        resource.vulnerabilities.append("Public read access")
                    
                    resources.append(resource)
            except Exception:
                continue
        
        return CloudScanResult(
            provider="gcp",
            scan_type="storage_enum",
            resources=resources
        )


class ContainerScanner:
    """Container security scanner"""
    
    def scan_docker_registry(self, registry_url: str) -> Dict[str, Any]:
        """Scan Docker registry for public images"""
        if not REQUESTS_AVAILABLE:
            return {'error': 'requests not available'}
        
        results = {
            'registry': registry_url,
            'accessible': False,
            'repositories': []
        }
        
        try:
            # Check catalog endpoint
            response = requests.get(f"{registry_url}/v2/_catalog", timeout=10)
            
            if response.status_code == 200:
                results['accessible'] = True
                data = response.json()
                results['repositories'] = data.get('repositories', [])
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def check_kubernetes_api(self, api_url: str) -> Dict[str, Any]:
        """Check for exposed Kubernetes API"""
        if not REQUESTS_AVAILABLE:
            return {'error': 'requests not available'}
        
        results = {
            'api_url': api_url,
            'exposed': False,
            'endpoints': []
        }
        
        endpoints = [
            '/api/v1/namespaces',
            '/api/v1/pods',
            '/api/v1/secrets',
            '/apis/apps/v1/deployments',
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{api_url}{endpoint}", timeout=5, verify=False)
                if response.status_code == 200:
                    results['exposed'] = True
                    results['endpoints'].append({
                        'path': endpoint,
                        'accessible': True
                    })
            except Exception:
                continue
        
        return results


class CloudSecurityScanner:
    """
    Master Cloud Security Scanner Module
    
    Provides:
    - AWS security scanning (S3, metadata)
    - Azure storage enumeration
    - GCP bucket discovery
    - Container registry scanning
    - Kubernetes API checking
    """
    
    def __init__(self):
        self.aws_scanner = AWSScanner()
        self.azure_scanner = AzureScanner()
        self.gcp_scanner = GCPScanner()
        self.container_scanner = ContainerScanner()
    
    def full_cloud_scan(self, company_name: str) -> Dict[str, CloudScanResult]:
        """Run full cloud security scan"""
        results = {}
        
        print(f"[*] Starting cloud security scan for: {company_name}")
        
        # AWS
        print("[*] Scanning AWS resources...")
        results['aws'] = self.aws_scanner.enumerate_s3(company_name)
        
        # Azure
        print("[*] Scanning Azure resources...")
        results['azure'] = self.azure_scanner.enumerate_storage(company_name)
        
        # GCP
        print("[*] Scanning GCP resources...")
        results['gcp'] = self.gcp_scanner.enumerate_storage(company_name)
        
        return results
    
    def scan_aws(self, company_name: str) -> CloudScanResult:
        """Scan AWS resources"""
        return self.aws_scanner.enumerate_s3(company_name)
    
    def scan_azure(self, company_name: str) -> CloudScanResult:
        """Scan Azure resources"""
        return self.azure_scanner.enumerate_storage(company_name)
    
    def scan_gcp(self, company_name: str) -> CloudScanResult:
        """Scan GCP resources"""
        return self.gcp_scanner.enumerate_storage(company_name)
    
    def scan_registry(self, registry_url: str) -> Dict[str, Any]:
        """Scan Docker registry"""
        return self.container_scanner.scan_docker_registry(registry_url)
    
    def check_k8s_api(self, api_url: str) -> Dict[str, Any]:
        """Check Kubernetes API exposure"""
        return self.container_scanner.check_kubernetes_api(api_url)
