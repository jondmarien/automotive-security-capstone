"""
startup_server.py

Entry point for launching the Automotive Security POC backend server. Starts the RTL-TCP server,
signal processing bridge, and Pico communication server. Provides monitoring and graceful shutdown.

Example usage:
    python -m rtl_sdr.startup_server
"""
import asyncio
import sys
import signal
from rtl_sdr.rtl_tcp_server import RTLTCPServerManager
from rtl_sdr.signal_bridge import SignalProcessingBridge

class AutomotiveSecurityServer:
    """
    Orchestrates the backend server for the Automotive Security POC.
    Starts RTL-TCP server, signal processing, and Pico event server.

    Example:
        server = AutomotiveSecurityServer()
        asyncio.run(server.start_server())
    """
    def __init__(self):
        """
        Initialize the AutomotiveSecurityServer with RTL manager and signal bridge.
        """
        self.rtl_manager = RTLTCPServerManager()
        self.signal_bridge = SignalProcessingBridge(self.rtl_manager)
        self.running = True

    async def start_server(self):
        """
        Start all backend services: RTL-TCP server, Pico server, and signal processing.
        Handles startup, task management, and graceful shutdown.

        Example:
            await server.start_server()
        """
        print("🚗 Automotive Security Server - POC Mode")
        print("=" * 45)
        print("Starting RTL-SDR V4 TCP server...")
        if not self.rtl_manager.start_rtl_tcp_server():
            print("❌ Failed to start RTL-TCP server")
            return False
        print("✅ RTL-TCP server started")
        tasks = [
            asyncio.create_task(self.rtl_manager.start_pico_communication_server()),
            asyncio.create_task(self.signal_bridge.start_signal_processing()),
            asyncio.create_task(self.monitor_system())
        ]
        print("🟢 Automotive Security Server is active")
        print("Waiting for Pico connections...")
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down server...")
            self.running = False
        finally:
            await self.cleanup()

    async def monitor_system(self):
        """
        Periodically print system status (connected Picos, RTL-SDR activity).
        """
        while self.running:
            await asyncio.sleep(30)
            pico_count = len(self.rtl_manager.connected_picos)
            print(f"📊 Status: {pico_count} Pico(s) connected, RTL-SDR active")

    async def cleanup(self):
        """
        Cleanup resources and terminate RTL-TCP subprocess on shutdown.
        """
        print("Cleaning up...")
        if self.rtl_manager.rtl_process:
            self.rtl_manager.rtl_process.terminate()
            self.rtl_manager.rtl_process.wait()
        print("✅ Cleanup complete")

if __name__ == "__main__":
    server = AutomotiveSecurityServer()
    def signal_handler(sig, frame):
        """
        Signal handler for interrupt signals (e.g. Ctrl+C).
        """
        print("\nReceived interrupt signal")
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    asyncio.run(server.start_server())