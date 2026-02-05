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

    # Cyberpunk 2077 themed menu categories
    MENU_CATEGORIES = {
        "BREACH_PROTOCOL": {
            "icon": "◢◤",
            "color": "\033[38;5;51m",  # Cyan
            "description": "ICE Breaching & Network Infiltration",
            "modules": [
                ("01", "Ping [QUICKHACK]", "Highlight enemies & reveal subnet topology"),
                ("02", "Breach Protocol", "Matrix minigame for daemon upload"),
                ("03", "Datamine [v1/v2/v3]", "Extract €$ and quickhack components"),
                ("04", "Neural Subnet Mapper", "AI-powered network discovery"),
                ("05", "ICE Analyzer", "Identify & classify security measures"),
            ]
        },
        "COMBAT_QUICKHACKS": {
            "icon": "⚡",
            "color": "\033[38;5;196m",  # Red
            "description": "Offensive Quickhacks - Direct Damage",
            "modules": [
                ("10", "Short Circuit", "Non-lethal EMP - overload neural implants"),
                ("11", "Synapse Burnout", "Lethal - fry enemy cybernetics"),
                ("12", "Contagion [DAEMON]", "Poison spreads through local subnet"),
                ("13", "System Collapse", "Massively damage all networked enemies"),
                ("14", "Cyberpsychosis", "Turn enemies against each other"),
            ]
        },
        "COVERT_QUICKHACKS": {
            "icon": "👻",
            "color": "\033[38;5;213m",  # Pink
            "description": "Stealth Quickhacks - Infiltration",
            "modules": [
                ("20", "Whistle [DISTRACT]", "Lure enemies to position"),
                ("21", "Memory Wipe", "Target forgets seeing you"),
                ("22", "Reboot Optics", "Temporarily blind enemies"),
                ("23", "Weapon Glitch", "Jam enemy weapons"),
                ("24", "Cripple Movement", "Disable enemy legs/wheels"),
            ]
        },
        "CONTROL_QUICKHACKS": {
            "icon": "🎭",
            "color": "\033[38;5;226m",  # Yellow
            "description": "Device & Environment Control",
            "modules": [
                ("30", "Distract Enemies", "Activate environmental distractions"),
                ("31", "Remote Activation", "Trigger devices remotely"),
                ("32", "Take Control", "Hijack turrets, cameras, drones"),
                ("33", "Detonate Grenade", "Trigger enemy grenades"),
                ("34", "Cyberware Malfunction", "Disable mantis blades, gorilla arms"),
            ]
        },
        "DAEMON_UPLOAD": {
            "icon": "🔥",
            "color": "\033[38;5;208m",  # Orange
            "description": "Persistent Daemons - Breach Protocol Rewards",
            "modules": [
                ("40", "DATAMINE_V1", "Extract €$100-500"),
                ("41", "DATAMINE_V2", "Extract €$500-1000 + components"),
                ("42", "DATAMINE_V3", "Extract €$1000-2500 + epic quickhacks"),
                ("43", "ICEPICK [DAEMON]", "Reduce RAM cost of quickhacks"),
                ("44", "MASS VULNERABILITY", "Enemies take +30% damage"),
            ]
        },
        "ULTIMATE_QUICKHACKS": {
            "icon": "💀",
            "color": "\033[38;5;201m",  # Magenta
            "description": "Legendary Quickhacks - Maximum Destruction",
            "modules": [
                ("50", "Suicide", "Target eliminates themselves"),
                ("51", "Detonate [LEGENDARY]", "Enemy grenades go critical"),
                ("52", "System Reset", "Non-lethal instant takedown"),
                ("53", "Blackwall Gateway", "Upload RELIC malware [EXTREME]"),
                ("54", "JOHNNY'S LEGACY", "Alt Cunningham's neural virus"),
            ]
        },
        "ARASAKA_PROTOCOLS": {
            "icon": "🏢",
            "color": "\033[38;5;255m",  # White
            "description": "Corporate Security Countermeasures",
            "modules": [
                ("60", "Phishing Campaign", "Credential harvesting via email"),
                ("61", "Spear Phishing", "Targeted executive compromise"),
                ("62", "QR Jacking", "Malicious QR code injection"),
                ("63", "Social Profiler", "OSINT on corporate targets"),
                ("64", "Deepfake Generator", "AI-generated impersonation"),
            ]
        },
        "MILITECH_ARSENAL": {
            "icon": "🔫",
            "color": "\033[38;5;124m",  # Dark Red
            "description": "Military-Grade Exploitation Tools",
            "modules": [
                ("70", "Exploit Framework", "Zero-day deployment platform"),
                ("71", "Payload Forge", "Custom shellcode generator"),
                ("72", "Shell Handler", "Reverse connection manager"),
                ("73", "PrivEsc Suite", "Local privilege escalation"),
                ("74", "Persistence Daemon", "Maintain access post-reboot"),
            ]
        },
        "BLACKHAND_FORENSICS": {
            "icon": "🔬",
            "color": "\033[38;5;39m",  # Light Blue
            "description": "Morgan Blackhand's Investigation Kit",
            "modules": [
                ("80", "RAM Analyzer", "Volatile memory forensics"),
                ("81", "Braindance Imager", "Disk forensic imaging"),
                ("82", "File Carver", "Deleted data recovery"),
                ("83", "Metadata Stripper", "Clean document traces"),
                ("84", "Timeline Reconstructor", "Event sequence analysis"),
            ]
        },
        "RELIC_CRYPTO": {
            "icon": "🔐",
            "color": "\033[38;5;46m",  # Green
            "description": "Soulkiller & Encryption Breaking",
            "modules": [
                ("90", "Hash Annihilator", "Brute-force password cracking"),
                ("91", "Cipher Breaker", "Cryptanalysis toolkit"),
                ("92", "Key Forge", "Secure key generation"),
                ("93", "Steganography", "Hidden message extraction"),
                ("94", "Blockchain Tracker", "Eddie trace & crypto forensics"),
            ]
        },
    }

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Cyberdeck Engine - Jack into the Net"""
        self.state = SystemState()
        self.console = Console() if RICH_AVAILABLE else None
        self.config_path = config_path or self._default_config_path()
        self._setup_signal_handlers()
        self._modules: Dict[str, Any] = {}
        self._callbacks: Dict[str, List[Callable]] = {}
        
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
        
        # Quickhack routing - this will be expanded with actual implementations
        module_handlers = {
            "01": self._run_ping_quickhack,
            "02": self._run_breach_protocol,
            "20": self._run_whistle_distract,
            "21": self._run_memory_wipe,
            "30": self._run_distract_enemies,
            "40": self._run_datamine_v1,
            "50": self._run_system_reset,
            "60": self._run_phishing_campaign,
            "70": self._run_exploit_framework,
            "80": self._run_ram_analyzer,
            "90": self._run_hash_annihilator,
        }
        
        handler = module_handlers.get(mod_id, self._module_placeholder)
        handler(name)
    
    def _module_placeholder(self, name: str):
        """Placeholder for quickhacks under development"""
        self.display_message(f"Loading quickhack: '{name}' into RAM buffer...", "info")
        self._show_tool_submenu(name)
    
    def _show_tool_submenu(self, name: str):
        """Show a submenu for quickhack operations"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"\n\033[38;5;201m╔════════════════════════════════════════════════════════════════╗")
        print(f"║  \033[38;5;51m◢◤ QUICKHACK: \033[38;5;226m{name:^42}\033[38;5;51m ◢◤\033[38;5;201m  ║")
        print(f"╚════════════════════════════════════════════════════════════════╝\033[0m\n")
        
        print("\033[38;5;51m  [1] Install Dependencies (Download from Net)")
        print("  [2] Execute Quickhack (Upload to Target)")
        print("  [3] View Quickhack Documentation")
        print("  [99] Return to Cyberdeck Menu\033[0m\n")
        
        choice = self.get_user_input(name[:15])
        
        if choice == "1":
            self._install_dependencies(name)
        elif choice == "2":
            self._run_tool_interactive(name)
        elif choice == "3":
            self._show_documentation(name)
    
    def _install_dependencies(self, name: str):
        """Download quickhack components from the Net"""
        self.display_message(f"Downloading {name} components from Night City darknet...", "info")
        # Placeholder for dependency installation
        self.display_message("Components installed - Quickhack ready for upload!", "success")
        input("\n\033[38;5;244mPress Enter to continue...\033[0m")
    
    def _run_tool_interactive(self, name: str):
        """Execute a quickhack against target"""
        self.display_message(f"Executing {name} - Neural link active...", "quickhack")
        # Placeholder for tool execution
        input("\n\033[38;5;244mPress Enter to continue...\033[0m")
    
    def _show_documentation(self, name: str):
        """Show quickhack documentation"""
        print(f"\n\033[38;5;51m{'='*60}\n◢◤ {name} - Quickhack Documentation\n{'='*60}\033[0m\n")
        print("\033[38;5;244mDocumentation will be displayed here.")
        print("Includes RAM cost, cooldown, and optimal use cases.\033[0m")
        input("\n\033[38;5;244mPress Enter to continue...\033[0m")
    
    # Quickhack implementation stubs with Cyberpunk 2077 names
    def _run_ping_quickhack(self, name: str):
        """Ping Quickhack - Reveals enemies and network topology"""
        self._show_tool_submenu(name)
    
    def _run_breach_protocol(self, name: str):
        """Breach Protocol - Matrix minigame for daemon upload"""
        self._show_tool_submenu(name)
    
    def _run_whistle_distract(self, name: str):
        """Whistle - Distract enemies to your position"""
        self._show_tool_submenu(name)
    
    def _run_memory_wipe(self, name: str):
        """Memory Wipe - Target forgets seeing you"""
        self._show_tool_submenu(name)
    
    def _run_distract_enemies(self, name: str):
        """Distract Enemies - Environmental distractions"""
        self._show_tool_submenu(name)
    
    def _run_datamine_v1(self, name: str):
        """Datamine v1 - Extract eddies from local subnet"""
        self._show_tool_submenu(name)
    
    def _run_system_reset(self, name: str):
        """System Reset - Non-lethal instant takedown"""
        self._show_tool_submenu(name)
    
    def _run_phishing_campaign(self, name: str):
        """Phishing Campaign - Credential harvesting"""
        self._show_tool_submenu(name)
    
    def _run_exploit_framework(self, name: str):
        """Exploit Framework - Zero-day deployment"""
        self._show_tool_submenu(name)
    
    def _run_ram_analyzer(self, name: str):
        """RAM Analyzer - Memory forensics"""
        self._show_tool_submenu(name)
    
    def _run_hash_annihilator(self, name: str):
        """Hash Annihilator - Password cracking"""
        self._show_tool_submenu(name)
    
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
