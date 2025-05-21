"""Unit tests for the Packet class."""
import time

import pytest

from ..packet import Packet


def test_packet_creation():
    """Test basic packet creation."""
    payload = b'test_payload'
    packet = Packet(rssi=-65, freq=433.92, payload=payload)
    
    assert packet.rssi == -65
    assert packet.freq == 433.92
    assert packet.payload == payload
    assert isinstance(packet.timestamp, float)
    assert packet.timestamp <= time.time()

def test_packet_signature():
    """Test packet signature generation."""
    payload1 = b'test_payload'
    payload2 = b'different_payload'
    
    packet1 = Packet(rssi=-65, freq=433.92, payload=payload1)
    packet2 = Packet(rssi=-65, freq=433.92, payload=payload1)
    packet3 = Packet(rssi=-70, freq=433.92, payload=payload1)  # Different RSSI
    packet4 = Packet(rssi=-65, freq=868.0, payload=payload1)    # Different frequency
    packet5 = Packet(rssi=-65, freq=433.92, payload=payload2)   # Different payload
    
    # Same packets should have same signature
    assert packet1.signature == packet2.signature
    
    # Different packets should have different signatures
    assert packet1.signature != packet3.signature
    assert packet1.signature != packet4.signature
    assert packet1.signature != packet5.signature

def test_packet_serialization():
    """Test packet serialization to/from dictionary."""
    original = Packet(rssi=-65, freq=433.92, payload=b'test_payload')
    data = original.to_dict()
    
    assert isinstance(data, dict)
    assert data['rssi'] == -65
    assert data['freq'] == 433.92
    assert data['payload'] == '746573745f7061796c6f6164'  # hex of 'test_payload'
    assert isinstance(data['timestamp'], float)
    
    # Test deserialization
    restored = Packet.from_dict(data)
    assert restored.rssi == original.rssi
    assert restored.freq == original.freq
    assert restored.payload == original.payload
    assert restored.timestamp == original.timestamp

@pytest.mark.parametrize("rssi,freq,payload,expected_valid", [
    (-65, 433.92, b'test', True),         # Valid
    (-100, 433.92, b'test', True),         # Low RSSI but still valid
    (10, 315.0, b'test', True),           # Different frequency
    (None, 433.92, b'test', False),        # Missing RSSI
    (-65, None, b'test', False),           # Missing frequency
    (-65, 433.92, None, False),            # Missing payload
    (-65, 433.92, b'', False),             # Empty payload
])
def test_packet_validation(rssi, freq, payload, expected_valid):
    """Test packet validation with various inputs."""
    try:
        packet = Packet(
            rssi=rssi,
            freq=freq,
            payload=payload
        )
        assert expected_valid
        assert isinstance(packet, Packet)
    except (TypeError, ValueError):
        assert not expected_valid
