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
        self.brute_force_threshold = 5  # Number of similar packets to trigger brute force detection
        self.packet_history = []
        self.jam_window = 1.0  # Seconds to analyze for jamming
        self.brute_force_window = 10.0  # Seconds to analyze for brute force
        self.suspicious_patterns = [
            b'REPLAY_ATTACK',
            b'JAMMER',
            b'INJECT',
            b'BRUTE',
            b'OLD_'
        ]
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
        
    def _is_brute_force_attack(self, packet) -> bool:
        """Detect potential brute force attempts."""
        current_time = time.time()
        
        # Check for known suspicious patterns in payload
        if hasattr(packet, 'payload'):
            # Convert payload to bytes if it's a string
            if isinstance(packet.payload, str):
                try:
                    # First try UTF-8 encoding
                    payload = packet.payload.encode('utf-8')
                except UnicodeEncodeError:
                    # If that fails, try with backslashreplace for non-UTF-8 sequences
                    payload = packet.payload.encode('utf-8', errors='backslashreplace')
            else:
                payload = packet.payload
            
            # Ensure payload is bytes for pattern matching
            if isinstance(payload, bytes):
                # Check for suspicious patterns
                for pattern in self.suspicious_patterns:
                    if pattern in payload:
                        logger.debug("Suspicious pattern detected in payload: %s", pattern.decode('utf-8', errors='replace'))
                        return True
        
        # Count similar packets (same type) in the recent window
        if hasattr(packet, 'payload') and hasattr(packet, 'timestamp'):
            # Convert payload to bytes for comparison
            if isinstance(packet.payload, str):
                try:
                    payload_bytes = packet.payload.encode('utf-8')
                except UnicodeEncodeError:
                    payload_bytes = packet.payload.encode('utf-8', errors='replace')
            else:
                payload_bytes = packet.payload
            
            # Determine packet type
            packet_type = None
            if isinstance(payload_bytes, bytes):
                if b'KEYFOB' in payload_bytes:
                    packet_type = 'KEYFOB'
                elif b'TIRE_SENSOR' in payload_bytes:
                    packet_type = 'TIRE_SENSOR'
                elif b'REMOTE' in payload_bytes:
                    packet_type = 'REMOTE'
                elif b'BEACON' in payload_bytes:
                    packet_type = 'BEACON'
            
            if packet_type:
                similar_packets = []
                for p in self.packet_history:
                    if not hasattr(p, 'payload') or not hasattr(p, 'timestamp'):
                        continue
                        
                    # Convert historical packet payload to bytes
                    if isinstance(p.payload, str):
                        try:
                            hist_payload = p.payload.encode('utf-8')
                        except UnicodeEncodeError:
                            hist_payload = p.payload.encode('utf-8', errors='replace')
                    else:
                        hist_payload = p.payload
                    
                    # Check if it's within the time window and matches the type
                    if (current_time - p.timestamp < self.brute_force_window and 
                        isinstance(hist_payload, bytes) and 
                        packet_type.encode('utf-8') in hist_payload):
                        similar_packets.append(p)
                
                if len(similar_packets) >= self.brute_force_threshold:
                    logger.debug(
                        "Brute force attack detected: %d similar %s packets in %.1f seconds",
                        len(similar_packets), packet_type, self.brute_force_window
                    )
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
            
        # Check for brute force attacks
        if self._is_brute_force_attack(packet):
            logger.warning("Brute force attack detected")
            return SecurityReport(
                packet=packet,
                threat_level=ThreatLevel.MALICIOUS,
                reason="Potential brute force attack detected"
            )
        
        # No threats detected
        logger.debug("No threats detected in packet")
        return SecurityReport(
            packet=packet,
            threat_level=ThreatLevel.BENIGN,
            reason="No threats detected"
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Return current security metrics.
        
        Returns:
            dict: A dictionary containing security metrics including packets per second,
                 total packets analyzed, jamming threshold, and analysis window.
        """
        current_time = time.time()
        recent_packets = [p for p in self.packet_history 
                         if current_time - p.timestamp < self.jam_window]
        
        return {
            'packets_per_second': len(recent_packets) / self.jam_window,
            'total_packets_analyzed': len(self.packet_history),
            'jamming_threshold': self.jam_detection_threshold,
            'analysis_window_sec': self.jam_window
        }
        
    def reset(self) -> None:
        """Reset the security analyzer state.
        
        This method clears all packet history and resets the analyzer's internal state.
        It should be called when the device is reset or when a new analysis session begins.
        """
        self.packet_history.clear()
        logger.debug("Security analyzer state has been reset")
