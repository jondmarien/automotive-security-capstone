"""Unit tests for the report logic and security analysis."""
import time
from unittest.mock import patch

from hardware.core.packet import Packet
from hardware.utils.reporter import SecurityAnalyzer, SecurityReport, ThreatLevel


def test_security_report_creation():
    """Test creation of security reports."""
    packet = Packet(rssi=-65, freq=433.92, payload=b'test')
    
    # Test with different threat levels
    for level in ThreatLevel:
        report = SecurityReport(
            packet=packet,
            threat_level=level,
            reason=f"Test {level.name}"
        )
        
        assert report.packet == packet
        assert report.threat_level == level
        assert report.reason == f"Test {level.name}"
        assert isinstance(report.timestamp, float)
        assert report.timestamp <= time.time()

def test_security_report_serialization():
    """Test serialization of security reports."""
    packet = Packet(rssi=-65, freq=433.92, payload=b'test')
    report = SecurityReport(
        packet=packet,
        threat_level=ThreatLevel.MALICIOUS,
        reason="Test serialization"
    )
    
    data = report.to_dict()
    
    assert isinstance(data, dict)
    assert data['threat_level'] == 'MALICIOUS'
    assert data['reason'] == 'Test serialization'
    assert isinstance(data['timestamp'], float)
    assert 'packet' in data
    assert data['packet']['rssi'] == -65
    assert data['packet']['freq'] == 433.92
    assert data['packet']['payload'] == '74657374'  # hex of 'test'


def test_security_analyzer_initialization():
    """Test initialization of the security analyzer."""
    analyzer = SecurityAnalyzer()
    assert analyzer is not None
    assert analyzer.jam_detection_threshold > 0


def test_replay_attack_detection():
    """Test detection of replay attacks."""
    analyzer = SecurityAnalyzer()
    
    # Create two identical packets with different RSSI (indicates potential replay)
    packet1 = Packet(rssi=-65, freq=433.92, payload=b'replay_test')
    packet2 = Packet(rssi=-70, freq=433.92, payload=b'replay_test')
    
    # First packet should be benign
    report1 = analyzer.analyze_packet(packet1)
    assert report1.threat_level == ThreatLevel.BENIGN
    
    # Second packet with same payload but different RSSI should be detected as malicious
    report2 = analyzer.analyze_packet(packet2)
    assert report2.threat_level == ThreatLevel.MALICIOUS
    assert "replay" in report2.reason.lower()


def test_jamming_attack_detection():
    """Test detection of jamming attacks."""
    # Create analyzer with low threshold for testing
    analyzer = SecurityAnalyzer()
    analyzer.jam_detection_threshold = 5  # Very low threshold for testing
    
    # Send packets rapidly to trigger jamming detection
    for i in range(6):  # One more than threshold
        packet = Packet(rssi=-65, freq=433.92, payload=f'test_{i}'.encode())
        report = analyzer.analyze_packet(packet)
        
        # Only the last one should trigger jamming detection
        if i < 5:
            assert report.threat_level == ThreatLevel.BENIGN
        else:
            assert report.threat_level == ThreatLevel.MALICIOUS
            assert "jamming" in report.reason.lower()


def test_benign_traffic():
    """Test that normal traffic is classified as benign."""
    analyzer = SecurityAnalyzer()
    
    # Send several different packets
    for i in range(10):
        packet = Packet(
            rssi=-60 - i,  # Vary RSSI slightly
            freq=433.92,
            payload=f'test_{i}'.encode()
        )
        report = analyzer.analyze_packet(packet)
        assert report.threat_level == ThreatLevel.BENIGN


def test_get_metrics():
    """Test retrieval of security metrics."""
    analyzer = SecurityAnalyzer()
    
    # Initial metrics
    metrics = analyzer.get_metrics()
    assert metrics['total_packets_analyzed'] == 0
    assert metrics['packets_per_second'] == 0
    
    # Analyze some packets
    for i in range(10):
        packet = Packet(rssi=-65, freq=433.92, payload=f'test_{i}'.encode())
        analyzer.analyze_packet(packet)
    
    # Check updated metrics
    updated_metrics = analyzer.get_metrics()
    assert updated_metrics['total_packets_analyzed'] == 10
    assert updated_metrics['packets_per_second'] > 0


def test_packet_history_management():
    """Test that packet history is properly managed."""
    analyzer = SecurityAnalyzer()
    analyzer.jam_window = 1.0  # 1 second window for testing
    
    # Send a packet
    packet1 = Packet(rssi=-65, freq=433.92, payload=b'test1')
    analyzer.analyze_packet(packet1)
    
    # Send another packet just before the window closes
    with patch('time.time', return_value=time.time() + 0.9):
        packet2 = Packet(rssi=-65, freq=433.92, payload=b'test2')
        analyzer.analyze_packet(packet2)
    
    # Should have both packets in history
    assert len(analyzer.packet_history) == 2
    
    # Move time forward past the window
    with patch('time.time', return_value=time.time() + 2.0):
        # This should trigger cleanup of old packets
        analyzer.analyze_packet(Packet(rssi=-65, freq=433.92, payload=b'test3'))
        
        # Only the most recent packet should remain
        assert len(analyzer.packet_history) == 1
