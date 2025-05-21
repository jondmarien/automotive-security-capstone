"""Unit tests for the EdgeDAO class."""
import pytest

from hardware.dao import EdgeDAO


@pytest.mark.asyncio
async def test_dao_initialization():
    """Test DAO initialization with custom limits."""
    # Test with custom limits
    dao = EdgeDAO(max_packets=100, max_alerts=50)
    assert dao.max_packets == 100
    assert dao.max_alerts == 50
    
    # Test default limits
    default_dao = EdgeDAO()
    assert default_dao.max_packets > 0
    assert default_dao.max_alerts > 0

@pytest.mark.asyncio
async def test_save_and_retrieve_packets():
    """Test saving and retrieving packets."""
    dao = EdgeDAO(max_packets=10)
    
    # Save some packets
    for i in range(5):
        packet = {
            'rssi': -60 - i,
            'freq': 433.92,
            'payload': f'test_{i}'.encode(),
            'timestamp': i
        }
        await dao.save_packet(packet)
    
    # Retrieve packets
    packets = await dao.get_recent_packets()
    assert len(packets) == 5
    
    # Check packet order (most recent first)
    for i, p in enumerate(reversed(packets)):
        assert p['rssi'] == -60 - i
        assert p['payload'] == f'test_{i}'.encode()

@pytest.mark.asyncio
async def test_save_and_retrieve_alerts():
    """Test saving and retrieving alerts."""
    dao = EdgeDAO(max_alerts=5)
    
    # Save some alerts
    for i in range(3):
        alert = {
            'level': 'WARNING',
            'message': f'Test alert {i}',
            'timestamp': i
        }
        await dao.save_alert(alert)
    
    # Retrieve alerts
    alerts = await dao.get_recent_alerts()
    assert len(alerts) == 3
    
    # Check alert order (most recent first)
    for i, a in enumerate(reversed(alerts)):
        assert a['message'] == f'Test alert {i}'

@pytest.mark.asyncio
async def test_storage_limits():
    """Test that storage limits are enforced."""
    # Test packet limit
    packet_dao = EdgeDAO(max_packets=3)
    for i in range(5):
        await packet_dao.save_packet({'data': f'packet_{i}'})
    
    packets = await packet_dao.get_recent_packets(10)
    assert len(packets) == 3  # Should be limited to max_packets
    assert packets[0]['data'] == 'packet_4'  # Most recent first
    assert packets[-1]['data'] == 'packet_2'  # Oldest of the kept packets
    
    # Test alert limit
    alert_dao = EdgeDAO(max_alerts=2)
    for i in range(4):
        await alert_dao.save_alert({'message': f'alert_{i}'})
    
    alerts = await alert_dao.get_recent_alerts(10)
    assert len(alerts) == 2  # Should be limited to max_alerts
    assert alerts[0]['message'] == 'alert_3'  # Most recent first
    assert alerts[-1]['message'] == 'alert_2'  # Oldest of the kept alerts

@pytest.mark.asyncio
async def test_metrics():
    """Test retrieval of storage metrics."""
    dao = EdgeDAO(max_packets=10, max_alerts=5)
    
    # Initial metrics
    metrics = await dao.get_metrics()
    assert metrics['packets']['count'] == 0
    assert metrics['packets']['max'] == 10
    assert metrics['alerts']['count'] == 0
    assert metrics['alerts']['max'] == 5
    
    # Add some data
    for i in range(3):
        await dao.save_packet({'test': 'packet'})
        await dao.save_alert({'test': 'alert'})
    
    # Check updated metrics
    updated_metrics = await dao.get_metrics()
    assert updated_metrics['packets']['count'] == 3
    assert updated_metrics['packets']['total'] == 3
    assert updated_metrics['alerts']['count'] == 3

@pytest.mark.asyncio
async def test_clear_all():
    """Test clearing all stored data."""
    dao = EdgeDAO()
    
    # Add some data
    await dao.save_packet({'test': 'packet'})
    await dao.save_alert({'test': 'alert'})
    
    # Verify data exists
    assert len(await dao.get_recent_packets()) == 1
    assert len(await dao.get_recent_alerts()) == 1
    
    # Clear all data
    await dao.clear_all()
    
    # Verify data is cleared
    assert len(await dao.get_recent_packets()) == 0
    assert len(await dao.get_recent_alerts()) == 0
    
    # Verify metrics are reset
    metrics = await dao.get_metrics()
    assert metrics['packets']['count'] == 0
    assert metrics['alerts']['count'] == 0
