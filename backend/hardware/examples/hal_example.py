#!/usr/bin/env python3
"""
Example usage of the Hardware Abstraction Layer (HAL).

This example demonstrates how to use the HAL to interact with hardware components.
"""

import asyncio
import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Use absolute imports
from hardware.core.factory import hardware_factory
from hardware.models.models import RFConfig


class HALExample:
    """Example class demonstrating HAL usage."""
    
    def __init__(self):
        """Initialize the example."""
        self.rf = None
        self.power = None
        self.status = None
        self.rx_count = 0
    
    async def packet_received(self, data: bytes) -> None:
        """Callback for received packets."""
        self.rx_count += 1
        print(f"\n[{datetime.now().isoformat()}] Packet received (Total: {self.rx_count}): {data!r}")
    
    async def run(self) -> None:
        """Run the example."""
        print("HAL Example - Starting...")
        
        try:
            # Create and configure RF interface
            print("Creating and configuring RF interface...")
            # Create RF config with required parameters
            rf_config = RFConfig(
                frequency=433.92e6,  # 433.92 MHz
                power=10,            # 10 dBm
                data_rate=100000,    # 100 kbps
                modulation='FSK',    # FSK modulation
                bandwidth=200000,    # 200 kHz
                devitation=25000,    # 25 kHz
                sync_word=b'\x12',   # Sync word
                crc_enabled=True,    # Enable CRC
                auto_ack=False,      # Disable auto-ack
                node_id=1,           # Node ID
                network_id=1         # Network ID
            )
            
            # Create and initialize RF interface with config
            self.rf = await hardware_factory.create_rf_interface('mock', rf_config)
            
            # Start receiving
            print("Starting packet reception...")
            await self.rf.start_receiving(self.packet_received)
            
            # Main loop
            print("\n=== HAL Example Running (Press Ctrl+C to stop) ===")
            print("Sending test packets every 5 seconds...")
            
            try:
                counter = 0
                while True:
                    # Send a test packet
                    test_data = f"TEST-{counter}".encode()
                    success = await self.rf.send_packet(test_data)
                    if success:
                        print(f"Sent packet: {test_data!r}")
                    else:
                        print(f"Failed to send packet: {test_data!r}")
                    
                    # Get signal metrics
                    metrics = self.rf.get_signal_metrics()
                    print(f"Signal metrics: RSSI={metrics.rssi:.1f} dBm, SNR={metrics.snr:.1f} dB")
                    
                    counter += 1
                    await asyncio.sleep(5)
                    
            except asyncio.CancelledError:
                print("\nShutting down...")
                
        except Exception as e:
            print(f"Error: {e}")
            raise
            
        finally:
            # Cleanup
            print("Cleaning up...")
            if self.rf and hasattr(self.rf, 'is_receiving') and self.rf.is_receiving:
                await self.rf.stop_receiving()
            print("Done.")


async def main():
    """Run the example."""
    example = HALExample()
    try:
        await example.run()
    except KeyboardInterrupt:
        print("\nUser interrupted.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
