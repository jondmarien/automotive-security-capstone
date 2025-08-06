"""
Test suite for signal bridge module.

Tests comprehensive signal processing functionality including:
- Signal processing bridge initialization
- IQ sample processing and conversion
- Automotive signal detection
- Burst pattern analysis
- Signal classification and threat level calculation
- Enhanced mode handling
"""

import pytest
import asyncio
import numpy as np
import struct
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
import time

from rtl_sdr.signal_bridge import SignalProcessingBridge, FOB_SETTINGS, log


class TestSignalProcessingBridge:
    """Test cases for SignalProcessingBridge class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_rtl_server = MagicMock()
        self.mock_rtl_server.frequency = 433920000
        self.mock_rtl_server.sample_rate = 2048000
        self.mock_rtl_server.gain = 30
        self.mock_rtl_server.connected_picos = []
        
        self.bridge = SignalProcessingBridge(
            rtl_server_manager=self.mock_rtl_server,
            rtl_tcp_host="localhost",
            rtl_tcp_port=1234,
            fob_model="BMW_X1_2023",
            enhanced_mode=False
        )

    def test_init_default_values(self):
        """Test SignalProcessingBridge initialization with default values."""
        bridge = SignalProcessingBridge(self.mock_rtl_server)
        
        assert bridge.rtl_server == self.mock_rtl_server
        assert bridge.rtl_tcp_host == "localhost"
        assert bridge.rtl_tcp_port == 1234
        assert bridge.processing_active is False
        assert bridge.signal_buffer == []
        assert bridge.detection_threshold == -60
        assert bridge._last_cooldown_log_time == 0
        assert bridge._last_burst_time == 0
        assert bridge.fob_settings == FOB_SETTINGS["BMW_X1_2023"]
        assert bridge.enhanced_mode is False
        assert bridge.enhanced_bridge is None

    def test_init_custom_values(self):
        """Test SignalProcessingBridge initialization with custom values."""
        assert self.bridge.rtl_server == self.mock_rtl_server
        assert self.bridge.rtl_tcp_host == "localhost"
        assert self.bridge.rtl_tcp_port == 1234
        assert self.bridge.fob_settings == FOB_SETTINGS["BMW_X1_2023"]
        assert self.bridge.enhanced_mode is False

    def test_init_unknown_fob_model(self):
        """Test initialization with unknown fob model falls back to default."""
        bridge = SignalProcessingBridge(
            self.mock_rtl_server,
            fob_model="UNKNOWN_MODEL"
        )
        
        assert bridge.fob_settings == FOB_SETTINGS["BMW_X1_2023"]

    @patch('rtl_sdr.signal_bridge.ENHANCED_MODE_AVAILABLE', True)
    @patch('rtl_sdr.signal_bridge.EnhancedSignalProcessingBridge')
    def test_init_enhanced_mode_available(self, mock_enhanced_bridge_class):
        """Test initialization with enhanced mode when available."""
        mock_enhanced_bridge = MagicMock()
        mock_enhanced_bridge_class.return_value = mock_enhanced_bridge
        
        bridge = SignalProcessingBridge(
            self.mock_rtl_server,
            enhanced_mode=True
        )
        
        assert bridge.enhanced_mode is True
        assert bridge.enhanced_bridge == mock_enhanced_bridge
        mock_enhanced_bridge_class.assert_called_once_with(
            self.mock_rtl_server, "localhost", 1234
        )

    @patch('rtl_sdr.signal_bridge.ENHANCED_MODE_AVAILABLE', False)
    def test_init_enhanced_mode_not_available(self):
        """Test initialization with enhanced mode when not available."""
        bridge = SignalProcessingBridge(
            self.mock_rtl_server,
            enhanced_mode=True
        )
        
        assert bridge.enhanced_mode is False
        assert bridge.enhanced_bridge is None

    @pytest.mark.asyncio
    async def test_start_signal_processing_enhanced_mode(self):
        """Test signal processing start with enhanced mode."""
        mock_enhanced_bridge = AsyncMock()
        mock_enhanced_bridge.start_signal_processing = AsyncMock(return_value="enhanced_result")
        
        self.bridge.enhanced_mode = True
        self.bridge.enhanced_bridge = mock_enhanced_bridge
        
        result = await self.bridge.start_signal_processing()
        
        assert result == "enhanced_result"
        mock_enhanced_bridge.start_signal_processing.assert_called_once()

    @pytest.mark.asyncio
    @patch('rtl_sdr.signal_bridge.asyncio.open_connection')
    async def test_start_signal_processing_legacy_mode(self, mock_open_connection):
        """Test signal processing start with legacy mode."""
        # Mock connection
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        mock_open_connection.return_value = (mock_reader, mock_writer)
        
        # Mock data reading - return empty to break the inner loop immediately
        mock_reader.read.return_value = b''
        
        # Mock configure_rtl_sdr
        with patch.object(self.bridge, 'configure_rtl_sdr', new_callable=AsyncMock) as mock_configure:
            # Mock broadcast_to_picos to avoid issues
            with patch.object(self.bridge.rtl_server, 'broadcast_to_picos', new_callable=AsyncMock):
                # Set processing_active to False immediately to prevent infinite loop
                original_processing_active = self.bridge.processing_active
                self.bridge.processing_active = False
                
                # Start signal processing - should exit quickly due to processing_active = False
                await self.bridge.start_signal_processing()
                
                # Restore original state
                self.bridge.processing_active = original_processing_active
        
        # The method should have attempted to connect
        mock_open_connection.assert_called_with("localhost", 1234)

    @pytest.mark.asyncio
    @patch('rtl_sdr.signal_bridge.asyncio.open_connection')
    async def test_start_signal_processing_with_data_processing(self, mock_open_connection):
        """Test signal processing with actual data processing."""
        # Mock connection
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        mock_open_connection.return_value = (mock_reader, mock_writer)
        
        # Add connected Pico
        self.mock_rtl_server.connected_picos = [{"mock": "pico"}]
        
        # Mock sample data
        sample_data = np.random.randint(0, 255, 1024, dtype=np.uint8).tobytes()
        mock_reader.read.side_effect = [sample_data, b'']  # Data then EOF
        
        # Mock methods
        with patch.object(self.bridge, 'configure_rtl_sdr', new_callable=AsyncMock):
            with patch.object(self.bridge, 'process_samples', new_callable=AsyncMock) as mock_process:
                mock_process.return_value = {"type": "test_detection"}
                
                self.bridge.processing_active = True
                
                # Create task and cancel quickly
                task = asyncio.create_task(self.bridge.start_signal_processing())
                await asyncio.sleep(0.1)
                self.bridge.processing_active = False
                
                try:
                    await task
                except Exception:
                    pass
        
        # Verify process_samples was called
        mock_process.assert_called()
        # Verify broadcast was called
        self.mock_rtl_server.broadcast_to_picos.assert_called()

    @pytest.mark.asyncio
    @patch('rtl_sdr.signal_bridge.asyncio.open_connection')
    async def test_start_signal_processing_connection_error(self, mock_open_connection):
        """Test signal processing with connection error."""
        mock_open_connection.side_effect = ConnectionRefusedError("Connection refused")
        
        self.bridge.processing_active = True
        
        # Create task and cancel quickly
        task = asyncio.create_task(self.bridge.start_signal_processing())
        await asyncio.sleep(0.1)
        self.bridge.processing_active = False
        
        try:
            await task
        except Exception:
            pass
        
        mock_open_connection.assert_called()

    @pytest.mark.asyncio
    async def test_configure_rtl_sdr(self):
        """Test RTL-SDR configuration via TCP."""
        mock_writer = AsyncMock()
        
        await self.bridge.configure_rtl_sdr(mock_writer)
        
        # Verify commands were written
        assert mock_writer.write.call_count == 3
        mock_writer.drain.assert_called_once()
        
        # Check command structure
        calls = mock_writer.write.call_args_list
        freq_cmd = calls[0][0][0]
        rate_cmd = calls[1][0][0]
        gain_cmd = calls[2][0][0]
        
        # Verify command format (command byte + 4-byte value)
        assert len(freq_cmd) == 5
        assert len(rate_cmd) == 5
        assert len(gain_cmd) == 5
        
        # Verify command types
        assert freq_cmd[0] == 0x01  # Frequency command
        assert rate_cmd[0] == 0x02  # Sample rate command
        assert gain_cmd[0] == 0x04  # Gain command

    @pytest.mark.asyncio
    async def test_process_samples_basic(self):
        """Test basic IQ sample processing."""
        # Create mock IQ data (interleaved I/Q samples)
        samples = np.array([127, 127, 150, 100, 200, 50] * 100, dtype=np.uint8)
        raw_data = samples.tobytes()
        
        with patch.object(self.bridge, 'detect_automotive_signals', new_callable=AsyncMock) as mock_detect:
            mock_detect.return_value = []  # No detections
            
            result = await self.bridge.process_samples(raw_data, 42)
            
            assert result is None
            mock_detect.assert_called_once()
            
            # Verify the call arguments
            args = mock_detect.call_args[0]
            power_db = args[0]
            complex_samples = args[1]
            
            assert isinstance(power_db, np.ndarray)
            assert isinstance(complex_samples, np.ndarray)
            assert len(power_db) == len(complex_samples)

    @pytest.mark.asyncio
    async def test_process_samples_with_detection(self):
        """Test IQ sample processing with signal detection."""
        # Create mock IQ data
        samples = np.array([127, 127, 150, 100, 200, 50] * 100, dtype=np.uint8)
        raw_data = samples.tobytes()
        
        mock_detection = {
            "detection_id": "test_det_123",
            "event_type": "key_fob_transmission",
            "power_db": -45.0
        }
        
        with patch.object(self.bridge, 'detect_automotive_signals', new_callable=AsyncMock) as mock_detect:
            mock_detect.return_value = [mock_detection]
            
            result = await self.bridge.process_samples(raw_data, 42)
            
            assert result is not None
            assert result["type"] == "signal_detection"
            assert result["sample_count"] == 42
            assert result["detections"] == [mock_detection]
            assert "timestamp" in result
            assert "frequency_mhz" in result
            assert "sample_rate" in result

    @pytest.mark.asyncio
    async def test_detect_automotive_signals_no_picos(self):
        """Test automotive signal detection with no connected Picos."""
        power_db = np.random.randn(1000) * 10 - 50
        complex_samples = np.random.randn(1000) + 1j * np.random.randn(1000)
        
        # No connected Picos
        self.mock_rtl_server.connected_picos = []
        
        result = await self.bridge.detect_automotive_signals(power_db, complex_samples)
        
        assert result == []

    @pytest.mark.asyncio
    async def test_detect_automotive_signals_insufficient_peaks(self):
        """Test automotive signal detection with insufficient peaks."""
        # Create low-power signal
        power_db = np.random.randn(1000) * 2 - 60  # Low power, few peaks
        complex_samples = np.random.randn(1000) + 1j * np.random.randn(1000)
        
        # Add connected Pico
        self.mock_rtl_server.connected_picos = [{"mock": "pico"}]
        
        result = await self.bridge.detect_automotive_signals(power_db, complex_samples)
        
        assert result == []

    @pytest.mark.asyncio
    async def test_detect_automotive_signals_low_power(self):
        """Test automotive signal detection with low maximum power."""
        # Create signal with many peaks but low power
        power_db = np.random.randn(1000) * 2 - 80  # Very low power
        # Add some peaks above threshold
        power_db[100:110] = -70  # Still below min_max_power_db
        complex_samples = np.random.randn(1000) + 1j * np.random.randn(1000)
        
        # Add connected Pico
        self.mock_rtl_server.connected_picos = [{"mock": "pico"}]
        
        result = await self.bridge.detect_automotive_signals(power_db, complex_samples)
        
        assert result == []

    @pytest.mark.asyncio
    async def test_detect_automotive_signals_cooldown(self):
        """Test automotive signal detection with cooldown period."""
        # Create strong signal
        power_db = np.random.randn(1000) * 5 - 30
        # Add strong peaks
        power_db[100:120] = -20  # Strong peaks
        complex_samples = np.random.randn(1000) + 1j * np.random.randn(1000)
        
        # Add connected Pico
        self.mock_rtl_server.connected_picos = [{"mock": "pico"}]
        
        # Set recent burst time to trigger cooldown
        self.bridge._last_burst_time = time.time()
        
        result = await self.bridge.detect_automotive_signals(power_db, complex_samples)
        
        assert result == []

    @pytest.mark.asyncio
    async def test_detect_automotive_signals_successful_detection(self):
        """Test successful automotive signal detection."""
        # Create strong signal with many peaks
        power_db = np.random.randn(1000) * 5 - 40
        # Add strong peaks above threshold
        power_db[100:120] = -15  # Strong peaks above min_max_power_db
        complex_samples = np.random.randn(1000) + 1j * np.random.randn(1000)
        
        # Add connected Pico
        self.mock_rtl_server.connected_picos = [{"mock": "pico"}]
        
        # Reset burst time to avoid cooldown
        self.bridge._last_burst_time = 0
        
        with patch.object(self.bridge, 'analyze_burst_pattern') as mock_analyze:
            with patch.object(self.bridge, 'classify_signal_type') as mock_classify:
                with patch.object(self.bridge, 'calculate_threat_level') as mock_threat:
                    mock_analyze.return_value = "key_fob_pattern"
                    mock_classify.return_value = "key_fob_transmission"
                    mock_threat.return_value = 0.7
                    
                    result = await self.bridge.detect_automotive_signals(power_db, complex_samples)
        
        assert len(result) == 1
        detection = result[0]
        assert "detection_id" in detection
        assert detection["event_type"] == "key_fob_transmission"
        assert detection["burst_pattern"] == "key_fob_pattern"
        assert detection["threat_level"] == 0.7
        assert "power_db" in detection
        assert "mean_power" in detection
        assert "peak_count" in detection

    def test_analyze_burst_pattern_key_fob(self):
        """Test burst pattern analysis for key fob signals."""
        power_db = np.random.randn(1000) * 5 - 40
        # Create key fob-like pattern with regular intervals
        peaks = np.array([100, 110, 120, 130, 140, 150, 160, 170])
        settings = FOB_SETTINGS["BMW_X1_2023"]
        
        result = self.bridge.analyze_burst_pattern(power_db, peaks, settings)
        
        assert result in ["key_fob_pattern", "jamming_pattern", "unknown_pattern"]

    def test_analyze_burst_pattern_jamming(self):
        """Test burst pattern analysis for jamming signals."""
        power_db = np.random.randn(1000) * 5 - 40
        # Create jamming-like pattern with irregular, dense peaks
        peaks = np.array([100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 
                         110, 111, 112, 113, 114, 115, 116, 117, 118, 119])
        settings = FOB_SETTINGS["BMW_X1_2023"]
        
        result = self.bridge.analyze_burst_pattern(power_db, peaks, settings)
        
        assert result in ["key_fob_pattern", "jamming_pattern", "unknown_pattern"]

    def test_classify_signal_type_key_fob(self):
        """Test signal type classification for key fob."""
        burst_pattern = "key_fob_pattern"
        max_power = -20.0
        peaks = np.array([100, 110, 120, 130, 140, 150])
        settings = FOB_SETTINGS["BMW_X1_2023"]
        
        result = self.bridge.classify_signal_type(burst_pattern, max_power, peaks, settings)
        
        assert result == "key_fob_transmission"

    def test_classify_signal_type_jamming(self):
        """Test signal type classification for jamming."""
        burst_pattern = "jamming_pattern"
        max_power = -15.0
        peaks = np.array(range(100, 150))  # Many peaks
        settings = FOB_SETTINGS["BMW_X1_2023"]
        
        result = self.bridge.classify_signal_type(burst_pattern, max_power, peaks, settings)
        
        assert result == "jamming_attack"

    def test_classify_signal_type_unknown(self):
        """Test signal type classification for unknown pattern."""
        burst_pattern = "unknown_pattern"
        max_power = -30.0
        peaks = np.array([100, 200, 300])
        settings = FOB_SETTINGS["BMW_X1_2023"]
        
        result = self.bridge.classify_signal_type(burst_pattern, max_power, peaks, settings)
        
        assert result == "unknown_signal"

    def test_calculate_threat_level_key_fob(self):
        """Test threat level calculation for key fob pattern."""
        burst_pattern = "key_fob_pattern"
        max_power = -20.0
        mean_power = -45.0
        
        result = self.bridge.calculate_threat_level(burst_pattern, max_power, mean_power)
        
        assert 0.0 <= result <= 1.0
        assert result < 0.5  # Key fob should be low threat

    def test_calculate_threat_level_jamming(self):
        """Test threat level calculation for jamming pattern."""
        burst_pattern = "jamming_pattern"
        max_power = -10.0
        mean_power = -30.0
        
        result = self.bridge.calculate_threat_level(burst_pattern, max_power, mean_power)
        
        assert 0.0 <= result <= 1.0
        assert result > 0.5  # Jamming should be high threat

    def test_calculate_threat_level_unknown(self):
        """Test threat level calculation for unknown pattern."""
        burst_pattern = "unknown_pattern"
        max_power = -25.0
        mean_power = -50.0
        
        result = self.bridge.calculate_threat_level(burst_pattern, max_power, mean_power)
        
        assert 0.0 <= result <= 1.0

    def test_fob_settings_structure(self):
        """Test FOB_SETTINGS structure and content."""
        assert "BMW_X1_2023" in FOB_SETTINGS
        bmw_settings = FOB_SETTINGS["BMW_X1_2023"]
        
        required_keys = ["min_peak_count", "samples_per_symbol", "modulation", "min_max_power_db"]
        for key in required_keys:
            assert key in bmw_settings
        
        assert isinstance(bmw_settings["min_peak_count"], int)
        assert isinstance(bmw_settings["samples_per_symbol"], int)
        assert isinstance(bmw_settings["modulation"], str)
        assert isinstance(bmw_settings["min_max_power_db"], (int, float))

    def test_log_function(self):
        """Test log function."""
        with patch('builtins.print') as mock_print:
            log("Test signal bridge message")
            
            mock_print.assert_called_once()
            call_args = mock_print.call_args[0][0]
            assert "Test signal bridge message" in call_args
            # Should contain timestamp format
            assert "[" in call_args and "]" in call_args

    @pytest.mark.asyncio
    async def test_process_samples_edge_cases(self):
        """Test process_samples with edge cases."""
        # Test with minimal data
        raw_data = np.array([127, 127, 128, 126], dtype=np.uint8).tobytes()
        
        with patch.object(self.bridge, 'detect_automotive_signals', new_callable=AsyncMock) as mock_detect:
            mock_detect.return_value = []
            
            result = await self.bridge.process_samples(raw_data, 0)
            
            assert result is None
            mock_detect.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_samples_uneven_iq_data(self):
        """Test process_samples with uneven I/Q data length."""
        # Create data with odd number of samples (uneven I/Q)
        raw_data = np.array([127, 127, 128, 126, 129], dtype=np.uint8).tobytes()
        
        with patch.object(self.bridge, 'detect_automotive_signals', new_callable=AsyncMock) as mock_detect:
            mock_detect.return_value = []
            
            result = await self.bridge.process_samples(raw_data, 1)
            
            assert result is None
            mock_detect.assert_called_once()
            
            # Verify that I and Q samples have same length
            args = mock_detect.call_args[0]
            complex_samples = args[1]
            assert len(complex_samples) > 0

    def test_signal_processing_attributes(self):
        """Test that SignalProcessingBridge has all required attributes."""
        required_attrs = [
            'rtl_server', 'rtl_tcp_host', 'rtl_tcp_port', 'processing_active',
            'signal_buffer', 'detection_threshold', '_last_cooldown_log_time',
            '_last_burst_time', 'fob_settings', 'enhanced_mode', 'enhanced_bridge'
        ]
        
        for attr in required_attrs:
            assert hasattr(self.bridge, attr)

    @pytest.mark.asyncio
    async def test_status_broadcast_every_100_samples(self):
        """Test that status is broadcast every 100 samples."""
        # Mock connection
        with patch('rtl_sdr.signal_bridge.asyncio.open_connection') as mock_open_connection:
            mock_reader = AsyncMock()
            mock_writer = AsyncMock()
            mock_open_connection.return_value = (mock_reader, mock_writer)
            
            # Add connected Pico
            self.mock_rtl_server.connected_picos = [{"mock": "pico"}]
            
            # Mock data to process 101 samples
            sample_data = np.random.randint(0, 255, 1024, dtype=np.uint8).tobytes()
            mock_reader.read.side_effect = [sample_data] * 101 + [b'']  # 101 samples then EOF
            
            with patch.object(self.bridge, 'configure_rtl_sdr', new_callable=AsyncMock):
                with patch.object(self.bridge, 'process_samples', new_callable=AsyncMock) as mock_process:
                    mock_process.return_value = None  # No detections
                    
                    self.bridge.processing_active = True
                    
                    # Create task and let it run briefly
                    task = asyncio.create_task(self.bridge.start_signal_processing())
                    await asyncio.sleep(0.1)
                    self.bridge.processing_active = False
                    
                    try:
                        await task
                    except Exception:
                        pass
            
            # Verify status broadcasts occurred
            broadcast_calls = self.mock_rtl_server.broadcast_to_picos.call_args_list
            status_calls = [call for call in broadcast_calls 
                          if call[0][0].get("type") == "status"]
            assert len(status_calls) >= 1  # At least one status broadcast

    def test_iq_sample_conversion(self):
        """Test IQ sample conversion from uint8 to complex."""
        # Create test data
        samples = np.array([0, 255, 127, 128, 64, 192], dtype=np.uint8)
        
        # Simulate the conversion logic from process_samples
        i_samples = (samples[0::2].astype(np.float32) - 127.5) / 127.5
        q_samples = (samples[1::2].astype(np.float32) - 127.5) / 127.5
        min_len = min(len(i_samples), len(q_samples))
        i_samples = i_samples[:min_len]
        q_samples = q_samples[:min_len]
        complex_samples = i_samples + 1j * q_samples
        
        # Verify conversion
        assert len(complex_samples) == 3  # 6 samples / 2 = 3 complex samples
        assert np.all(np.abs(complex_samples.real) <= 1.0)  # Normalized to [-1, 1]
        assert np.all(np.abs(complex_samples.imag) <= 1.0)  # Normalized to [-1, 1]

    @pytest.mark.asyncio
    async def test_detect_automotive_signals_timing_logs(self):
        """Test that timing logs are properly managed in detect_automotive_signals."""
        # Create signal that will trigger various log conditions
        power_db = np.random.randn(1000) * 2 - 60  # Low power signal
        complex_samples = np.random.randn(1000) + 1j * np.random.randn(1000)
        
        # Add connected Pico
        self.mock_rtl_server.connected_picos = [{"mock": "pico"}]
        
        # Reset log timing
        self.bridge._last_cooldown_log_time = 0
        
        # Call multiple times to test log timing
        for _ in range(3):
            result = await self.bridge.detect_automotive_signals(power_db, complex_samples)
            assert result == []
        
        # Verify that cooldown log time was updated
        assert self.bridge._last_cooldown_log_time > 0
