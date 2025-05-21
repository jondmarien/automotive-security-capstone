"""Unit tests for the EdgeDevice class."""
import asyncio  # noqa: F401
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from hardware.device import EdgeDevice
from hardware.packet import Packet
from hardware.report_logic import ThreatLevel


@pytest.fixture
def edge_device():
    """Fixture that provides a test EdgeDevice instance."""
    return EdgeDevice(device_id="test_device")


@pytest.mark.asyncio
async def test_device_initialization(edge_device):
    """Test device initialization and properties."""
    assert edge_device.device_id == "test_device"
    assert edge_device.running is False
    assert edge_device.packet_count == 0
    assert edge_device.alert_count == 0


@pytest.mark.asyncio
async def test_start_stop(edge_device):
    """Test device start and stop functionality."""
    # Start the device
    await edge_device.start()
    assert edge_device.running is True
    
    # Try to start again (should be idempotent)
    await edge_device.start()
    assert edge_device.running is True
    
    # Stop the device
    await edge_device.stop()
    assert edge_device.running is False
    
    # Try to stop again (should be idempotent)
    await edge_device.stop()
    assert edge_device.running is False


@pytest.mark.asyncio
async def test_process_packet_normal(edge_device):
    """Test processing a normal (non-threat) packet."""
    await edge_device.start()
    
    # Process a normal packet
    result = await edge_device.process_packet(
        rssi=-65,
        freq=433.92,
        payload=b'normal_packet'
    )
    
    assert result is not None
    assert result['threat_detected'] is False
    assert edge_device.packet_count == 1
    assert edge_device.alert_count == 0
    
    # Verify packet was stored
    metrics = await edge_device.dao.get_metrics()
    assert metrics['packets']['count'] == 1
    assert metrics['alerts']['count'] == 0


@pytest.mark.asyncio
async def test_process_packet_replay_attack(edge_device):
    """Test detection of a replay attack."""
    await edge_device.start()
    
    # First packet (normal)
    result1 = await edge_device.process_packet(
        rssi=-65,
        freq=433.92,
        payload=b'replay_attack'
    )
    assert result1['threat_detected'] is False
    
    # Same payload, different RSSI (potential replay attack)
    result2 = await edge_device.process_packet(
        rssi=-70,  # Different RSSI
        freq=433.92,
        payload=b'replay_attack'  # Same payload
    )
    
    assert result2['threat_detected'] is True
    assert 'replay' in result2['reason'].lower()
    assert edge_device.packet_count == 2
    assert edge_device.alert_count == 1
    
    # Verify alert was stored
    alerts = await edge_device.dao.get_recent_alerts()
    assert len(alerts) == 1
    assert 'replay' in alerts[0]['reason'].lower()


@pytest.mark.asyncio
async def test_process_packet_jamming_attack(edge_device):
    """Test detection of a jamming attack."""
    await edge_device.start()
    
    # Lower the jamming threshold for testing
    edge_device.security_analyzer.jam_detection_threshold = 3
    
    # Send packets rapidly to trigger jamming detection
    for i in range(4):  # One more than threshold
        result = await edge_device.process_packet(
            rssi=-65,
            freq=433.92,
            payload=f'jamming_test_{i}'.encode()
        )
        
        # Only the last one should trigger jamming detection
        if i < 3:
            assert result['threat_detected'] is False
        else:
            assert result['threat_detected'] is True
            assert 'jamming' in result['reason'].lower()
    
    assert edge_device.alert_count == 1


@pytest.mark.asyncio
async def test_reset(edge_device):
    """Test device reset functionality."""
    await edge_device.start()
    
    # Add some data
    await edge_device.process_packet(rssi=-65, freq=433.92, payload=b'test')
    
    # Verify data exists
    metrics = await edge_device.dao.get_metrics()
    assert metrics['packets']['count'] == 1
    
    # Reset the device
    await edge_device.reset()
    
    # Verify state was reset
    assert edge_device.packet_count == 0
    assert edge_device.alert_count == 0
    
    # Verify storage was cleared
    metrics = await edge_device.dao.get_metrics()
    assert metrics['packets']['count'] == 0
    assert metrics['alerts']['count'] == 0


@pytest.mark.asyncio
async def test_get_status(edge_device):
    """Test device status reporting."""
    await edge_device.start()
    
    # Process a packet
    await edge_device.process_packet(rssi=-65, freq=433.92, payload=b'status_test')
    
    # Get status
    status = await edge_device.get_status()
    
    # Verify status contains expected fields
    assert status['device_id'] == 'test_device'
    assert status['status'] == 'running'
    assert status['packets_processed'] == 1
    assert status['alerts_generated'] == 0
    
    # Verify sub-metrics
    assert 'storage_metrics' in status
    assert status['storage_metrics']['packets']['count'] == 1
    assert 'signal_metrics' in status
    assert 'security_metrics' in status
    assert 'timestamp' in status


@pytest.mark.asyncio
async def test_packet_processing_when_stopped(edge_device):
    """Test that packets are not processed when device is stopped."""
    # Don't start the device
    
    # Try to process a packet
    result = await edge_device.process_packet(
        rssi=-65,
        freq=433.92,
        payload=b'should_not_process'
    )
    
    assert result is None
    assert edge_device.packet_count == 0
    
    # Verify packet was not stored
    metrics = await edge_device.dao.get_metrics()
    assert metrics['packets']['count'] == 0
