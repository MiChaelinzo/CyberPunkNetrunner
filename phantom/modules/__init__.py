#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHANTOM Security Modules - Tactical Operations Suite
"""

from phantom.modules.recon import ReconnaissanceModule
from phantom.modules.network import NetworkAnalyzer
from phantom.modules.exploit import ExploitFramework
from phantom.modules.stealth import StealthOperations
from phantom.modules.forensics import ForensicsModule
from phantom.modules.crypto import CryptoAnalyzer
from phantom.modules.web import WebSecurityScanner
from phantom.modules.wireless import WirelessModule
from phantom.modules.social import SocialEngineering
from phantom.modules.cloud import CloudSecurityScanner

__all__ = [
    "ReconnaissanceModule",
    "NetworkAnalyzer",
    "ExploitFramework",
    "StealthOperations",
    "ForensicsModule",
    "CryptoAnalyzer",
    "WebSecurityScanner",
    "WirelessModule",
    "SocialEngineering",
    "CloudSecurityScanner",
]
