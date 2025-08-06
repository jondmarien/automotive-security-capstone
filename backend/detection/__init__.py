"""
Automotive Security Detection Package

This package contains the core security analysis and threat detection components
for the automotive security capstone project.

Modules:
- event_logic: Core event detection algorithms and heuristics
- packet: RF packet structure definitions and parsing
- security_analyzer: Main security threat analysis engine
- security_report: Report generation and formatting
- threat_levels: Threat classification system (BENIGN/SUSPICIOUS/MALICIOUS)
"""

from .threat_levels import ThreatLevel
from .packet import Packet
from .event_logic import analyze_event
from .security_analyzer import SecurityAnalyzer
from .security_report import SecurityReport

__version__ = "0.1.0"
__all__ = [
    "ThreatLevel",
    "Packet", 
    "analyze_event",
    "SecurityAnalyzer",
    "SecurityReport",
]
