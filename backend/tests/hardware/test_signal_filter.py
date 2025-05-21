"""Unit tests for the SignalFilter class."""
import time

from hardware.packet import Packet
from hardware.signal_filter import FREQ_BANDS, MIN_RSSI_DBM, SignalFilter


def test_signal_filter_initialization():
    """Test that the signal filter initializes correctly."""
    filter = SignalFilter()
    assert filter is not None

def test_is_within_freq_bands():
    """Test frequency band filtering."""
    filter = SignalFilter()
    
    # Test frequencies within bands
    for lower, upper in FREQ_BANDS:
        # Test lower bound
        assert filter.is_within_freq_bands(lower)
        # Test upper bound
        assert filter.is_within_freq_bands(upper)
        # Test middle
        if upper > lower:
            assert filter.is_within_freq_bands((lower + upper) / 2)
    
    # Test frequencies outside bands
    assert not filter.is_within_freq_bands(200.0)   # Below all bands
    assert not filter.is_within_freq_bands(1000.0)  # Above all bands
    assert not filter.is_within_freq_bands(400.0)   # Between 315 and 433 bands

def test_is_strong_signal():
    """Test signal strength filtering."""
    filter = SignalFilter()
    
    # Test signals above and at threshold
    assert filter.is_strong_signal(MIN_RSSI_DBM)      # At threshold
    assert filter.is_strong_signal(MIN_RSSI_DBM + 10) # Above threshold
    
    # Test signals below threshold
    assert not filter.is_strong_signal(MIN_RSSI_DBM - 1)  # Just below
    assert not filter.is_strong_signal(-100)              # Far below

def test_duplicate_detection():
    """Test duplicate packet detection."""
    filter = SignalFilter()
    packet1 = Packet(rssi=-65, freq=433.92, payload=b'test1')
    packet2 = Packet(rssi=-65, freq=433.92, payload=b'test1')  # Same as packet1
    packet3 = Packet(rssi=-65, freq=433.92, payload=b'test2')  # Different payload
    
    # First packet should not be a duplicate
    assert not filter.is_duplicate(packet1.signature, packet1.timestamp)
    
    # Same packet should be detected as duplicate
    assert filter.is_duplicate(packet2.signature, packet2.timestamp)
    
    # Different packet should not be a duplicate
    assert not filter.is_duplicate(packet3.signature, packet3.timestamp)

def test_duplicate_window():
    """Test that duplicates are only detected within the time window."""
    filter = SignalFilter()
    signature = "test_signature"
    now = time.time()
    
    # Add a packet just inside the window
    assert not filter.is_duplicate(signature, now - 4.9)  # Inside 5s window
    
    # Same packet just outside the window should not be a duplicate
    assert not filter.is_duplicate(signature, now + 0.2)  # Outside window

def test_should_accept():
    """Test the combined filtering logic."""
    filter = SignalFilter()
    
    # Create test packets
    good_packet = Packet(rssi=-65, freq=433.92, payload=b'good')
    weak_packet = Packet(rssi=-100, freq=433.92, payload=b'weak')
    wrong_freq = Packet(rssi=-65, freq=200.0, payload=b'wrong_freq')
    
    # Test good packet
    assert filter.should_accept(good_packet)
    
    # Test weak signal
    assert not filter.should_accept(weak_packet)
    
    # Test wrong frequency
    assert not filter.should_accept(wrong_freq)
    
    # Test duplicate
    assert filter.should_accept(good_packet)  # First time - should accept
    assert not filter.should_accept(good_packet)  # Second time - duplicate

def test_get_signal_metrics():
    """Test retrieval of signal metrics."""
    filter = SignalFilter()
    metrics = filter.get_signal_metrics()
    
    assert isinstance(metrics, dict)
    assert metrics['min_rssi'] == MIN_RSSI_DBM
    assert metrics['monitored_bands'] == FREQ_BANDS
    assert metrics['duplicate_window_sec'] > 0
    assert metrics['max_duplicates'] > 0
    
    # Test that active_signals updates
    packet = Packet(rssi=-65, freq=433.92, payload=b'test')
    filter.should_accept(packet)
    updated_metrics = filter.get_signal_metrics()
    assert updated_metrics['active_signals'] == 1
