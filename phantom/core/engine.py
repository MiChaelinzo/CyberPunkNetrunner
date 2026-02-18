#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  PHANTOM NETRUNNER ENGINE - CYBERDECK CORE v3.0                              ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━║
║  "In the Net, no one hears you breach the ICE." - Night City Netrunner       ║
╚═══════════════════════════════════════════════════════════════════════════════╝

This module serves as the central orchestrator for all PHANTOM operations,
managing quickhack deployment, cyberdeck protocols, and ICE-breaching routines.

Terminology (Cyberpunk 2077):
- ICE (Intrusion Countermeasures Electronics): Security programs
- Daemon: Automated background processes/exploits
- Quickhack: Rapid offensive/defensive cyber attacks
- Cyberdeck: Hardware interface for netrunning
- Subnet: Local network segment
- NetWatch: Corporate net security (the enemy)
- Blackwall: The ultimate barrier (AI containment)
"""

import sys
import os
import signal
import asyncio
import json
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from datetime import datetime
from pathlib import Path

# Rich library for modern TUI
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt, Confirm
    from rich.text import Text
    from rich.live import Live
    from rich.layout import Layout
    from rich import print as rprint
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("[!] Rich library not found. Install with: pip install rich")

# Import PHANTOM modules
from phantom.modules.recon import ReconnaissanceModule
from phantom.modules.network import NetworkAnalyzer
from phantom.modules.web import WebSecurityScanner
from phantom.modules.exploit import ExploitFramework
from phantom.modules.wireless import WirelessModule
from phantom.modules.stealth import StealthOperations
from phantom.modules.social import SocialEngineering
from phantom.modules.forensics import ForensicsModule
from phantom.modules.crypto import CryptoAnalyzer
from phantom.modules.cloud import CloudSecurityScanner


class OperationMode(Enum):
    """PHANTOM Operation Modes - Cyberdeck Configuration"""
    STEALTH = auto()      # Ghost Protocol - Minimal ICE detection
    AGGRESSIVE = auto()   # Berserker Mode - Full daemon deployment
    RECON = auto()        # Ping Protocol - Intelligence gathering
    AUDIT = auto()        # NetWatch Scan - Corporate compliance
    INTERACTIVE = auto()  # Live Jack-In - User-guided operations


@dataclass
class SystemState:
    """Tracks the current state of the Cyberdeck system"""
    initialized: bool = False
    session_active: bool = False
    current_module: Optional[str] = None
    operation_mode: OperationMode = OperationMode.INTERACTIVE
    start_time: datetime = field(default_factory=datetime.now)
    loaded_plugins: List[str] = field(default_factory=list)
    active_tasks: Dict[str, Any] = field(default_factory=dict)
    ram_units: int = 8  # Cyberdeck RAM for quickhacks
    ice_breached: int = 0  # ICE layers compromised


class PhantomEngine:
    """
    Core Cyberdeck Engine for PHANTOM Netrunner Framework
    
    "The Net is vast and infinite." - Ghost in the Shell
    
    Manages all netrunning operations, quickhack deployment, daemon control,
    and ICE-breaching routines through a military-grade cyberdeck interface.
    
    Inspired by Cyberpunk 2077's Netrunning mechanics.
    """
    
    VERSION = "3.0.0"
    CODENAME = "PHANTOM"
    CYBERDECK = "Netwatch Netdriver Mk.5"
    
    # ASCII Art Banner - Cyberpunk 2077 Style
    BANNER = """
\033[38;5;201m╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
║\033[38;5;51m  ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄  \033[38;5;201m║
║\033[38;5;51m  █▓▒░ P H A N T O M   N E T R U N N E R ░▒▓█   ◢◤ CYBERDECK ONLINE ◢◤                            \033[38;5;201m║
║\033[38;5;51m  ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀  \033[38;5;201m║
║                                                                                                          ║
║   \033[38;5;201m██████╗ \033[38;5;198m██╗  ██╗ \033[38;5;51m█████╗ \033[38;5;47m███╗   ██╗\033[38;5;226m████████╗\033[38;5;201m ██████╗ \033[38;5;198m███╗   ███╗\033[0m                                  \033[38;5;201m║
║   \033[38;5;201m██╔══██╗\033[38;5;198m██║  ██║\033[38;5;51m██╔══██╗\033[38;5;47m████╗  ██║\033[38;5;226m╚══██╔══╝\033[38;5;201m██╔═══██╗\033[38;5;198m████╗ ████║\033[0m    \033[38;5;51mN E T R U N N E R\033[0m       \033[38;5;201m║
║   \033[38;5;201m██████╔╝\033[38;5;198m███████║\033[38;5;51m███████║\033[38;5;47m██╔██╗ ██║\033[38;5;226m   ██║   \033[38;5;201m██║   ██║\033[38;5;198m██╔████╔██║\033[0m    \033[38;5;198mv3.0 // NIGHT CITY\033[0m    \033[38;5;201m║
║   \033[38;5;201m██╔═══╝ \033[38;5;198m██╔══██║\033[38;5;51m██╔══██║\033[38;5;47m██║╚██╗██║\033[38;5;226m   ██║   \033[38;5;201m██║   ██║\033[38;5;198m██║╚██╔╝██║\033[0m                           \033[38;5;201m║
║   \033[38;5;201m██║     \033[38;5;198m██║  ██║\033[38;5;51m██║  ██║\033[38;5;47m██║ ╚████║\033[38;5;226m   ██║   \033[38;5;201m╚██████╔╝\033[38;5;198m██║ ╚═╝ ██║\033[0m                           \033[38;5;201m║
║   \033[38;5;201m╚═╝     \033[38;5;198m╚═╝  ╚═╝\033[38;5;51m╚═╝  ╚═╝\033[38;5;47m╚═╝  ╚═══╝\033[38;5;226m   ╚═╝   \033[38;5;201m ╚═════╝ \033[38;5;198m╚═╝     ╚═╝\033[0m                           \033[38;5;201m║
║                                                                                                          ║
║   \033[38;5;226m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[38;5;201m   ║
║   \033[38;5;51m◢ \033[38;5;226mCYBERDECK STATUS\033[38;5;51m ◤\033[0m              \033[38;5;51m◢ \033[38;5;226mQUICKHACKS LOADED\033[38;5;51m ◤\033[0m              \033[38;5;51m◢ \033[38;5;226mICE STATUS\033[38;5;51m ◤\033[0m         \033[38;5;201m║
║   \033[38;5;47m[■] RAM: 8 UNITS AVAILABLE\033[0m        \033[38;5;47m[■] BREACH PROTOCOL v3.0\033[0m           \033[38;5;47m[■] STANDBY\033[0m            \033[38;5;201m║
║   \033[38;5;47m[■] BUFFER: 6 SLOTS\033[0m               \033[38;5;47m[■] DAEMON UPLOAD READY\033[0m            \033[38;5;47m[■] NO TRACE\033[0m           \033[38;5;201m║
║   \033[38;5;47m[■] NEURAL LINK: STABLE\033[0m           \033[38;5;47m[■] PING NETWORK ACTIVE\033[0m            \033[38;5;47m[■] GHOST MODE\033[0m         \033[38;5;201m║
║                                                                                                          ║
║   \033[38;5;196m⚠  NETWATCH ADVISORY: UNAUTHORIZED ACCESS IS A CORPO DEATH SENTENCE  ⚠\033[0m                        \033[38;5;201m║
║   \033[38;5;51m🌐 https://github.com/MiChaelinzo/CyberPunkNetrunner\033[0m   \033[38;5;226m// NIGHT CITY // 2077\033[0m              \033[38;5;201m║
║                                                                                                          ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════╝\033[0m
"""

    # Cyberpunk 2077 themed menu categories with real tool descriptions
    MENU_CATEGORIES = {
        "BREACH_PROTOCOL": {
            "icon": "◢◤",
            "color": "\033[38;5;51m",  # Cyan
            "description": "Reconnaissance & Information Gathering",
            "modules": [
                ("01", "Ping [QUICKHACK]", "Multi-threaded port scanner on target"),
                ("02", "Breach Protocol", "Full web security scan (SQLi/XSS/dirs/headers)"),
                ("03", "Datamine [v1/v2/v3]", "OSINT gathering (WHOIS, IP info)"),
                ("04", "Neural Subnet Mapper", "Network discovery & host mapping"),
                ("05", "ICE Analyzer", "HTTP security header analysis"),
            ]
        },
        "COMBAT_QUICKHACKS": {
            "icon": "⚡",
            "color": "\033[38;5;196m",  # Red
            "description": "Web Application Vulnerability Scanning",
            "modules": [
                ("10", "Short Circuit", "SQL injection vulnerability scanner"),
                ("11", "Synapse Burnout", "Cross-Site Scripting (XSS) scanner"),
                ("12", "Contagion [DAEMON]", "Directory & file enumeration"),
                ("13", "System Collapse", "Comprehensive web vulnerability scan"),
                ("14", "Cyberpsychosis", "Service vulnerability scanner"),
            ]
        },
        "COVERT_QUICKHACKS": {
            "icon": "👻",
            "color": "\033[38;5;213m",  # Pink
            "description": "Stealth & Anonymization Operations",
            "modules": [
                ("20", "Whistle [DISTRACT]", "Check anonymity status (IP, TOR, MAC)"),
                ("21", "Memory Wipe", "MAC address spoofing"),
                ("22", "Reboot Optics", "TOR network management (start/stop/identity)"),
                ("23", "Weapon Glitch", "Proxy chain configuration"),
                ("24", "Cripple Movement", "Log cleaning & anti-forensics"),
            ]
        },
        "CONTROL_QUICKHACKS": {
            "icon": "🎭",
            "color": "\033[38;5;226m",  # Yellow
            "description": "Network Analysis & Monitoring",
            "modules": [
                ("30", "Distract Enemies", "ARP/ping-based host discovery"),
                ("31", "Remote Activation", "Traceroute to remote target"),
                ("32", "Take Control", "Network bandwidth monitoring"),
                ("33", "Detonate Grenade", "List network interfaces"),
                ("34", "Cyberware Malfunction", "Traffic statistics summary"),
            ]
        },
        "DAEMON_UPLOAD": {
            "icon": "🔥",
            "color": "\033[38;5;208m",  # Orange
            "description": "Advanced Reconnaissance Daemons",
            "modules": [
                ("40", "DATAMINE_V1", "DNS record enumeration (A/MX/NS/TXT...)"),
                ("41", "DATAMINE_V2", "Subdomain discovery via wordlist"),
                ("42", "DATAMINE_V3", "Web technology fingerprinting"),
                ("43", "ICEPICK [DAEMON]", "Quick recon (ports + tech fingerprint)"),
                ("44", "MASS VULNERABILITY", "Full recon (ports/DNS/subs/tech/OSINT)"),
            ]
        },
        "ULTIMATE_QUICKHACKS": {
            "icon": "💀",
            "color": "\033[38;5;201m",  # Magenta
            "description": "Cloud Infrastructure Security Scanning",
            "modules": [
                ("50", "Suicide", "AWS S3 bucket enumeration & permissions"),
                ("51", "Detonate [LEGENDARY]", "Azure storage account enumeration"),
                ("52", "System Reset", "GCP storage bucket discovery"),
                ("53", "Blackwall Gateway", "Full cloud scan (AWS/Azure/GCP)"),
                ("54", "JOHNNY'S LEGACY", "Docker registry & Kubernetes API scan"),
            ]
        },
        "ARASAKA_PROTOCOLS": {
            "icon": "🏢",
            "color": "\033[38;5;255m",  # White
            "description": "Social Engineering & Credential Harvesting",
            "modules": [
                ("60", "Phishing Campaign", "Start phishing server with templates"),
                ("61", "Spear Phishing", "List available phishing templates"),
                ("62", "QR Jacking", "Generate QR codes for phishing URLs"),
                ("63", "Social Profiler", "Username OSINT across 12+ platforms"),
                ("64", "Deepfake Generator", "Email breach database search"),
            ]
        },
        "MILITECH_ARSENAL": {
            "icon": "🔫",
            "color": "\033[38;5;124m",  # Dark Red
            "description": "Exploitation & Payload Generation",
            "modules": [
                ("70", "Exploit Framework", "Service vulnerability scanner"),
                ("71", "Payload Forge", "Reverse shell & web shell generator"),
                ("72", "Shell Handler", "Reverse shell listener"),
                ("73", "PrivEsc Suite", "List all available payloads"),
                ("74", "Persistence Daemon", "View active shell sessions"),
            ]
        },
        "BLACKHAND_FORENSICS": {
            "icon": "🔬",
            "color": "\033[38;5;39m",  # Light Blue
            "description": "Digital Forensics & Evidence Analysis",
            "modules": [
                ("80", "RAM Analyzer", "File hash & metadata analysis"),
                ("81", "Braindance Imager", "Forensic disk imaging (dd)"),
                ("82", "File Carver", "Recover files from raw data/images"),
                ("83", "Metadata Stripper", "Extract file metadata & permissions"),
                ("84", "Timeline Reconstructor", "Build forensic timeline from directory"),
            ]
        },
        "RELIC_CRYPTO": {
            "icon": "🔐",
            "color": "\033[38;5;46m",  # Green
            "description": "Cryptographic Analysis & Cracking",
            "modules": [
                ("90", "Hash Annihilator", "Dictionary & brute-force hash cracking"),
                ("91", "Cipher Breaker", "Encode/decode (Base64/Hex/ROT13/XOR)"),
                ("92", "Key Forge", "Secure password & key generation"),
                ("93", "Steganography", "Detect hidden data in files"),
                ("94", "Blockchain Tracker", "Hash type identification"),
            ]
        },
    }

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Cyberdeck Engine - Jack into the Net"""
        self.state = SystemState()
        self.console = Console() if RICH_AVAILABLE else None
        self.config_path = config_path or self._default_config_path()
        self._setup_signal_handlers()
        self._callbacks: Dict[str, List[Callable]] = {}

        # Initialize real PHANTOM modules
        self.recon = ReconnaissanceModule()
        self.network_analyzer = NetworkAnalyzer()
        self.web_scanner = WebSecurityScanner()
        self.exploit_framework = ExploitFramework()
        self.wireless = WirelessModule()
        self.stealth = StealthOperations()
        self.social = SocialEngineering()
        self.forensics = ForensicsModule()
        self.crypto = CryptoAnalyzer()
        self.cloud_scanner = CloudSecurityScanner()

        self._modules: Dict[str, Any] = {
            'recon': self.recon,
            'network': self.network_analyzer,
            'web': self.web_scanner,
            'exploit': self.exploit_framework,
            'wireless': self.wireless,
            'stealth': self.stealth,
            'social': self.social,
            'forensics': self.forensics,
            'crypto': self.crypto,
            'cloud': self.cloud_scanner,
        }
        
    def _default_config_path(self) -> str:
        """Get default Cyberdeck configuration path"""
        return str(Path.home() / ".phantom" / "config.yaml")
    
    def _setup_signal_handlers(self):
        """Setup graceful shutdown handlers"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful jack-out"""
        self.display_message("\n[!] EMERGENCY JACK-OUT INITIATED - Cleaning traces...", "warning")
        self.cleanup()
        sys.exit(0)
    
    def display_banner(self):
        """Display the PHANTOM Cyberdeck boot sequence"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print(self.BANNER)
        
    def display_message(self, message: str, msg_type: str = "info"):
        """Display formatted Netrunner message"""
        colors = {
            "info": "\033[38;5;51m",      # Cyan - standard info
            "success": "\033[38;5;46m",    # Green - breach successful
            "warning": "\033[38;5;226m",   # Yellow - NetWatch alert
            "error": "\033[38;5;196m",     # Red - ICE detected
            "debug": "\033[38;5;244m",     # Gray - system debug
            "quickhack": "\033[38;5;201m"  # Magenta - quickhack loaded
        }
        icons = {
            "info": "◢◤",
            "success": "✓ BREACH",
            "warning": "⚠ ALERT",
            "error": "✗ ICE",
            "debug": "●",
            "quickhack": "⚡"
        }
        color = colors.get(msg_type, "\033[0m")
        icon = icons.get(msg_type, "")
        print(f"{color}[{icon}] {message}\033[0m")
    
    def display_menu(self):
        """Display the Netrunner Quickhack Menu"""
        if RICH_AVAILABLE:
            self._display_rich_menu()
        else:
            self._display_simple_menu()
    
    def _display_rich_menu(self):
        """Display menu using Rich library - Cyberpunk style"""
        table = Table(show_header=True, header_style="bold magenta", border_style="cyan")
        table.add_column("ID", style="cyan", width=4)
        table.add_column("Quickhack", style="green", width=28)
        table.add_column("Effect", style="white", width=48)
        
        for category, data in self.MENU_CATEGORIES.items():
            desc = data.get('description', '')
            table.add_row("", f"{data['icon']} {category.replace('_', ' ')}", desc, style="bold yellow")
            for mod_id, name, desc in data["modules"]:
                table.add_row(mod_id, name, desc)
        
        table.add_row("", "", "")
        table.add_row("99", "⚙️  Cyberdeck Settings", "Configure your neural interface")
        table.add_row("00", "🚪 Jack Out", "Disconnect safely from the Net")
        
        self.console.print(table)
    
    def _display_simple_menu(self):
        """Display Night City Netrunner terminal menu"""
        print("\n\033[38;5;201m╔════════════════════════════════════════════════════════════════════════════════╗")
        print("║       \033[38;5;51m◢◤ PHANTOM NETRUNNER - QUICKHACK COMMAND INTERFACE ◢◤\033[38;5;201m                    ║")
        print("║       \033[38;5;226m      「 NIGHT CITY SUBNET // CYBERDECK ONLINE 」\033[38;5;201m                        ║")
        print("╚════════════════════════════════════════════════════════════════════════════════╝\033[0m\n")
        
        for category, data in self.MENU_CATEGORIES.items():
            desc = data.get('description', '')
            print(f"\n{data['color']}━━━ {data['icon']} {category.replace('_', ' ')} ━━━")
            print(f"    \033[38;5;244m{desc}\033[0m")
            for mod_id, name, desc in data["modules"]:
                print(f"  \033[38;5;51m[{mod_id}]\033[0m {name:<28} \033[38;5;244m- {desc}\033[0m")
        
        print(f"\n\033[38;5;226m━━━ ⚙️  CYBERDECK SYSTEM ━━━\033[0m")
        print(f"  \033[38;5;51m[99]\033[0m Cyberdeck Settings")
        print(f"  \033[38;5;51m[00]\033[0m Jack Out")
        print()
    
    def get_user_input(self, prompt: str = "NETRUNNER") -> str:
        """Get user input with styled Cyberpunk prompt"""
        try:
            return input(f"\033[38;5;201m┌──[\033[38;5;51m{prompt}\033[38;5;201m@\033[38;5;226mNIGHT_CITY\033[38;5;201m]\n└──▶ \033[38;5;47m").strip()
        except EOFError:
            return "00"
    
    def run_module(self, module_id: str):
        """Execute the selected quickhack module"""
        # Find module in categories
        for category, data in self.MENU_CATEGORIES.items():
            for mod_id, name, desc in data["modules"]:
                if mod_id == module_id:
                    self._execute_module(category, mod_id, name)
                    return
        
        self.display_message(f"Unknown quickhack ID: {module_id} - Check your buffer sequence", "error")
    
    def _execute_module(self, category: str, mod_id: str, name: str):
        """Execute a specific quickhack"""
        self.display_message(f"Uploading {name} to cyberdeck buffer...", "quickhack")

        # Quickhack routing to real module implementations
        module_handlers = {
            # BREACH_PROTOCOL - Recon & Network
            "01": self._run_port_scan,
            "02": self._run_web_scan,
            "03": self._run_osint_gather,
            "04": self._run_network_map,
            "05": self._run_header_analysis,
            # COMBAT_QUICKHACKS - Web Attacks
            "10": self._run_sqli_scan,
            "11": self._run_xss_scan,
            "12": self._run_directory_bust,
            "13": self._run_full_web_scan,
            "14": self._run_vuln_scan,
            # COVERT_QUICKHACKS - Stealth Operations
            "20": self._run_anonymity_check,
            "21": self._run_mac_spoof,
            "22": self._run_tor_manager,
            "23": self._run_proxy_chain,
            "24": self._run_log_cleaner,
            # CONTROL_QUICKHACKS - Network Analysis
            "30": self._run_host_discovery,
            "31": self._run_trace_route,
            "32": self._run_bandwidth_monitor,
            "33": self._run_interface_list,
            "34": self._run_traffic_stats,
            # DAEMON_UPLOAD - Recon Daemons
            "40": self._run_dns_enum,
            "41": self._run_subdomain_finder,
            "42": self._run_tech_fingerprint,
            "43": self._run_quick_recon,
            "44": self._run_full_recon,
            # ULTIMATE_QUICKHACKS - Cloud Scanning
            "50": self._run_cloud_aws_scan,
            "51": self._run_cloud_azure_scan,
            "52": self._run_cloud_gcp_scan,
            "53": self._run_cloud_full_scan,
            "54": self._run_container_scan,
            # ARASAKA_PROTOCOLS - Social Engineering
            "60": self._run_phishing_server,
            "61": self._run_phishing_templates,
            "62": self._run_qr_generator,
            "63": self._run_social_profiler,
            "64": self._run_email_search,
            # MILITECH_ARSENAL - Exploitation
            "70": self._run_exploit_vuln_scan,
            "71": self._run_payload_generator,
            "72": self._run_shell_handler,
            "73": self._run_list_payloads,
            "74": self._run_active_sessions,
            # BLACKHAND_FORENSICS - Forensics
            "80": self._run_file_analysis,
            "81": self._run_disk_imager,
            "82": self._run_file_carver,
            "83": self._run_metadata_stripper,
            "84": self._run_timeline_builder,
            # RELIC_CRYPTO - Crypto Analysis
            "90": self._run_hash_cracker,
            "91": self._run_cipher_tools,
            "92": self._run_key_generator,
            "93": self._run_stego_analyzer,
            "94": self._run_hash_identifier,
        }

        handler = module_handlers.get(mod_id, self._module_placeholder)
        handler(name)

    def _module_placeholder(self, name: str):
        """Placeholder for quickhacks under development"""
        self.display_message(f"Quickhack '{name}' is under development.", "warning")
        input("\n\033[38;5;244mPress Enter to continue...\033[0m")

    def _print_results(self, data: Any, title: str = "Results"):
        """Pretty-print scan results"""
        print(f"\n\033[38;5;51m{'='*60}")
        print(f"◢◤ {title}")
        print(f"{'='*60}\033[0m\n")
        if isinstance(data, dict):
            print(json.dumps(data, indent=2, default=str))
        elif isinstance(data, list):
            print(json.dumps(data, indent=2, default=str))
        else:
            print(data)
        input("\n\033[38;5;244mPress Enter to continue...\033[0m")

    def _get_target(self, prompt_text: str = "Enter target (IP/hostname/URL)") -> str:
        """Prompt user for a target"""
        return input(f"\n\033[38;5;51m{prompt_text}: \033[38;5;47m").strip()

    # =========================================================================
    # BREACH_PROTOCOL - Reconnaissance (01-05)
    # =========================================================================

    def _run_port_scan(self, name: str):
        """Port scanning via ReconnaissanceModule"""
        target = self._get_target("Enter target IP or hostname for port scan")
        if not target:
            return
        self.display_message(f"Scanning ports on {target}...", "quickhack")
        result = self.recon.port_scanner.scan(target)
        self._print_results(vars(result), f"Port Scan: {target}")

    def _run_web_scan(self, name: str):
        """Web security scanning via WebSecurityScanner"""
        target = self._get_target("Enter target URL (e.g. http://example.com)")
        if not target:
            return
        self.display_message(f"Running web security scan on {target}...", "quickhack")
        results = self.web_scanner.full_scan(target)
        output = {}
        for key, val in results.items():
            output[key] = vars(val) if hasattr(val, '__dict__') else val
        self._print_results(output, f"Web Security Scan: {target}")

    def _run_osint_gather(self, name: str):
        """OSINT gathering via ReconnaissanceModule"""
        target = self._get_target("Enter target domain for OSINT")
        if not target:
            return
        self.display_message(f"Gathering OSINT on {target}...", "quickhack")
        result = self.recon.osint.scan(target)
        self._print_results(vars(result), f"OSINT: {target}")

    def _run_network_map(self, name: str):
        """Network mapping via NetworkAnalyzer"""
        network = self._get_target("Enter network CIDR (e.g. 192.168.1.0/24)")
        if not network:
            network = "192.168.1.0/24"
        self.display_message(f"Mapping network {network}...", "quickhack")
        result = self.network_analyzer.get_network_map(network)
        self._print_results(result, f"Network Map: {network}")

    def _run_header_analysis(self, name: str):
        """HTTP header analysis via WebSecurityScanner"""
        target = self._get_target("Enter URL for security header analysis")
        if not target:
            return
        self.display_message(f"Analyzing security headers on {target}...", "quickhack")
        result = self.web_scanner.check_headers(target)
        self._print_results(result, f"Security Headers: {target}")

    # =========================================================================
    # COMBAT_QUICKHACKS - Web Vulnerability Scanning (10-14)
    # =========================================================================

    def _run_sqli_scan(self, name: str):
        """SQL injection scanning"""
        target = self._get_target("Enter URL with parameters for SQLi test")
        if not target:
            return
        self.display_message(f"Testing {target} for SQL injection...", "quickhack")
        result = self.web_scanner.scan_sqli(target)
        self._print_results(vars(result), f"SQLi Scan: {target}")

    def _run_xss_scan(self, name: str):
        """XSS scanning"""
        target = self._get_target("Enter URL with parameters for XSS test")
        if not target:
            return
        self.display_message(f"Testing {target} for XSS...", "quickhack")
        result = self.web_scanner.scan_xss(target)
        self._print_results(vars(result), f"XSS Scan: {target}")

    def _run_directory_bust(self, name: str):
        """Directory enumeration"""
        target = self._get_target("Enter base URL for directory enumeration")
        if not target:
            return
        self.display_message(f"Enumerating directories on {target}...", "quickhack")
        result = self.web_scanner.enumerate_directories(target)
        self._print_results(vars(result), f"Directory Scan: {target}")

    def _run_full_web_scan(self, name: str):
        """Full web vulnerability scan"""
        target = self._get_target("Enter URL for full web security scan")
        if not target:
            return
        self.display_message(f"Full web scan on {target}...", "quickhack")
        results = self.web_scanner.full_scan(target)
        output = {}
        for key, val in results.items():
            output[key] = vars(val) if hasattr(val, '__dict__') else val
        self._print_results(output, f"Full Web Scan: {target}")

    def _run_vuln_scan(self, name: str):
        """Vulnerability scanner via ExploitFramework"""
        target = self._get_target("Enter target IP for vulnerability scan")
        if not target:
            return
        self.display_message(f"Scanning {target} for vulnerabilities...", "quickhack")
        result = self.exploit_framework.scan_vulnerabilities(target)
        self._print_results(result, f"Vulnerability Scan: {target}")

    # =========================================================================
    # COVERT_QUICKHACKS - Stealth Operations (20-24)
    # =========================================================================

    def _run_anonymity_check(self, name: str):
        """Check anonymity status"""
        self.display_message("Checking anonymity status...", "quickhack")
        result = self.stealth.check_anonymity_status()
        self._print_results(result, "Anonymity Status")

    def _run_mac_spoof(self, name: str):
        """MAC address spoofing"""
        print("\n\033[38;5;51m  [1] Spoof MAC (random)")
        print("  [2] Spoof MAC (custom)")
        print("  [3] Restore original MAC")
        print("  [99] Return\033[0m\n")
        choice = self.get_user_input("MAC_SPOOF")
        if choice == "1":
            iface = self._get_target("Enter interface (e.g. eth0)")
            if iface:
                self.stealth.mac_spoofer.interface = iface
                self.stealth.mac_spoofer.spoof_mac()
        elif choice == "2":
            iface = self._get_target("Enter interface (e.g. eth0)")
            mac = self._get_target("Enter new MAC address (e.g. aa:bb:cc:dd:ee:ff)")
            if iface and mac:
                self.stealth.mac_spoofer.interface = iface
                self.stealth.mac_spoofer.spoof_mac(mac)
        elif choice == "3":
            self.stealth.mac_spoofer.restore_mac()
        input("\n\033[38;5;244mPress Enter to continue...\033[0m")

    def _run_tor_manager(self, name: str):
        """TOR network management"""
        print("\n\033[38;5;51m  [1] Start TOR")
        print("  [2] Stop TOR")
        print("  [3] Get new TOR identity")
        print("  [4] Show TOR exit IP")
        print("  [99] Return\033[0m\n")
        choice = self.get_user_input("TOR")
        if choice == "1":
            self.stealth.tor_manager.start_tor()
        elif choice == "2":
            self.stealth.tor_manager.stop_tor()
        elif choice == "3":
            self.stealth.tor_manager.get_new_identity()
        elif choice == "4":
            ip = self.stealth.tor_manager.get_exit_ip()
            self.display_message(f"TOR exit IP: {ip}", "info")
        input("\n\033[38;5;244mPress Enter to continue...\033[0m")

    def _run_proxy_chain(self, name: str):
        """Proxy chain configuration"""
        print("\n\033[38;5;51m  [1] Add proxy to chain")
        print("  [2] View current chain")
        print("  [3] Generate config")
        print("  [4] Apply config")
        print("  [5] Clear chain")
        print("  [99] Return\033[0m\n")
        choice = self.get_user_input("PROXY")
        if choice == "1":
            host = self._get_target("Enter proxy host")
            port_str = self._get_target("Enter proxy port")
            ptype = self._get_target("Enter type (socks4/socks5/http)") or "socks5"
            if host and port_str:
                self.stealth.proxy_chain.add_proxy(host, int(port_str), ptype)
                self.display_message("Proxy added to chain", "success")
        elif choice == "2":
            proxies = [vars(p) for p in self.stealth.proxy_chain.proxies]
            self._print_results(proxies, "Proxy Chain")
            return
        elif choice == "3":
            config = self.stealth.proxy_chain.generate_config()
            print(config)
        elif choice == "4":
            self.stealth.proxy_chain.apply_config()
        elif choice == "5":
            self.stealth.proxy_chain.clear_chain()
            self.display_message("Proxy chain cleared", "success")
        input("\n\033[38;5;244mPress Enter to continue...\033[0m")

    def _run_log_cleaner(self, name: str):
        """Log cleaning / anti-forensics"""
        print("\n\033[38;5;51m  [1] List log files")
        print("  [2] Clear shell history")
        print("  [3] Shred a file")
        print("  [99] Return\033[0m\n")
        choice = self.get_user_input("LOGS")
        if choice == "1":
            logs = self.stealth.log_cleaner.list_logs()
            self._print_results(logs, "Detected Log Files")
            return
        elif choice == "2":
            self.stealth.log_cleaner.clear_history()
        elif choice == "3":
            filepath = self._get_target("Enter file path to shred")
            if filepath:
                self.stealth.log_cleaner.shred_file(filepath)
        input("\n\033[38;5;244mPress Enter to continue...\033[0m")

    # =========================================================================
    # CONTROL_QUICKHACKS - Network Analysis (30-34)
    # =========================================================================

    def _run_host_discovery(self, name: str):
        """Discover hosts on network"""
        network = self._get_target("Enter network CIDR (e.g. 192.168.1.0/24)")
        if not network:
            network = "192.168.1.0/24"
        self.display_message(f"Discovering hosts on {network}...", "quickhack")
        hosts = self.network_analyzer.discover_hosts(network)
        self._print_results([vars(h) for h in hosts], f"Hosts Discovered: {network}")

    def _run_trace_route(self, name: str):
        """Trace route to target"""
        target = self._get_target("Enter target for traceroute")
        if not target:
            return
        self.display_message(f"Tracing route to {target}...", "quickhack")
        result = self.network_analyzer.trace_route(target)
        self._print_results(result, f"Traceroute: {target}")

    def _run_bandwidth_monitor(self, name: str):
        """Bandwidth monitoring"""
        iface = self._get_target("Enter interface (e.g. eth0)") or "eth0"
        self.display_message(f"Reading bandwidth on {iface}...", "quickhack")
        result = self.network_analyzer.get_bandwidth_stats(iface)
        self._print_results(result, f"Bandwidth: {iface}")

    def _run_interface_list(self, name: str):
        """List network interfaces"""
        self.display_message("Listing network interfaces...", "quickhack")
        interfaces = self.network_analyzer.get_interfaces()
        self._print_results(interfaces, "Network Interfaces")

    def _run_traffic_stats(self, name: str):
        """Traffic statistics"""
        self.display_message("Getting traffic statistics...", "quickhack")
        result = self.network_analyzer.get_traffic_stats()
        self._print_results(result, "Traffic Statistics")

    # =========================================================================
    # DAEMON_UPLOAD - Advanced Recon (40-44)
    # =========================================================================

    def _run_dns_enum(self, name: str):
        """DNS enumeration"""
        target = self._get_target("Enter domain for DNS enumeration")
        if not target:
            return
        self.display_message(f"Enumerating DNS records for {target}...", "quickhack")
        result = self.recon.dns_enum.scan(target)
        self._print_results(vars(result), f"DNS Enumeration: {target}")

    def _run_subdomain_finder(self, name: str):
        """Subdomain discovery"""
        target = self._get_target("Enter domain for subdomain discovery")
        if not target:
            return
        self.display_message(f"Finding subdomains for {target}...", "quickhack")
        result = self.recon.subdomain_finder.scan(target)
        self._print_results(vars(result), f"Subdomains: {target}")

    def _run_tech_fingerprint(self, name: str):
        """Technology fingerprinting"""
        target = self._get_target("Enter URL for technology fingerprinting")
        if not target:
            return
        self.display_message(f"Fingerprinting technologies on {target}...", "quickhack")
        result = self.recon.tech_fingerprint.scan(target)
        self._print_results(vars(result), f"Tech Fingerprint: {target}")

    def _run_quick_recon(self, name: str):
        """Quick reconnaissance scan"""
        target = self._get_target("Enter target for quick recon")
        if not target:
            return
        self.display_message(f"Quick recon on {target}...", "quickhack")
        results = self.recon.quick_scan(target)
        output = {k: vars(v) for k, v in results.items()}
        self._print_results(output, f"Quick Recon: {target}")

    def _run_full_recon(self, name: str):
        """Full reconnaissance scan"""
        target = self._get_target("Enter target for full recon")
        if not target:
            return
        self.display_message(f"Full reconnaissance on {target}...", "quickhack")
        results = self.recon.full_scan(target)
        output = {k: vars(v) for k, v in results.items()}
        self._print_results(output, f"Full Recon: {target}")

    # =========================================================================
    # ULTIMATE_QUICKHACKS - Cloud Security (50-54)
    # =========================================================================

    def _run_cloud_aws_scan(self, name: str):
        """AWS S3 bucket enumeration"""
        company = self._get_target("Enter company/org name for AWS S3 enumeration")
        if not company:
            return
        self.display_message(f"Enumerating AWS S3 buckets for {company}...", "quickhack")
        result = self.cloud_scanner.scan_aws(company)
        self._print_results(vars(result), f"AWS S3 Scan: {company}")

    def _run_cloud_azure_scan(self, name: str):
        """Azure storage enumeration"""
        company = self._get_target("Enter company/org name for Azure storage enumeration")
        if not company:
            return
        self.display_message(f"Enumerating Azure storage for {company}...", "quickhack")
        result = self.cloud_scanner.scan_azure(company)
        self._print_results(vars(result), f"Azure Scan: {company}")

    def _run_cloud_gcp_scan(self, name: str):
        """GCP storage enumeration"""
        company = self._get_target("Enter company/project name for GCP bucket scan")
        if not company:
            return
        self.display_message(f"Enumerating GCP buckets for {company}...", "quickhack")
        result = self.cloud_scanner.scan_gcp(company)
        self._print_results(vars(result), f"GCP Scan: {company}")

    def _run_cloud_full_scan(self, name: str):
        """Full cloud scan across AWS/Azure/GCP"""
        company = self._get_target("Enter company name for full cloud scan")
        if not company:
            return
        self.display_message(f"Full cloud scan for {company}...", "quickhack")
        results = self.cloud_scanner.full_cloud_scan(company)
        output = {k: vars(v) for k, v in results.items()}
        self._print_results(output, f"Full Cloud Scan: {company}")

    def _run_container_scan(self, name: str):
        """Container/Kubernetes scanning"""
        print("\n\033[38;5;51m  [1] Scan Docker registry")
        print("  [2] Check Kubernetes API")
        print("  [99] Return\033[0m\n")
        choice = self.get_user_input("CONTAINER")
        if choice == "1":
            url = self._get_target("Enter Docker registry URL")
            if url:
                result = self.cloud_scanner.scan_registry(url)
                self._print_results(result, f"Docker Registry: {url}")
                return
        elif choice == "2":
            url = self._get_target("Enter Kubernetes API URL")
            if url:
                result = self.cloud_scanner.check_k8s_api(url)
                self._print_results(result, f"K8s API: {url}")
                return
        input("\n\033[38;5;244mPress Enter to continue...\033[0m")

    # =========================================================================
    # ARASAKA_PROTOCOLS - Social Engineering (60-64)
    # =========================================================================

    def _run_phishing_server(self, name: str):
        """Start phishing server"""
        templates = self.social.list_templates()
        print("\n\033[38;5;51mAvailable phishing templates:\033[0m")
        for i, t in enumerate(templates, 1):
            print(f"  \033[38;5;51m[{i}]\033[0m {t}")
        choice = self._get_target("Select template number")
        port_str = self._get_target("Enter port (default 8080)") or "8080"
        if choice and choice.isdigit() and 1 <= int(choice) <= len(templates):
            template = templates[int(choice) - 1]
            self.display_message(f"Starting phishing server with '{template}' on port {port_str}...", "quickhack")
            self.display_message("Press Ctrl+C to stop the server.", "warning")
            try:
                self.social.start_phishing(template, int(port_str))
            except KeyboardInterrupt:
                self.display_message("Phishing server stopped.", "info")
        input("\n\033[38;5;244mPress Enter to continue...\033[0m")

    def _run_phishing_templates(self, name: str):
        """List and view phishing templates"""
        templates = self.social.list_templates()
        self._print_results(templates, "Available Phishing Templates")

    def _run_qr_generator(self, name: str):
        """QR code generation"""
        data = self._get_target("Enter data/URL for QR code")
        if not data:
            return
        output = self._get_target("Enter output path (or press Enter for /tmp)")
        result = self.social.generate_qr(data, output if output else None)
        if result:
            self.display_message(f"QR code saved to: {result}", "success")
        else:
            self.display_message("QR generation failed - qrcode library may not be installed", "error")
        input("\n\033[38;5;244mPress Enter to continue...\033[0m")

    def _run_social_profiler(self, name: str):
        """Social media username profiling"""
        username = self._get_target("Enter username to profile across platforms")
        if not username:
            return
        self.display_message(f"Profiling username '{username}' across platforms...", "quickhack")
        result = self.social.profile_username(username)
        self._print_results(result, f"Social Profile: {username}")

    def _run_email_search(self, name: str):
        """Email breach search"""
        email = self._get_target("Enter email address to search")
        if not email:
            return
        self.display_message(f"Searching for {email} in breach databases...", "quickhack")
        result = self.social.social_profiler.search_email(email)
        self._print_results(result, f"Email Search: {email}")

    # =========================================================================
    # MILITECH_ARSENAL - Exploitation (70-74)
    # =========================================================================

    def _run_exploit_vuln_scan(self, name: str):
        """Vulnerability scanning"""
        target = self._get_target("Enter target IP for vulnerability scan")
        if not target:
            return
        self.display_message(f"Scanning {target} for vulnerabilities...", "quickhack")
        result = self.exploit_framework.scan_vulnerabilities(target)
        self._print_results(result, f"Vulnerability Scan: {target}")

    def _run_payload_generator(self, name: str):
        """Payload generation"""
        available = self.exploit_framework.list_payloads()
        print("\n\033[38;5;51mAvailable payload types:\033[0m")
        all_shells = available.get('reverse_shells', [])
        for i, s in enumerate(all_shells, 1):
            print(f"  \033[38;5;51m[{i}]\033[0m {s}")
        choice = self._get_target("Select shell type number")
        host = self._get_target("Enter LHOST (your IP)")
        port_str = self._get_target("Enter LPORT") or "4444"
        if choice and choice.isdigit() and host:
            idx = int(choice) - 1
            if 0 <= idx < len(all_shells):
                shell_type = all_shells[idx]
                payload = self.exploit_framework.generate_payload(shell_type, host, int(port_str))
                print(f"\n\033[38;5;51m{'='*60}")
                print(f"◢◤ Generated Payload: {payload.name}")
                print(f"{'='*60}\033[0m\n")
                print(f"\033[38;5;47m{payload.code}\033[0m")
        input("\n\033[38;5;244mPress Enter to continue...\033[0m")

    def _run_shell_handler(self, name: str):
        """Start reverse shell listener"""
        host = self._get_target("Enter LHOST to listen on (default 0.0.0.0)") or "0.0.0.0"
        port_str = self._get_target("Enter LPORT (default 4444)") or "4444"
        self.display_message(f"Starting listener on {host}:{port_str}...", "quickhack")
        self.display_message("Waiting for connection... Press Ctrl+C to cancel.", "warning")
        try:
            self.exploit_framework.start_handler(host, int(port_str))
        except KeyboardInterrupt:
            self.display_message("Listener stopped.", "info")
        input("\n\033[38;5;244mPress Enter to continue...\033[0m")

    def _run_list_payloads(self, name: str):
        """List available payloads"""
        result = self.exploit_framework.list_payloads()
        self._print_results(result, "Available Payloads")

    def _run_active_sessions(self, name: str):
        """List active shell sessions"""
        sessions = self.exploit_framework.get_active_sessions()
        if sessions:
            self._print_results(sessions, "Active Sessions")
        else:
            self.display_message("No active sessions.", "info")
            input("\n\033[38;5;244mPress Enter to continue...\033[0m")

    # =========================================================================
    # BLACKHAND_FORENSICS - Digital Forensics (80-84)
    # =========================================================================

    def _run_file_analysis(self, name: str):
        """Comprehensive file analysis"""
        filepath = self._get_target("Enter file path to analyze")
        if not filepath:
            return
        self.display_message(f"Analyzing {filepath}...", "quickhack")
        result = self.forensics.analyze_file(filepath)
        self._print_results(result, f"File Analysis: {filepath}")

    def _run_disk_imager(self, name: str):
        """Forensic disk imaging"""
        source = self._get_target("Enter source device/file (e.g. /dev/sda)")
        dest = self._get_target("Enter destination path for image")
        if not source or not dest:
            return
        self.display_message(f"Creating forensic image of {source}...", "quickhack")
        result = self.forensics.create_disk_image(source, dest)
        self._print_results(result, f"Disk Image: {source}")

    def _run_file_carver(self, name: str):
        """File carving from raw data"""
        source = self._get_target("Enter source file/image to carve from")
        output = self._get_target("Enter output directory (default /tmp/carved)") or "/tmp/carved"
        if not source:
            return
        self.display_message(f"Carving files from {source}...", "quickhack")
        results = self.forensics.carve_files(source, output)
        self._print_results(results, f"Carved Files from {source}")

    def _run_metadata_stripper(self, name: str):
        """Metadata extraction and analysis"""
        filepath = self._get_target("Enter file path for metadata extraction")
        if not filepath:
            return
        self.display_message(f"Extracting metadata from {filepath}...", "quickhack")
        metadata = self.forensics.metadata_extractor.extract(filepath)
        self._print_results(vars(metadata), f"Metadata: {filepath}")

    def _run_timeline_builder(self, name: str):
        """Build forensic timeline"""
        dirpath = self._get_target("Enter directory path for timeline analysis")
        fmt = self._get_target("Export format (json/csv, default json)") or "json"
        if not dirpath:
            return
        self.display_message(f"Building timeline from {dirpath}...", "quickhack")
        output_path = self.forensics.build_timeline(dirpath, fmt)
        self.display_message(f"Timeline exported to: {output_path}", "success")
        input("\n\033[38;5;244mPress Enter to continue...\033[0m")

    # =========================================================================
    # RELIC_CRYPTO - Cryptographic Analysis (90-94)
    # =========================================================================

    def _run_hash_cracker(self, name: str):
        """Hash cracking"""
        hash_val = self._get_target("Enter hash value to crack")
        if not hash_val:
            return
        print("\n\033[38;5;51m  [1] Dictionary attack")
        print("  [2] Brute force attack\033[0m\n")
        method = self.get_user_input("METHOD")
        if method == "1":
            wordlist = self._get_target("Enter wordlist path (default /usr/share/wordlists/rockyou.txt)")
            wordlist = wordlist or "/usr/share/wordlists/rockyou.txt"
            self.display_message("Running dictionary attack...", "quickhack")
            result = self.crypto.crack_hash(hash_val, method="dictionary", wordlist=wordlist)
        elif method == "2":
            max_len = self._get_target("Max password length (default 6)") or "6"
            self.display_message("Running brute force attack...", "quickhack")
            result = self.crypto.crack_hash(hash_val, method="bruteforce", max_len=int(max_len))
        else:
            return
        if result:
            self.display_message(f"CRACKED! Plaintext: {result}", "success")
        else:
            self.display_message("Hash not cracked.", "warning")
        input("\n\033[38;5;244mPress Enter to continue...\033[0m")

    def _run_cipher_tools(self, name: str):
        """Encoding/decoding tools"""
        print("\n\033[38;5;51m  [1] Encode (base64/hex/rot13)")
        print("  [2] Decode (base64/hex/rot13)")
        print("  [3] Caesar cipher")
        print("  [4] XOR cipher")
        print("  [5] Hash a string\033[0m\n")
        choice = self.get_user_input("CIPHER")
        if choice == "1":
            data = self._get_target("Enter data to encode")
            enc = self._get_target("Encoding type (base64/hex/rot13)")
            if data and enc:
                result = self.crypto.encode(data, enc)
                self.display_message(f"Encoded: {result}", "success")
        elif choice == "2":
            data = self._get_target("Enter data to decode")
            enc = self._get_target("Encoding type (base64/hex/rot13)")
            if data and enc:
                result = self.crypto.decode(data, enc)
                self.display_message(f"Decoded: {result}", "success")
        elif choice == "3":
            data = self._get_target("Enter text")
            shift = self._get_target("Enter shift value") or "3"
            result = self.crypto.encoder.caesar_cipher(data, int(shift))
            self.display_message(f"Result: {result}", "success")
        elif choice == "4":
            data = self._get_target("Enter text")
            key = self._get_target("Enter XOR key")
            if data and key:
                result = self.crypto.encoder.xor_cipher(data, key)
                self.display_message(f"Result: {result}", "success")
        elif choice == "5":
            data = self._get_target("Enter string to hash")
            algo = self._get_target("Algorithm (md5/sha1/sha256/sha512)") or "sha256"
            if data:
                result = self.crypto.hash_string(data, algo)
                self.display_message(f"{algo.upper()}: {result}", "success")
        input("\n\033[38;5;244mPress Enter to continue...\033[0m")

    def _run_key_generator(self, name: str):
        """Secure key/password generation"""
        print("\n\033[38;5;51m  [1] Generate secure password")
        print("  [2] Generate UUID")
        print("  [3] Generate random bytes (hex)\033[0m\n")
        choice = self.get_user_input("KEYGEN")
        if choice == "1":
            length = self._get_target("Password length (default 16)") or "16"
            password = self.crypto.generate_password(int(length))
            self.display_message(f"Generated password: {password}", "success")
        elif choice == "2":
            uuid = self.crypto.key_generator.generate_uuid()
            self.display_message(f"UUID: {uuid}", "success")
        elif choice == "3":
            length = self._get_target("Byte length (default 32)") or "32"
            rand_bytes = self.crypto.key_generator.generate_random_bytes(int(length))
            self.display_message(f"Random bytes: {rand_bytes.hex()}", "success")
        input("\n\033[38;5;244mPress Enter to continue...\033[0m")

    def _run_stego_analyzer(self, name: str):
        """Steganography analysis"""
        filepath = self._get_target("Enter file path to analyze for hidden data")
        if not filepath:
            return
        self.display_message(f"Analyzing {filepath} for steganography...", "quickhack")
        result = self.crypto.analyze_for_stego(filepath)
        self._print_results(result, f"Steganography Analysis: {filepath}")

    def _run_hash_identifier(self, name: str):
        """Hash type identification"""
        hash_val = self._get_target("Enter hash value to identify")
        if not hash_val:
            return
        result = self.crypto.identify_hash(hash_val)
        if result:
            self.display_message(f"Possible hash types: {', '.join(result)}", "success")
        else:
            self.display_message("Could not identify hash type.", "warning")
        input("\n\033[38;5;244mPress Enter to continue...\033[0m")
    
    def show_config_menu(self):
        """Display Cyberdeck configuration menu"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n\033[38;5;201m╔════════════════════════════════════════════════════════════════╗")
        print("║         \033[38;5;51m◢◤ CYBERDECK CONFIGURATION INTERFACE ◢◤\033[38;5;201m               ║")
        print("╚════════════════════════════════════════════════════════════════╝\033[0m\n")
        
        print("\033[38;5;51m  [1] Set Operations Directory (Safehouse)")
        print("  [2] Configure Proxy Chain (Anonymity)")
        print("  [3] Update PHANTOM (Download Latest)")
        print("  [4] Check for Updates (Scan Darknet)")
        print("  [5] View Cyberdeck Specs")
        print("  [6] Reset Cyberdeck (Factory Default)")
        print("  [7] Uninstall PHANTOM (Burn Evidence)")
        print("  [99] Return to Main Interface\033[0m\n")
        
        choice = self.get_user_input("CONFIG")
        self._handle_config_choice(choice)
    
    def _handle_config_choice(self, choice: str):
        """Handle configuration menu selection"""
        if choice == "1":
            self._set_operations_directory()
        elif choice == "2":
            self._configure_proxy()
        elif choice == "3":
            self._update_phantom()
        elif choice == "4":
            self._check_updates()
        elif choice == "5":
            self._show_system_info()
        elif choice == "6":
            self._reset_configuration()
        elif choice == "7":
            self._uninstall_phantom()
    
    def _set_operations_directory(self):
        """Set the Netrunner safehouse directory"""
        print("\n\033[38;5;51mCurrent safehouse: " + os.getcwd() + "\033[0m")
        new_path = input("\nEnter new safehouse location (or press Enter to keep current): ").strip()
        if new_path:
            if os.path.exists(new_path):
                self.display_message(f"Safehouse relocated to: {new_path}", "success")
            else:
                create = input("\033[38;5;226mLocation doesn't exist. Create it? [y/n]: \033[0m").strip().lower()
                if create == 'y':
                    os.makedirs(new_path, exist_ok=True)
                    self.display_message(f"New safehouse established: {new_path}", "success")
        input("\n\033[38;5;244mPress Enter to continue...\033[0m")
    
    def _configure_proxy(self):
        """Configure proxy chain for anonymity"""
        print("\n\033[38;5;51m◢◤ Proxy Chain Configuration ◢◤\033[0m")
        proxy = input("Enter proxy address (e.g., socks5://127.0.0.1:9050): ").strip()
        if proxy:
            self.display_message(f"Proxy chain configured: {proxy}", "success")
            self.display_message("Your connection is now routed through the proxy.", "info")
        input("\n\033[38;5;244mPress Enter to continue...\033[0m")
    
    def _update_phantom(self):
        """Update PHANTOM from the darknet"""
        self.display_message("Connecting to Night City darknet for updates...", "info")
        os.system("git pull origin main 2>/dev/null || git pull origin master 2>/dev/null")
        self.display_message("Cyberdeck firmware updated!", "success")
        input("\n\033[38;5;244mPress Enter to continue...\033[0m")
    
    def _check_updates(self):
        """Scan darknet for available updates"""
        self.display_message("Scanning darknet for PHANTOM updates...", "info")
        self.display_message(f"Current firmware: v{self.VERSION}", "info")
        self.display_message("You have the latest version - Cyberdeck optimal!", "success")
        input("\n\033[38;5;244mPress Enter to continue...\033[0m")
    
    def _show_system_info(self):
        """Display Cyberdeck specifications"""
        import platform
        print("\n\033[38;5;51m" + "="*60)
        print("◢◤ CYBERDECK SPECIFICATIONS ◢◤")
        print("="*60 + "\033[0m\n")
        print(f"\033[38;5;201mModel:        \033[38;5;47m{self.CYBERDECK}")
        print(f"\033[38;5;201mFirmware:     \033[38;5;47mv{self.VERSION}")
        print(f"\033[38;5;201mCodename:     \033[38;5;47m{self.CODENAME}")
        print(f"\033[38;5;201mRAM Units:    \033[38;5;47m{self.state.ram_units}")
        print(f"\033[38;5;201mBuffer Slots: \033[38;5;47m6")
        print(f"\033[38;5;201mPython Core:  \033[38;5;47m{platform.python_version()}")
        print(f"\033[38;5;201mOS Substrate: \033[38;5;47m{platform.system()} {platform.release()}")
        print(f"\033[38;5;201mArchitecture: \033[38;5;47m{platform.machine()}")
        print(f"\033[38;5;201mNetrunner:    \033[38;5;47m{os.getenv('USER', 'unknown')}")
        print(f"\033[38;5;201mHome Node:    \033[38;5;47m{Path.home()}\033[0m")
        print(f"\n\033[38;5;226mICE Breached: \033[38;5;47m{self.state.ice_breached}\033[0m")
        input("\n\033[38;5;244mPress Enter to continue...\033[0m")
    
    def _reset_configuration(self):
        """Reset Cyberdeck to factory defaults"""
        confirm = input("\n\033[38;5;196mAre you sure you want to factory reset your Cyberdeck? [y/N]: \033[0m").strip().lower()
        if confirm == 'y':
            self.display_message("Cyberdeck reset to factory configuration", "success")
            self.display_message("All custom quickhacks and daemons purged.", "warning")
        input("\n\033[38;5;244mPress Enter to continue...\033[0m")
    
    def _uninstall_phantom(self):
        """Uninstall PHANTOM - Burn all evidence"""
        confirm = input("\n\033[38;5;196m⚠ DANGER: This will destroy all PHANTOM data. Continue? [y/N]: \033[0m").strip().lower()
        if confirm == 'y':
            self.display_message("Initiating evidence destruction protocol...", "warning")
            self.display_message("PHANTOM has been wiped. You were never here.", "success")
            sys.exit(0)
        input("\n\033[38;5;244mPress Enter to continue...\033[0m")
    
    def cleanup(self):
        """Cleanup resources before jack-out"""
        self.display_message("Cleaning traces from local subnet...", "info")
        self.state.session_active = False
    
    def run(self):
        """Main execution loop - Jack into the Net"""
        self.state.initialized = True
        self.state.session_active = True
        
        while self.state.session_active:
            try:
                self.display_banner()
                self.display_menu()
                
                choice = self.get_user_input()
                
                if choice == "00" or choice.lower() == "exit" or choice.lower() == "jackout":
                    self.display_message("Initiating jack-out sequence...", "warning")
                    self.cleanup()
                    print("\n\033[38;5;46m[✓] Neural link disconnected. Stay safe in Night City, choom!\033[0m\n")
                    break
                elif choice == "99":
                    self.show_config_menu()
                elif choice:
                    self.run_module(choice)
                    
            except KeyboardInterrupt:
                continue
            except Exception as e:
                self.display_message(f"ICE DETECTED: {str(e)}", "error")
                input("\033[38;5;244mPress Enter to continue...\033[0m")


def main():
    """Entry point for PHANTOM Netrunner - Welcome to Night City"""
    engine = PhantomEngine()
    engine.run()


if __name__ == "__main__":
    main()
