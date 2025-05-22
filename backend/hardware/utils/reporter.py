"""Threat analysis and reporting for automotive security."""
import time
from enum import Enum, auto
from typing import Any, Dict


class ThreatLevel(Enum):
    """Classification of potential security threats."""
    BENIGN = auto()
    SUSPICIOUS = auto()
    MALICIOUS = auto()

class SecurityReport:
    """Represents a security analysis of a captured packet."""
    
    def __init__(self, packet, threat_level: ThreatLevel, reason: str):
        self.packet = packet
        self.threat_level = threat_level
        self.reason = reason
        self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary for serialization."""
        return {
            'threat_level': self.threat_level.name,
            'reason': self.reason,
            'timestamp': self.timestamp,
            'packet': self.packet.to_dict()
        }

import logging

logger = logging.getLogger(__name__)

class SecurityAnalyzer:
    """Analyzes packets for potential security threats."""
    
    def __init__(self):
        self.jam_detection_threshold = 100  # Packets/second to detect jamming
        self.packet_history = []
        self.jam_window = 1.0  # Seconds to analyze for jamming
        logger.debug("SecurityAnalyzer initialized with jam_detection_threshold=%s", self.jam_detection_threshold)
    
    def _is_replay_attack(self, packet) -> bool:
        """Detect potential replay attacks.
        
        Args:
            packet: The packet to check for replay attacks
            
        Returns:
            bool: True if a replay attack is detected, False otherwise
        """
        current_time = time.time()
        
        # Look for packets with the same payload and frequency but different RSSI
        # within the last 5 seconds
        for p in self.packet_history:
            time_diff = current_time - p.timestamp
            if time_diff >= 5.0:
                continue
                
            # Check if payload and frequency match but RSSI is different
            if (hasattr(p, 'payload') and hasattr(packet, 'payload') and 
                hasattr(p, 'freq') and hasattr(packet, 'freq') and
                hasattr(p, 'rssi') and hasattr(packet, 'rssi')):
                
                if (p.payload == packet.payload and 
                    p.freq == packet.freq and 
                    abs(p.rssi - packet.rssi) > 3):  # Small threshold for test environment
                    logger.debug(
                        "Replay attack detected: same payload (%.2f MHz) with different RSSI (%.1f vs %.1f)",
                        p.freq, p.rssi, packet.rssi
                    )
                    return True
                
        return False
    
    def _is_jamming_attack(self) -> bool:
        """Detect potential jamming attempts."""
        current_time = time.time()
        recent_packets = [p for p in self.packet_history 
                         if current_time - p.timestamp < self.jam_window]
        
        if len(recent_packets) > self.jam_detection_threshold:
            return True
        return False
    
    def analyze_packet(self, packet) -> SecurityReport:
        """Analyze a packet and return a security report."""
        logger.debug("Analyzing packet: %s", packet.to_dict() if hasattr(packet, 'to_dict') else str(packet))
        
        # Clean up old packets from history
        current_time = time.time()
        self.packet_history = [p for p in self.packet_history 
                             if current_time - p.timestamp < self.jam_window]
        
        # Update packet history with current packet
        self.packet_history.append(packet)
        
        # Check for replay attacks
        if self._is_replay_attack(packet):
            logger.warning("Replay attack detected in packet: %s", packet.payload)
            return SecurityReport(
                packet=packet,
                threat_level=ThreatLevel.MALICIOUS,
                reason="Potential replay attack detected"
            )
        
        # Check for jamming
        if self._is_jamming_attack():
            logger.warning("Jamming attack detected")
            return SecurityReport(
                packet=packet,
                threat_level=ThreatLevel.MALICIOUS,
                reason="Potential jamming attack detected"
            )
        
        # No threats detected
        logger.debug("No threats detected in packet")
        return SecurityReport(
            packet=packet,
            threat_level=ThreatLevel.BENIGN,
            reason="No threats detected"
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Return current security metrics."""
        current_time = time.time()
        recent_packets = [p for p in self.packet_history 
                         if current_time - p.timestamp < self.jam_window]
        
        return {
            'packets_per_second': len(recent_packets) / self.jam_window,
            'total_packets_analyzed': len(self.packet_history),
            'jamming_threshold': self.jam_detection_threshold,
            'analysis_window_sec': self.jam_window
        }
