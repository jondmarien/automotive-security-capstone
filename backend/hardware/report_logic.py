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

class SecurityAnalyzer:
    """Analyzes packets for potential security threats."""
    
    def __init__(self):
        self.jam_detection_threshold = 100  # Packets/second to detect jamming
        self.packet_history = []
        self.jam_window = 1.0  # Seconds to analyze for jamming
    
    def _is_replay_attack(self, packet) -> bool:
        """Detect potential replay attacks."""
        # In a real implementation, this would check against a rolling code database
        # For now, we'll just check for exact duplicate payloads within a 
        # short time window to detect replay attacks.
        current_time = time.time()
        recent_packets = [p for p in self.packet_history 
                         if current_time - p.timestamp < 5.0]  # 5-second window
        
        for p in recent_packets:
            if (p.payload == packet.payload and 
                p.freq == packet.freq and 
                p.rssi != packet.rssi):
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
        # Update packet history
        self.packet_history.append(packet)
        
        # Check for replay attacks
        if self._is_replay_attack(packet):
            return SecurityReport(
                packet=packet,
                threat_level=ThreatLevel.MALICIOUS,
                reason="Potential replay attack detected"
            )
        
        # Check for jamming
        if self._is_jamming_attack():
            return SecurityReport(
                packet=packet,
                threat_level=ThreatLevel.MALICIOUS,
                reason="Potential jamming attack detected"
            )
        
        # No threats detected
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
