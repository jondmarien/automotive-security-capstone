"""
security_analyzer.py

Implements SecurityAnalyzer for analyzing packets and reporting threats.
"""

import time
from .threat_levels import ThreatLevel
from .security_report import SecurityReport


class SecurityAnalyzer:
    """
    Analyzes packets for potential security threats.
    Implements replay, jamming, and brute force detection.
    """

    def __init__(self):
        self.jam_detection_threshold = 100  # Packets/sec to detect jamming
        self.brute_force_threshold = 5  # Similar packets for brute force
        self.packet_history = []
        self.jam_window = 1.0  # Seconds for jamming analysis
        self.brute_force_window = 10.0  # Seconds for brute force
        self.suspicious_patterns = [
            b"REPLAY_ATTACK",
            b"JAMMER",
            b"INJECT",
            b"BRUTE",
            b"OLD_",
        ]

    def _is_replay_attack(self, packet):
        current_time = time.time()
        for p in self.packet_history:
            # Defensive: skip packets with missing timestamp, rssi, or freq
            if (
                getattr(p, "timestamp", None) is None
                or getattr(p, "rssi", None) is None
                or getattr(p, "freq", None) is None
            ):
                continue
            time_diff = current_time - p.timestamp
            if time_diff >= 5.0:
                continue
            if (
                getattr(p, "payload", None) == getattr(packet, "payload", None)
                and getattr(p, "freq", None) == getattr(packet, "freq", None)
                and abs(getattr(p, "rssi", 0) - getattr(packet, "rssi", 0)) > 3
            ):
                return True
        return False

    def _is_jamming_attack(self):
        current_time = time.time()
        recent_packets = [
            p
            for p in self.packet_history
            if current_time - getattr(p, "timestamp", current_time) < self.jam_window
        ]
        return len(recent_packets) > self.jam_detection_threshold

    def _is_brute_force_attack(self, packet):
        current_time = time.time()
        if hasattr(packet, "payload"):
            payload = (
                packet.payload
                if isinstance(packet.payload, bytes)
                else str(packet.payload).encode("utf-8", errors="replace")
            )
            for pattern in self.suspicious_patterns:
                if pattern in payload:
                    similar_packets = [
                        p
                        for p in self.packet_history
                        if current_time - getattr(p, "timestamp", current_time)
                        < self.brute_force_window
                        and pattern
                        in (
                            p.payload
                            if isinstance(p.payload, bytes)
                            else str(p.payload).encode("utf-8", errors="replace")
                        )
                    ]
                    if len(similar_packets) >= self.brute_force_threshold:
                        return True
        return False

    def analyze_packet(self, packet):
        current_time = time.time()
        packet.timestamp = current_time
        # Defensive: filter out packets with missing timestamp, rssi, or freq
        self.packet_history = [
            p
            for p in self.packet_history
            if getattr(p, "timestamp", None) is not None
            and getattr(p, "rssi", None) is not None
            and getattr(p, "freq", None) is not None
            and current_time - getattr(p, "timestamp", current_time) < self.jam_window
        ]
        self.packet_history.append(packet)
        if self._is_replay_attack(packet):
            return SecurityReport(
                packet, ThreatLevel.MALICIOUS, "Potential replay attack detected"
            )
        if self._is_jamming_attack():
            return SecurityReport(
                packet, ThreatLevel.MALICIOUS, "Potential jamming attack detected"
            )
        if self._is_brute_force_attack(packet):
            return SecurityReport(
                packet, ThreatLevel.MALICIOUS, "Potential brute force attack detected"
            )
        return SecurityReport(packet, ThreatLevel.BENIGN, "No threats detected")
