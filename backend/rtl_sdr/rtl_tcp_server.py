import subprocess
import socket
import threading
import json
import time
import asyncio
from datetime import datetime
import os

class RTLTCPServerManager:
    def __init__(self, frequency=434000000, sample_rate=2048000, gain=25):
        self.frequency = frequency
        self.sample_rate = sample_rate
        self.gain = gain
        self.rtl_process = None
        self.tcp_port = 1234
        self.pico_server_port = 8888
        self.connected_picos = []

    def start_rtl_tcp_server(self):
        """Start rtl_tcp server with RTL-SDR V4 (using rtl_tcp.exe from rtl_sdr_bin)"""
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
        """Start TCP server for Pico connections"""
        server = await asyncio.start_server(
            self.handle_pico_connection,
            '0.0.0.0',
            self.pico_server_port
        )
        print(f"Pico communication server listening on port {self.pico_server_port}")
        async with server:
            await server.serve_forever()

    async def handle_pico_connection(self, reader, writer):
        """Handle incoming Pico connections"""
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
        """Send JSON data to Pico"""
        try:
            json_data = json.dumps(data) + '\n'
            writer.write(json_data.encode())
            await writer.drain()
        except Exception as e:
            print(f"Failed to send to Pico: {e}")

    async def broadcast_to_picos(self, data):
        """Broadcast data to all connected Picos"""
        if not self.connected_picos:
            return
        for pico in self.connected_picos[:]:
            try:
                await self.send_to_pico(pico['writer'], data)
            except Exception as e:
                print(f"Failed to broadcast to {pico['address']}: {e}")
                self.connected_picos.remove(pico)

    async def handle_pico_command(self, message, writer):
        # Placeholder for handling commands from Pico
        print(f"Received command from Pico: {message}") 