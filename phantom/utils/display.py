#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHANTOM Display Manager

Console output formatting, colors, and display utilities.
"""

import os
import sys
from typing import Optional

# ANSI Color Codes
class Colors:
    """ANSI color codes"""
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


class DisplayManager:
    """Console display manager"""
    
    def __init__(self, color_enabled: bool = True):
        self.color_enabled = color_enabled
        self.colors = Colors()
    
    def color(self, text: str, color: str) -> str:
        """Apply color to text"""
        if not self.color_enabled:
            return text
        color_code = getattr(self.colors, color.upper(), '')
        return f"{color_code}{text}{self.colors.RESET}"
    
    def success(self, message: str):
        """Print success message"""
        print(f"{self.colors.BRIGHT_GREEN}[✓] {message}{self.colors.RESET}")
    
    def error(self, message: str):
        """Print error message"""
        print(f"{self.colors.BRIGHT_RED}[✗] {message}{self.colors.RESET}")
    
    def warning(self, message: str):
        """Print warning message"""
        print(f"{self.colors.BRIGHT_YELLOW}[!] {message}{self.colors.RESET}")
    
    def info(self, message: str):
        """Print info message"""
        print(f"{self.colors.BRIGHT_CYAN}[*] {message}{self.colors.RESET}")
    
    def debug(self, message: str):
        """Print debug message"""
        print(f"{self.colors.BRIGHT_BLACK}[#] {message}{self.colors.RESET}")
    
    def header(self, text: str, char: str = "="):
        """Print header"""
        width = len(text) + 4
        line = char * width
        print(f"\n{self.colors.BRIGHT_MAGENTA}{line}")
        print(f"  {text}  ")
        print(f"{line}{self.colors.RESET}\n")
    
    def box(self, text: str, title: Optional[str] = None):
        """Print text in a box"""
        lines = text.split('\n')
        width = max(len(line) for line in lines) + 4
        
        print(f"{self.colors.CYAN}╔{'═' * width}╗")
        
        if title:
            title_line = f" {title} ".center(width)
            print(f"║{title_line}║")
            print(f"╠{'═' * width}╣")
        
        for line in lines:
            padded = f"  {line}".ljust(width)
            print(f"║{padded}║")
        
        print(f"╚{'═' * width}╝{self.colors.RESET}")
    
    def table(self, headers: list, rows: list):
        """Print simple table"""
        # Calculate column widths
        widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(widths):
                    widths[i] = max(widths[i], len(str(cell)))
        
        # Print header
        header_line = " │ ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
        print(f"{self.colors.BRIGHT_WHITE}{header_line}{self.colors.RESET}")
        print("─" * (sum(widths) + len(widths) * 3 - 1))
        
        # Print rows
        for row in rows:
            row_line = " │ ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row))
            print(row_line)
    
    def progress_bar(self, current: int, total: int, width: int = 40):
        """Print progress bar"""
        percent = current / total
        filled = int(width * percent)
        bar = "█" * filled + "░" * (width - filled)
        sys.stdout.write(f"\r{self.colors.CYAN}[{bar}] {percent*100:.1f}%{self.colors.RESET}")
        sys.stdout.flush()
        if current >= total:
            print()
    
    def clear(self):
        """Clear screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def banner(self, text: str):
        """Print ASCII banner"""
        print(f"{self.colors.BRIGHT_MAGENTA}{text}{self.colors.RESET}")


# Global display manager instance
display = DisplayManager()
