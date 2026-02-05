#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHANTOM Display Manager - Night City Terminal Interface

Console output formatting with Cyberpunk 2077 aesthetic.
Neon colors, terminal glitch effects, and Night City style.

"The Net is deep, and full of ICE." - Netrunner Proverb
"""

import os
import sys
from typing import Optional

# ANSI Color Codes - Cyberpunk 2077 Palette
class Colors:
    """ANSI color codes - Night City Neon Palette"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'
    
    # Regular colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # Cyberpunk 2077 Custom Colors (256-color mode)
    NEON_CYAN = '\033[38;5;51m'      # Primary UI color
    NEON_MAGENTA = '\033[38;5;201m'  # Secondary accent
    NEON_PINK = '\033[38;5;198m'     # Danger/hostile
    NEON_YELLOW = '\033[38;5;226m'   # Warnings/highlights
    NEON_GREEN = '\033[38;5;46m'     # Success/friendly
    NEON_ORANGE = '\033[38;5;208m'   # Daemons/special
    NEON_RED = '\033[38;5;196m'      # ICE/enemies
    NEON_BLUE = '\033[38;5;39m'      # Info/neutral
    CORPO_WHITE = '\033[38;5;255m'   # Corporate text
    STREET_GREY = '\033[38;5;244m'   # Dimmed text


class DisplayManager:
    """Night City Terminal Display Manager"""
    
    def __init__(self, color_enabled: bool = True):
        self.color_enabled = color_enabled
        self.colors = Colors()
    
    def color(self, text: str, color: str) -> str:
        """Apply neon color to text"""
        if not self.color_enabled:
            return text
        color_code = getattr(self.colors, color.upper(), '')
        return f"{color_code}{text}{self.colors.RESET}"
    
    def success(self, message: str):
        """Print breach successful message"""
        print(f"{self.colors.NEON_GREEN}[✓ BREACH] {message}{self.colors.RESET}")
    
    def error(self, message: str):
        """Print ICE detected message"""
        print(f"{self.colors.NEON_RED}[✗ ICE] {message}{self.colors.RESET}")
    
    def warning(self, message: str):
        """Print NetWatch alert message"""
        print(f"{self.colors.NEON_YELLOW}[⚠ ALERT] {message}{self.colors.RESET}")
    
    def info(self, message: str):
        """Print subnet info message"""
        print(f"{self.colors.NEON_CYAN}[◢◤] {message}{self.colors.RESET}")
    
    def debug(self, message: str):
        """Print system debug message"""
        print(f"{self.colors.STREET_GREY}[●] {message}{self.colors.RESET}")
    
    def quickhack(self, message: str):
        """Print quickhack loaded message"""
        print(f"{self.colors.NEON_MAGENTA}[⚡ QUICKHACK] {message}{self.colors.RESET}")
    
    def daemon(self, message: str):
        """Print daemon upload message"""
        print(f"{self.colors.NEON_ORANGE}[🔥 DAEMON] {message}{self.colors.RESET}")
    
    def header(self, text: str, char: str = "━"):
        """Print Cyberpunk style header"""
        width = len(text) + 4
        line = char * width
        print(f"\n{self.colors.NEON_MAGENTA}{line}")
        print(f"◢◤ {text} ◢◤")
        print(f"{line}{self.colors.RESET}\n")
    
    def box(self, text: str, title: Optional[str] = None):
        """Print text in a neon box"""
        lines = text.split('\n')
        width = max(len(line) for line in lines) + 4
        
        print(f"{self.colors.NEON_CYAN}╔{'═' * width}╗")
        
        if title:
            title_line = f" ◢◤ {title} ◢◤ ".center(width)
            print(f"║{title_line}║")
            print(f"╠{'═' * width}╣")
        
        for line in lines:
            padded = f"  {line}".ljust(width)
            print(f"║{padded}║")
        
        print(f"╚{'═' * width}╝{self.colors.RESET}")
    
    def table(self, headers: list, rows: list):
        """Print Night City style table"""
        # Calculate column widths
        widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(widths):
                    widths[i] = max(widths[i], len(str(cell)))
        
        # Print header
        header_line = " │ ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
        print(f"{self.colors.NEON_CYAN}{header_line}{self.colors.RESET}")
        print(f"{self.colors.NEON_MAGENTA}{'━' * (sum(widths) + len(widths) * 3 - 1)}{self.colors.RESET}")
        
        # Print rows
        for row in rows:
            row_line = " │ ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row))
            print(f"{self.colors.CORPO_WHITE}{row_line}{self.colors.RESET}")
    
    def progress_bar(self, current: int, total: int, width: int = 40, label: str = "UPLOADING"):
        """Print Cyberpunk style progress bar"""
        percent = current / total
        filled = int(width * percent)
        bar = "█" * filled + "░" * (width - filled)
        sys.stdout.write(f"\r{self.colors.NEON_CYAN}[{label}] [{bar}] {percent*100:.1f}%{self.colors.RESET}")
        sys.stdout.flush()
        if current >= total:
            print()
    
    def clear(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def banner(self, text: str):
        """Print ASCII art banner in neon colors"""
        print(f"{self.colors.NEON_MAGENTA}{text}{self.colors.RESET}")
    
    def breach_matrix(self, matrix: list):
        """Display a Breach Protocol style matrix"""
        print(f"\n{self.colors.NEON_CYAN}╔══════════════════════════════════╗")
        print(f"║  ◢◤ BREACH PROTOCOL MATRIX ◢◤   ║")
        print(f"╠══════════════════════════════════╣{self.colors.RESET}")
        for row in matrix:
            row_str = "  ".join(f"{self.colors.NEON_GREEN}{cell}{self.colors.RESET}" for cell in row)
            print(f"{self.colors.NEON_CYAN}║  {row_str}  ║{self.colors.RESET}")
        print(f"{self.colors.NEON_CYAN}╚══════════════════════════════════╝{self.colors.RESET}\n")
    
    def ram_display(self, used: int, total: int):
        """Display Cyberdeck RAM status"""
        available = total - used
        bar = f"{self.colors.NEON_GREEN}{'█' * available}{self.colors.NEON_RED}{'█' * used}{self.colors.RESET}"
        print(f"{self.colors.NEON_CYAN}RAM: [{bar}] {available}/{total} UNITS{self.colors.RESET}")


# Global display manager instance - Night City style
display = DisplayManager()
