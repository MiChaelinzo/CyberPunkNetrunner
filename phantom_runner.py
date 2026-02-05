#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄  ║
║  █▓▒░ P H A N T O M   N E T R U N N E R ░▒▓█   ◢◤ NIGHT CITY EDITION ◢◤                                ║
║  ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                          ║
║   ██████╗ ██╗  ██╗ █████╗ ███╗   ██╗████████╗ ██████╗ ███╗   ███╗                                       ║
║   ██╔══██╗██║  ██║██╔══██╗████╗  ██║╚══██╔══╝██╔═══██╗████╗ ████║    NETRUNNER v3.0                     ║
║   ██████╔╝███████║███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║    Night City // 2077                 ║
║   ██╔═══╝ ██╔══██║██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║                                       ║
║   ██║     ██║  ██║██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║    "In the Net, no one               ║
║   ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝     hears you breach the ICE."      ║
║                                                                                                          ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║   ◢ QUICKHACKS ◤           ◢ DAEMONS ◤              ◢ ICE BREACHING ◤                                   ║
║   [■] Breach Protocol      [■] ICEPICK              [■] Neural Scanner                                   ║
║   [■] Short Circuit        [■] MASS VULNERABILITY   [■] Subnet Mapper                                    ║
║   [■] Cyberpsychosis       [■] DATAMINE             [■] Ghost Protocol                                   ║
║                                                                                                          ║
║   ⚠  NETWATCH ADVISORY: UNAUTHORIZED ACCESS IS A CORPO DEATH SENTENCE  ⚠                               ║
║   🌐 https://github.com/MiChaelinzo/CyberPunkNetrunner                                                   ║
║                                                                                                          ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════╝

PHANTOM NETRUNNER - Cyberpunk 2077 Inspired Cybersecurity Framework

This is the main jack-in point for the PHANTOM Netrunner cyberdeck.
Run this script to jack into the Net and access quickhacks.

Usage:
    python phantom_runner.py [options]

Options:
    -h, --help          Show this help message
    -v, --version       Show cyberdeck firmware version
    -q, --quiet         Quiet mode (stealth output)
    --no-banner         Skip the boot sequence animation
    --config PATH       Path to cyberdeck configuration file

Cyberpunk 2077 Terms:
    - ICE: Intrusion Countermeasures Electronics (security programs)
    - Quickhack: Rapid cyber attack uploaded to target
    - Daemon: Persistent background program
    - Netrunner: Professional hacker with neural interface
    - Jack In/Out: Connect/disconnect from the Net

Copyright (c) 2024 CyberPunk Netrunner Project
Licensed under MIT License - For authorized security testing only

"Wake the f*** up, Samurai. We have a city to burn." - Johnny Silverhand
"""

import sys
import os
import argparse
from pathlib import Path

# Add phantom package to path
sys.path.insert(0, str(Path(__file__).parent))

__version__ = "3.0.0"
__codename__ = "PHANTOM"
__cyberdeck__ = "Netwatch Netdriver Mk.5"


def parse_arguments():
    """Parse command line arguments for the Cyberdeck"""
    parser = argparse.ArgumentParser(
        description="PHANTOM Netrunner - Night City Cybersecurity Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s                    Jack into the Net (interactive mode)
    %(prog)s --no-banner        Skip boot animation
    %(prog)s -v                 Show cyberdeck firmware version
    
Cyberpunk 2077 Inspired - For authorized security testing only.
"In the Net, no one hears you breach the ICE."

For more information, visit: https://github.com/MiChaelinzo/CyberPunkNetrunner
        """
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'PHANTOM Netrunner v{__version__} ({__codename__}) // Cyberdeck: {__cyberdeck__}'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Ghost mode - stealth output'
    )
    
    parser.add_argument(
        '--no-banner',
        action='store_true',
        help='Skip the cyberdeck boot animation'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to cyberdeck configuration file'
    )
    
    parser.add_argument(
        '--module',
        type=str,
        default=None,
        help='Execute specific quickhack directly'
    )
    
    return parser.parse_args()


def check_python_version():
    """Check Python version compatibility"""
    if sys.version_info < (3, 7):
        print("\033[38;5;196m[✗ ICE] PHANTOM requires Python 3.7 or higher\033[0m")
        print(f"\033[38;5;244m[◢◤] Current version: {sys.version}\033[0m")
        sys.exit(1)


def check_dependencies():
    """Check for required cyberdeck components"""
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
        print("\033[38;5;196m[✗ ICE] Missing required cyberdeck components:\033[0m")
        for pkg in missing_required:
            print(f"\033[38;5;244m    - {pkg}\033[0m")
        print(f"\n\033[38;5;51m[◢◤] Install with: pip install " + " ".join(missing_required) + "\033[0m")
        sys.exit(1)
    
    if missing_optional:
        print("\033[38;5;226m[⚠ ALERT] Optional components not installed (some quickhacks limited):\033[0m")
        for pkg in missing_optional:
            print(f"\033[38;5;244m    - {pkg}\033[0m")
        print()


def main():
    """Main entry point - Jack into the Net"""
    # Parse arguments
    args = parse_arguments()
    
    # Check Python version
    check_python_version()
    
    # Check dependencies
    if not args.quiet:
        check_dependencies()
    
    # Import and run the Cyberdeck engine
    try:
        from phantom.core.engine import PhantomEngine
        
        engine = PhantomEngine(config_path=args.config)
        
        if args.module:
            # Execute specific quickhack
            engine.display_banner()
            engine.run_module(args.module)
        else:
            # Interactive netrunning mode
            engine.run()
            
    except KeyboardInterrupt:
        print("\n\n\033[38;5;226m[⚠ ALERT] Emergency jack-out initiated by user\033[0m")
        sys.exit(0)
    except Exception as e:
        print(f"\n\033[38;5;196m[✗ ICE] Critical system failure: {e}\033[0m")
        if '--debug' in sys.argv:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
