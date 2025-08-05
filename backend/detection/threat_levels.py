"""
threat_levels.py

Defines threat level classification for automotive security events.
"""

from enum import Enum, auto


class ThreatLevel(Enum):
    """
    Classification of potential security threats.
    """

    BENIGN = auto()
    SUSPICIOUS = auto()
    MALICIOUS = auto()
