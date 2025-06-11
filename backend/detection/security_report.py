"""
security_report.py

Defines SecurityReport for reporting and serializing security analysis results.
"""
import time
from .threat_levels import ThreatLevel

class SecurityReport:
    """
    Represents a security analysis of a captured packet.
    """
    def __init__(self, packet, threat_level: ThreatLevel, reason: str):
        self.packet = packet
        self.threat_level = threat_level
        self.reason = reason
        self.timestamp = time.time()

    def to_dict(self):
        """
        Convert report to dictionary for serialization.
        """
        return {
            'threat_level': self.threat_level.name,
            'reason': self.reason,
            'timestamp': self.timestamp,
            'packet': self.packet.to_dict() if hasattr(self.packet, 'to_dict') else str(self.packet)
        }
