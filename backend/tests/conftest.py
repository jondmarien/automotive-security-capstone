"""Test configuration and fixtures for the test suite."""

import asyncio
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.db.mongodb import MongoDB
from app.main import app
from hardware.models.models import RFConfig


@pytest.fixture(scope="module")
def test_client():
    """
    Create a test client for the FastAPI application.
    """
    with TestClient(app) as client:
        yield client

@pytest.fixture(autouse=True)
async def setup_and_teardown():
    """
    Setup and teardown for tests.
    """
    # Setup: Connect to MongoDB
    await MongoDB.connect_db()
    
    yield  # This is where the testing happens
    
    # Teardown: Close MongoDB connection
    await MongoDB.close_db()


@pytest.fixture
def rf_config() -> RFConfig:
    """Create a test RF configuration."""
    return RFConfig(
        frequency=868e6,  # 868 MHz
        tx_power=14,     # dBm
        bandwidth=125e3,  # 125 kHz
        spreading_factor=7,
        coding_rate=5,
        sync_word=0x12,
        implicit_header=False,
        rx_timeout=5.0,
        tx_timeout=5.0,
    )


@pytest.fixture
def mock_rf_interface():
    """Create a mock RF interface for testing."""
    with patch('hardware.interfaces.rf.RFInterface') as mock_rf:
        # Configure the mock
        mock_rf.return_value.is_initialized = False
        mock_rf.return_value.is_receiving = False
        
        # Set up async methods
        async def mock_initialize(config):
            mock_rf.return_value.is_initialized = True
            
        async def mock_start_receiving(callback):
            mock_rf.return_value.is_receiving = True
            mock_rf.return_value._receive_callback = callback
            
        async def mock_stop_receiving():
            mock_rf.return_value.is_receiving = False
            mock_rf.return_value._receive_callback = None
            
        async def mock_send_packet(data, timeout=5.0):
            return True
            
        # Assign the mock methods
        mock_rf.return_value.initialize = mock_initialize
        mock_rf.return_value.start_receiving = mock_start_receiving
        mock_rf.return_value.stop_receiving = mock_stop_receiving
        mock_rf.return_value.send_packet = mock_send_packet
        mock_rf.return_value.get_signal_metrics.return_value = {
            'rssi': -75.5,
            'snr': 12.3,
            'frequency': 868e6,
            'channel': 0
        }
        
        yield mock_rf.return_value
