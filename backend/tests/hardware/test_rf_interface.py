"""Tests for the RF interface implementation."""
import asyncio

import pytest

from hardware.drivers.mock.rf import MockRFInterface
from hardware.models.models import RFConfig


class TestMockRFInterface:
    """Test suite for the RF interface."""

    @pytest.fixture
    def rf_config(self) -> RFConfig:
        """Create a test RF configuration."""
        return RFConfig(
            frequency=868e6,  # 868 MHz
            power=14,       # Transmit power in dBm
            data_rate=50000, # 50 kbps
            modulation='2-FSK',
            bandwidth=125e3, # 125 kHz
            devitation=25e3, # 25 kHz
            sync_word=b'\x12',
            crc_enabled=True,
            auto_ack=False
        )

    @pytest.fixture
    def rf_interface(self) -> MockRFInterface:
        """Create an instance of the mock RF interface."""
        return MockRFInterface()

    @pytest.mark.asyncio
    async def test_initialize(self, rf_interface, rf_config):
        """Test initializing the RF interface."""
        assert not rf_interface.is_initialized
        await rf_interface.initialize(rf_config)
        assert rf_interface.is_initialized

    @pytest.mark.asyncio
    async def test_initialize_twice_fails(self, rf_interface, rf_config):
        """Test that initializing twice raises an error."""
        await rf_interface.initialize(rf_config)
        with pytest.raises(Exception) as exc_info:  # Catch the specific exception type
            await rf_interface.initialize(rf_config)
        assert "RF interface already initialized" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_packet(self, rf_interface, rf_config):
        """Test sending a packet."""
        await rf_interface.initialize(rf_config)
        result = await rf_interface.send_packet(b"test")
        assert result is True

    @pytest.mark.asyncio
    async def test_send_packet_not_initialized(self, rf_interface):
        """Test sending a packet when not initialized raises an error."""
        with pytest.raises(Exception) as exc_info:  # Catch the specific exception type
            await rf_interface.send_packet(b"test")
        assert "RF interface not initialized" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_receive_packets(self, rf_interface, rf_config):
        """Test receiving packets."""
        received = []
        
        async def callback(data: bytes) -> None:
            received.append(data)
        
        await rf_interface.initialize(rf_config)
        await rf_interface.start_receiving(callback)
        
        # Send some test packets
        test_packets = [b"test1", b"test2", b"test3"]
        for packet in test_packets:
            await rf_interface.send_packet(packet)
            await asyncio.sleep(0.1)  # Allow time for processing
        
        await rf_interface.stop_receiving()
        
        # Verify we received all packets
        assert len(received) == len(test_packets)
        for sent, recv in zip(test_packets, received):
            assert sent == recv

    @pytest.mark.asyncio
    async def test_get_signal_metrics(self, rf_interface, rf_config):
        """Test getting signal metrics."""
        await rf_interface.initialize(rf_config)
        metrics = rf_interface.get_signal_metrics()
        
        assert isinstance(metrics, dict)
        assert "rssi" in metrics
        assert "snr" in metrics
        assert "frequency" in metrics
        assert "channel" in metrics
