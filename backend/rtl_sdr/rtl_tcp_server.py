"""
rtl_tcp_server.py

Manages the RTL-SDR V4 TCP server for RF signal capture and Pico client communication.
Starts and supervises rtl_tcp (for IQ data), and provides a TCP server for Pico clients
to connect and receive configuration and detection events.

Designed for use in the Automotive Security Capstone POC project.

Example:
    manager = RTLTCPServerManager()
    manager.start_rtl_tcp_server()
    asyncio.run(manager.start_pico_communication_server())
"""
import subprocess
import json
import time
import asyncio
from datetime import datetime
import os

class RTLTCPServerManager:
    """
    Manages RTL-SDR V4 TCP server and Pico communication server.

    Attributes:
        frequency (int): RF frequency for RTL-SDR (Hz).
        sample_rate (int): Sample rate for RTL-SDR (Hz).
        gain (int): RF gain for RTL-SDR (dB).
        rtl_process (subprocess.Popen): Subprocess for rtl_tcp.
        tcp_port (int): Port for rtl_tcp server (default 1234).
        pico_server_port (int): Port for Pico TCP server (default 8888).
        connected_picos (list): List of currently connected Pico clients.

    Example:
        manager = RTLTCPServerManager()
        manager.start_rtl_tcp_server()
        asyncio.run(manager.start_pico_communication_server())
    """
    def __init__(self, frequency=434000000, sample_rate=2048000, gain=25):
        """
        Initializes the RTLTCPServerManager instance.

        Args:
            frequency (int): RF frequency for RTL-SDR (Hz). Defaults to 434000000.
            sample_rate (int): Sample rate for RTL-SDR (Hz). Defaults to 2048000.
            gain (int): RF gain for RTL-SDR (dB). Defaults to 25.
        """
        self.frequency = frequency
        self.sample_rate = sample_rate
        self.gain = gain
        self.rtl_process = None
        self.tcp_port = 1234
        self.pico_server_port = 8888
        self.connected_picos = []

    def start_rtl_tcp_server(self):
        """
        Start rtl_tcp server with RTL-SDR V4 (using rtl_tcp.exe from rtl_sdr_bin).
        Returns True if started successfully, False otherwise.

        Example:
            manager = RTLTCPServerManager()
            manager.start_rtl_tcp_server()
        """
        # Use the rtl_tcp.exe from the rtl_sdr_bin directory (one level up)
        rtl_tcp_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'rtl_sdr_bin', 'rtl_tcp.exe'))
        cmd = [
            rtl_tcp_path,
            '-a', '0.0.0.0',
            '-p', str(self.tcp_port),
            '-f', str(self.frequency),
            '-s', str(self.sample_rate),
            '-g', str(self.gain),
            '-n', '1'
        ]
        print(f"Starting RTL-SDR V4 TCP server: {' '.join(cmd)}")
        try:
            self.rtl_process = subprocess.Popen(cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE)
            time.sleep(3)
            if self.rtl_process.poll() is None:
                print(f"RTL-TCP server running on port {self.tcp_port}")
                return True
            else:
                stderr = self.rtl_process.stderr.read().decode() # type: ignore
                print(f"RTL-TCP server failed to start: {stderr}")
                return False
        except Exception as e:
            print(f"Failed to start RTL-TCP server: {e}")
            return False

    async def start_pico_communication_server(self):
        """
        Start TCP server for Pico connections.
        Listens for incoming Pico clients and handles their communication.

        Example:
            await manager.start_pico_communication_server()
        """
        server = await asyncio.start_server(
            self.handle_pico_connection,
            '0.0.0.0',
            self.pico_server_port
        )
        print(f"Pico communication server listening on port {self.pico_server_port}")
        async with server:
            await server.serve_forever()

    async def handle_pico_connection(self, reader, writer):
        """
        Handle incoming Pico client connections.
        Sends initial config, processes commands, and maintains heartbeat.

        Args:
            reader (StreamReader): Asyncio stream reader from Pico.
            writer (StreamWriter): Asyncio stream writer to Pico.
        """
        addr = writer.get_extra_info('peername')
        print(f"Pico connected from {addr}")
        self.connected_picos.append({
            'reader': reader,
            'writer': writer,
            'address': addr,
            'connected_at': datetime.now()
        })
        try:
            config = {
                'type': 'config',
                'rtl_frequency': self.frequency,
                'sample_rate': self.sample_rate,
                'server_info': {
                    'version': '1.0.0',
                    'capabilities': ['rf_monitoring', 'nfc_detection']
                }
            }
            await self.send_to_pico(writer, config)
            while True:
                try:
                    data = await asyncio.wait_for(reader.read(1024), timeout=30.0)
                    if not data:
                        break
                    try:
                        message = json.loads(data.decode().strip())
                        await self.handle_pico_command(message, writer)
                    except json.JSONDecodeError:
                        print(f"Invalid JSON from Pico {addr}")
                except asyncio.TimeoutError:
                    await self.send_to_pico(writer, {'type': 'heartbeat'})
        except Exception as e:
            print(f"Pico connection error from {addr}: {e}")
        finally:
            print(f"Pico {addr} disconnected")
            self.connected_picos = [p for p in self.connected_picos if p['writer'] != writer]
            writer.close()

    async def send_to_pico(self, writer, data):
        """
        Send JSON data to a Pico client.

        Args:
            writer (StreamWriter): Asyncio stream writer to Pico.
            data (dict): Data to send (will be JSON-encoded).
        """
        try:
            json_data = json.dumps(data) + '\n'
            writer.write(json_data.encode())
            await writer.drain()
        except Exception as e:
            print(f"Failed to send to Pico: {e}")

    async def broadcast_to_picos(self, data):
        """
        Broadcast data to all currently connected Pico clients.

        Args:
            data (dict): Data to send (will be JSON-encoded).
        """
        if not self.connected_picos:
            return
        for pico in self.connected_picos[:]:
            try:
                await self.send_to_pico(pico['writer'], data)
            except Exception as e:
                print(f"Failed to broadcast to {pico['address']}: {e}")
                self.connected_picos.remove(pico)

    async def handle_pico_command(self, message, writer):
        """
        Handle commands received from Pico client.
        Extend this function to support custom commands (e.g., status, config, etc).

        Args:
            message (dict): JSON-decoded command from Pico.
            writer (StreamWriter): Asyncio stream writer to Pico.
        """
        print(f"Received command from Pico: {message}")