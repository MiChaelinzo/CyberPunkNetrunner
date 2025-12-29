#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                                      ║
║   ██████╗ ██╗  ██╗ █████╗ ███╗   ██╗████████╗ ██████╗ ███╗   ███╗    ██╗   ██╗██████╗     ██████╗   ║
║   ██╔══██╗██║  ██║██╔══██╗████╗  ██║╚══██╔══╝██╔═══██╗████╗ ████║    ██║   ██║╚════██╗   ██╔═████╗  ║
║   ██████╔╝███████║███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║    ██║   ██║ █████╔╝   ██║██╔██║  ║
║   ██╔═══╝ ██╔══██║██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║    ╚██╗ ██╔╝ ╚═══██╗   ████╔╝██║  ║
║   ██║     ██║  ██║██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║     ╚████╔╝ ██████╔╝██╗╚██████╔╝  ║
║   ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝      ╚═══╝  ╚═════╝ ╚═╝ ╚═════╝   ║
║                                                                                                      ║
║   PHANTOM NETRUNNER v3.0 - Next-Generation Cybersecurity Operations Framework                        ║
║                                                                                                      ║
║   ⚡ Neural Network Powered Analysis                                                                  ║
║   🔒 Zero-Day Defense Capabilities                                                                   ║
║   🌐 Global Threat Intelligence Integration                                                          ║
║                                                                                                      ║
║   ⚠  FOR AUTHORIZED SECURITY TESTING ONLY  ⚠                                                        ║
║   🌐 https://github.com/MiChaelinzo/CyberPunkNetrunner                                               ║
║                                                                                                      ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝

PHANTOM - Advanced Cybersecurity Operations Framework

This is the main entry point for the PHANTOM Netrunner framework.
Run this script to launch the interactive security testing interface.

Usage:
    python phantom_runner.py [options]

Options:
    -h, --help          Show this help message
    -v, --version       Show version information
    -q, --quiet         Quiet mode (minimal output)
    --no-banner         Skip the banner display
    --config PATH       Path to configuration file

Copyright (c) 2024 CyberPunk Netrunner Project
Licensed under MIT License - For authorized security testing only
"""

import sys
import os
import argparse
from pathlib import Path

# Add phantom package to path
sys.path.insert(0, str(Path(__file__).parent))

__version__ = "3.0.0"
__codename__ = "PHANTOM"


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="PHANTOM Netrunner - Advanced Cybersecurity Operations Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s                    Start interactive mode
    %(prog)s --no-banner        Start without banner
    %(prog)s -v                 Show version
    
For more information, visit: https://github.com/MiChaelinzo/CyberPunkNetrunner
        """
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'PHANTOM Netrunner v{__version__} ({__codename__})'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Quiet mode - minimal output'
    )
    
    parser.add_argument(
        '--no-banner',
        action='store_true',
        help='Skip the banner display'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--module',
        type=str,
        default=None,
        help='Run specific module directly'
    )
    
    return parser.parse_args()


def check_python_version():
    """Check Python version compatibility"""
    if sys.version_info < (3, 7):
        print("[!] PHANTOM requires Python 3.7 or higher")
        print(f"[!] Current version: {sys.version}")
        sys.exit(1)


def check_dependencies():
    """Check for required dependencies"""
    required = ['requests']
    optional = ['rich', 'flask']
    
    missing_required = []
    missing_optional = []
    
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing_required.append(pkg)
    
    for pkg in optional:
        try:
            __import__(pkg)
        except ImportError:
            missing_optional.append(pkg)
    
    if missing_required:
        print("[!] Missing required dependencies:")
        for pkg in missing_required:
            print(f"    - {pkg}")
        print("\n[*] Install with: pip install " + " ".join(missing_required))
        sys.exit(1)
    
    if missing_optional:
        print("[*] Optional dependencies not installed (some features may be limited):")
        for pkg in missing_optional:
            print(f"    - {pkg}")
        print()


def main():
    """Main entry point"""
    # Parse arguments
    args = parse_arguments()
    
    # Check Python version
    check_python_version()
    
    # Check dependencies
    if not args.quiet:
        check_dependencies()
    
    # Import and run engine
    try:
        from phantom.core.engine import PhantomEngine
        
        engine = PhantomEngine(config_path=args.config)
        
        if args.module:
            # Run specific module
            engine.display_banner()
            engine.run_module(args.module)
        else:
            # Interactive mode
            engine.run()
            
    except KeyboardInterrupt:
        print("\n\n[!] Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[!] Fatal error: {e}")
        if '--debug' in sys.argv:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
