"""
Test suite for RTL TCP server module.

Tests comprehensive RTL-SDR TCP server functionality including:
- RTL-SDR V4 TCP server management
- Pico client communication
- JSON message handling
- Connection management
- Error handling
"""

import pytest
import asyncio
import json
import subprocess
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
import os

from rtl_sdr.rtl_tcp_server import RTLTCPServerManager, log


class TestRTLTCPServerManager:
    """Test cases for RTLTCPServerManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = RTLTCPServerManager(
            frequency=433920000,
            sample_rate=2048000,
            gain=30
        )

    def test_init_default_values(self):
        """Test RTLTCPServerManager initialization with default values."""
        manager = RTLTCPServerManager()
        
        assert manager.frequency == 434000000
        assert manager.sample_rate == 2048000
        assert manager.gain == 25
        assert manager.rtl_process is None
        assert manager.tcp_port == 1234
        assert manager.pico_server_port == 8888
        assert manager.connected_picos == []

    def test_init_custom_values(self):
        """Test RTLTCPServerManager initialization with custom values."""
        assert self.manager.frequency == 433920000
        assert self.manager.sample_rate == 2048000
        assert self.manager.gain == 30
        assert self.manager.rtl_process is None
        assert self.manager.tcp_port == 1234
        assert self.manager.pico_server_port == 8888
        assert self.manager.connected_picos == []

    @patch('rtl_sdr.rtl_tcp_server.subprocess.Popen')
    @patch('rtl_sdr.rtl_tcp_server.time.sleep')
    @patch('rtl_sdr.rtl_tcp_server.os.path.abspath')
    @patch('rtl_sdr.rtl_tcp_server.os.path.join')
    @patch('rtl_sdr.rtl_tcp_server.os.path.dirname')
    def test_start_rtl_tcp_server_success(self, mock_dirname, mock_join, mock_abspath, mock_sleep, mock_popen):
        """Test successful RTL TCP server start."""
        # Mock file path resolution
        mock_dirname.return_value = "/test/path"
        mock_join.return_value = "/test/path/../rtl_sdr_bin/rtl_tcp.exe"
        mock_abspath.return_value = "/test/rtl_sdr_bin/rtl_tcp.exe"
        
        # Mock successful process
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Process is running
        mock_popen.return_value = mock_process
        
        result = self.manager.start_rtl_tcp_server()
        
        assert result is True
        assert self.manager.rtl_process == mock_process
        
        # Verify command construction
        expected_cmd = [
            "/test/rtl_sdr_bin/rtl_tcp.exe",
            "-a", "0.0.0.0",
            "-p", "1234",
            "-f", "433920000",
            "-s", "2048000",
            "-g", "30",
            "-n", "1"
        ]
        mock_popen.assert_called_once_with(
            expected_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        mock_sleep.assert_called_once_with(3)

    @patch('rtl_sdr.rtl_tcp_server.subprocess.Popen')
    @patch('rtl_sdr.rtl_tcp_server.time.sleep')
    @patch('rtl_sdr.rtl_tcp_server.os.path.abspath')
    @patch('rtl_sdr.rtl_tcp_server.os.path.join')
    @patch('rtl_sdr.rtl_tcp_server.os.path.dirname')
    def test_start_rtl_tcp_server_process_failed(self, mock_dirname, mock_join, mock_abspath, mock_sleep, mock_popen):
        """Test RTL TCP server start when process fails."""
        # Mock file path resolution
        mock_dirname.return_value = "/test/path"
        mock_join.return_value = "/test/path/../rtl_sdr_bin/rtl_tcp.exe"
        mock_abspath.return_value = "/test/rtl_sdr_bin/rtl_tcp.exe"
        
        # Mock failed process
        mock_process = MagicMock()
        mock_process.poll.return_value = 1  # Process exited with error
        mock_stderr = MagicMock()
        mock_stderr.read.return_value.decode.return_value = "RTL-SDR not found"
        mock_process.stderr = mock_stderr
        mock_popen.return_value = mock_process
        
        result = self.manager.start_rtl_tcp_server()
        
        assert result is False
        assert self.manager.rtl_process == mock_process

    @patch('rtl_sdr.rtl_tcp_server.subprocess.Popen')
    @patch('rtl_sdr.rtl_tcp_server.os.path.abspath')
    @patch('rtl_sdr.rtl_tcp_server.os.path.join')
    @patch('rtl_sdr.rtl_tcp_server.os.path.dirname')
    def test_start_rtl_tcp_server_exception(self, mock_dirname, mock_join, mock_abspath, mock_popen):
        """Test RTL TCP server start when exception occurs."""
        # Mock file path resolution
        mock_dirname.return_value = "/test/path"
        mock_join.return_value = "/test/path/../rtl_sdr_bin/rtl_tcp.exe"
        mock_abspath.return_value = "/test/rtl_sdr_bin/rtl_tcp.exe"
        
        # Mock exception
        mock_popen.side_effect = FileNotFoundError("rtl_tcp.exe not found")
        
        result = self.manager.start_rtl_tcp_server()
        
        assert result is False
        assert self.manager.rtl_process is None

    @pytest.mark.asyncio
    @patch('rtl_sdr.rtl_tcp_server.asyncio.start_server')
    async def test_start_pico_communication_server(self, mock_start_server):
        """Test starting Pico communication server."""
        mock_server = AsyncMock()
        mock_server.__aenter__ = AsyncMock(return_value=mock_server)
        mock_server.__aexit__ = AsyncMock(return_value=None)
        mock_server.serve_forever = AsyncMock()
        mock_start_server.return_value = mock_server
        
        # Run the server start (but cancel it quickly to avoid infinite loop)
        task = asyncio.create_task(self.manager.start_pico_communication_server())
        await asyncio.sleep(0.1)  # Let it start
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            pass
        
        mock_start_server.assert_called_once_with(
            self.manager.handle_pico_connection,
            "0.0.0.0",
            8888
        )

    @pytest.mark.asyncio
    async def test_handle_pico_connection_success(self):
        """Test successful Pico connection handling."""
        # Mock reader and writer
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        mock_writer.get_extra_info.return_value = ("192.168.1.100", 12345)
        
        # Mock data reading
        mock_reader.read.side_effect = [
            b'{"type": "status", "message": "ready"}\n',
            b''  # EOF to end the loop
        ]
        
        # Mock send_to_pico and handle_pico_command as regular async functions
        async def mock_send_to_pico(writer, data):
            pass
        
        async def mock_handle_command(message, writer):
            pass
        
        with patch.object(self.manager, 'send_to_pico', side_effect=mock_send_to_pico) as mock_send:
            with patch.object(self.manager, 'handle_pico_command', side_effect=mock_handle_command) as mock_handle:
                await self.manager.handle_pico_connection(mock_reader, mock_writer)
        
        # Verify initial config was sent
        assert mock_send.call_count >= 1
        
        # Verify command was handled
        mock_handle.assert_called_once()
        
        # Verify writer was closed
        mock_writer.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_pico_connection_timeout(self):
        """Test Pico connection with timeout."""
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        mock_writer.get_extra_info.return_value = ("192.168.1.100", 12345)
        
        # Mock timeout on first read, then EOF on second read to exit loop
        mock_reader.read.side_effect = [asyncio.TimeoutError(), b'']
        
        async def mock_send_to_pico(writer, data):
            pass
        
        with patch.object(self.manager, 'send_to_pico', side_effect=mock_send_to_pico) as mock_send:
            await self.manager.handle_pico_connection(mock_reader, mock_writer)
        
        # Verify heartbeat was sent after timeout
        heartbeat_calls = [call for call in mock_send.call_args_list if len(call[0]) > 1 and call[0][1].get("type") == "heartbeat"]
        assert len(heartbeat_calls) >= 1
        
        mock_writer.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_pico_connection_invalid_json(self):
        """Test Pico connection with invalid JSON."""
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        mock_writer.get_extra_info.return_value = ("192.168.1.100", 12345)
        
        # Mock invalid JSON data
        mock_reader.read.side_effect = [
            b'invalid json data\n',
            b''  # EOF
        ]
        
        async def mock_send_to_pico(writer, data):
            pass
        
        async def mock_handle_command(message, writer):
            pass
        
        with patch.object(self.manager, 'send_to_pico', side_effect=mock_send_to_pico):
            with patch.object(self.manager, 'handle_pico_command', side_effect=mock_handle_command) as mock_handle:
                await self.manager.handle_pico_connection(mock_reader, mock_writer)
        
        # Command handler should not be called for invalid JSON
        mock_handle.assert_not_called()
        mock_writer.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_pico_connection_exception(self):
        """Test Pico connection with exception."""
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        mock_writer.get_extra_info.return_value = ("192.168.1.100", 12345)
        
        # Mock exception during processing
        mock_reader.read.side_effect = Exception("Connection error")
        
        async def mock_send_to_pico(writer, data):
            pass
        
        with patch.object(self.manager, 'send_to_pico', side_effect=mock_send_to_pico):
            await self.manager.handle_pico_connection(mock_reader, mock_writer)
        
        mock_writer.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_to_pico_success(self):
        """Test successful sending to Pico."""
        mock_writer = AsyncMock()
        
        data = {"type": "test", "message": "hello"}
        await self.manager.send_to_pico(mock_writer, data)
        
        expected_json = json.dumps(data) + "\n"
        mock_writer.write.assert_called_once_with(expected_json.encode())
        mock_writer.drain.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_to_pico_exception(self):
        """Test sending to Pico with exception."""
        mock_writer = AsyncMock()
        mock_writer.write.side_effect = Exception("Write error")
        
        data = {"type": "test", "message": "hello"}
        # Should not raise exception
        await self.manager.send_to_pico(mock_writer, data)
        
        mock_writer.write.assert_called_once()

    @pytest.mark.asyncio
    async def test_broadcast_to_picos_no_connections(self):
        """Test broadcasting when no Picos are connected."""
        data = {"type": "broadcast", "message": "test"}
        
        # Should not raise exception
        await self.manager.broadcast_to_picos(data)
        
        assert len(self.manager.connected_picos) == 0

    @pytest.mark.asyncio
    async def test_broadcast_to_picos_success(self):
        """Test successful broadcasting to connected Picos."""
        # Add mock connected Picos
        mock_writer1 = AsyncMock()
        mock_writer2 = AsyncMock()
        
        self.manager.connected_picos = [
            {
                "reader": AsyncMock(),
                "writer": mock_writer1,
                "address": ("192.168.1.100", 12345),
                "connected_at": datetime.now()
            },
            {
                "reader": AsyncMock(),
                "writer": mock_writer2,
                "address": ("192.168.1.101", 12346),
                "connected_at": datetime.now()
            }
        ]
        
        data = {"type": "broadcast", "message": "test"}
        
        with patch.object(self.manager, 'send_to_pico', new_callable=AsyncMock) as mock_send:
            await self.manager.broadcast_to_picos(data)
        
        assert mock_send.call_count == 2
        mock_send.assert_any_call(mock_writer1, data)
        mock_send.assert_any_call(mock_writer2, data)

    @pytest.mark.asyncio
    async def test_broadcast_to_picos_with_failure(self):
        """Test broadcasting with one Pico failing."""
        # Add mock connected Picos
        mock_writer1 = AsyncMock()
        mock_writer2 = AsyncMock()
        
        pico1 = {
            "reader": AsyncMock(),
            "writer": mock_writer1,
            "address": ("192.168.1.100", 12345),
            "connected_at": datetime.now()
        }
        pico2 = {
            "reader": AsyncMock(),
            "writer": mock_writer2,
            "address": ("192.168.1.101", 12346),
            "connected_at": datetime.now()
        }
        
        self.manager.connected_picos = [pico1, pico2]
        
        data = {"type": "broadcast", "message": "test"}
        
        # Mock send_to_pico to fail for first Pico
        async def mock_send_side_effect(writer, data):
            if writer == mock_writer1:
                raise Exception("Send failed")
        
        with patch.object(self.manager, 'send_to_pico', side_effect=mock_send_side_effect):
            await self.manager.broadcast_to_picos(data)
        
        # Failed Pico should be removed
        assert len(self.manager.connected_picos) == 1
        assert self.manager.connected_picos[0] == pico2

    @pytest.mark.asyncio
    async def test_handle_pico_command(self):
        """Test handling Pico commands."""
        mock_writer = AsyncMock()
        message = {"type": "status", "message": "ready"}
        
        # This is a placeholder method in the original code
        await self.manager.handle_pico_command(message, mock_writer)
        
        # Should not raise any exceptions
        assert True

    def test_log_function(self):
        """Test log function."""
        with patch('builtins.print') as mock_print:
            log("Test message")
            
            mock_print.assert_called_once()
            call_args = mock_print.call_args[0][0]
            assert "Test message" in call_args
            # Should contain timestamp format
            assert "[" in call_args and "]" in call_args

    @pytest.mark.asyncio
    async def test_connection_management(self):
        """Test connection management during handle_pico_connection."""
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        mock_writer.get_extra_info.return_value = ("192.168.1.100", 12345)
        
        # Mock data reading to end quickly
        mock_reader.read.return_value = b''  # EOF immediately
        
        initial_count = len(self.manager.connected_picos)
        
        with patch.object(self.manager, 'send_to_pico', new_callable=AsyncMock):
            await self.manager.handle_pico_connection(mock_reader, mock_writer)
        
        # Connection should be cleaned up
        assert len(self.manager.connected_picos) == initial_count

    @pytest.mark.asyncio
    async def test_pico_connection_data_buffering(self):
        """Test data buffering in Pico connection handling."""
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        mock_writer.get_extra_info.return_value = ("192.168.1.100", 12345)
        
        # Mock partial data reading (incomplete JSON)
        mock_reader.read.side_effect = [
            b'{"type": "status"',  # Partial JSON
            b', "message": "ready"}\n',  # Complete JSON
            b''  # EOF
        ]
        
        with patch.object(self.manager, 'send_to_pico', new_callable=AsyncMock):
            with patch.object(self.manager, 'handle_pico_command', new_callable=AsyncMock) as mock_handle:
                await self.manager.handle_pico_connection(mock_reader, mock_writer)
        
        # Command should be handled once the complete JSON is received
        mock_handle.assert_called_once()
        call_args = mock_handle.call_args[0][0]
        assert call_args["type"] == "status"
        assert call_args["message"] == "ready"

    @pytest.mark.asyncio
    async def test_multiple_json_messages_in_buffer(self):
        """Test handling multiple JSON messages in single read."""
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        mock_writer.get_extra_info.return_value = ("192.168.1.100", 12345)
        
        # Mock multiple JSON messages in one read
        mock_reader.read.side_effect = [
            b'{"type": "status", "message": "ready"}\n{"type": "ping"}\n',
            b''  # EOF
        ]
        
        with patch.object(self.manager, 'send_to_pico', new_callable=AsyncMock):
            with patch.object(self.manager, 'handle_pico_command', new_callable=AsyncMock) as mock_handle:
                await self.manager.handle_pico_connection(mock_reader, mock_writer)
        
        # Both commands should be handled
        assert mock_handle.call_count == 2
        
        # Verify the commands
        call1_args = mock_handle.call_args_list[0][0][0]
        call2_args = mock_handle.call_args_list[1][0][0]
        
        assert call1_args["type"] == "status"
        assert call2_args["type"] == "ping"

    def test_manager_attributes_after_init(self):
        """Test that manager has all required attributes after initialization."""
        required_attrs = [
            'frequency', 'sample_rate', 'gain', 'rtl_process',
            'tcp_port', 'pico_server_port', 'connected_picos'
        ]
        
        for attr in required_attrs:
            assert hasattr(self.manager, attr)

    @pytest.mark.asyncio
    async def test_config_message_structure(self):
        """Test that config message has correct structure."""
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        mock_writer.get_extra_info.return_value = ("192.168.1.100", 12345)
        mock_reader.read.return_value = b''  # EOF immediately
        
        with patch.object(self.manager, 'send_to_pico', new_callable=AsyncMock) as mock_send:
            await self.manager.handle_pico_connection(mock_reader, mock_writer)
        
        # Get the config message (first call)
        config_call = mock_send.call_args_list[0]
        config = config_call[0][1]
        
        assert config["type"] == "config"
        assert config["rtl_frequency"] == self.manager.frequency
        assert config["sample_rate"] == self.manager.sample_rate
        assert "server_info" in config
        assert "version" in config["server_info"]
        assert "capabilities" in config["server_info"]
        assert isinstance(config["server_info"]["capabilities"], list)
