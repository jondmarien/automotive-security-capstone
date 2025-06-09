#!/usr/bin/env python3
"""
Example usage of the Hardware Abstraction Layer (HAL).

This example demonstrates how to use the HAL to interact with hardware components.
"""

import asyncio
import logging
import random
import sys
import time
from datetime import datetime

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def color_text(text, color):
    """Apply color to text if output is a terminal."""
    return f"{color}{text}{Colors.END}" if sys.stdout.isatty() else text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Use absolute imports
from hardware.core.factory import hardware_factory  # noqa: E402
from hardware.models.models import RFConfig  # noqa: E402
from hardware.utils.reporter import SecurityAnalyzer  # noqa: E402


class HALExample:
    """Example class demonstrating HAL usage."""
    
    def __init__(self):
        """Initialize the example."""
        self.rf = None
        self.power = None
        self.status = None
        self.rx_count = 0
        self.analyzer = SecurityAnalyzer()
    
    async def packet_received(self, data: bytes) -> None:
        """Callback for received packets."""
        self.rx_count += 1
        print(f"\n{color_text('[' + datetime.now().isoformat() + ']', Colors.HEADER)} "
              f"Packet received {color_text(f'(Total: {self.rx_count}):', Colors.BOLD)}")
        print(f"  {color_text('Raw:', Colors.BLUE)} {data!r}")
        print(f"  {color_text('Hex:', Colors.CYAN)} {data.hex()}")
        
        # Try to decode as UTF-8 if possible
        try:
            decoded = data.decode('utf-8', errors='replace')
            print(f"  {color_text('Text:', Colors.GREEN)} {decoded}")
        except UnicodeDecodeError:
            pass  # Not UTF-8, skip text representation
    
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
                    # Occasionally generate potentially malicious packets (1 in 5 chance)
                    if random.random() < 0.2:  # 20% chance of generating a suspicious packet
                        attack_type = random.choice([
                            'REPLAY',     # Replay attack pattern
                            'JAMMING',    # Jamming pattern (very high power)
                            'INJECT',     # Injection attempt
                            'BRUTE',      # Brute force attempt
                            'REPLAY_OLD'  # Old timestamp replay
                        ])
                        
                        if attack_type == 'REPLAY':
                            # Replay attack - same packet multiple times
                            packet_type = 'KEYFOB'
                            random_id = 9999  # Suspicious ID
                            random_data = b'REPLAY_ATTACK_1234'
                            
                        elif attack_type == 'JAMMING':
                            # Jamming pattern - very high power signal
                            packet_type = 'JAMMER'
                            random_id = 0
                            random_data = b'\xFF' * 16  # Full power signal
                            
                        elif attack_type == 'INJECT':
                            # Injection attempt - malformed packet
                            packet_type = 'INJECT'
                            random_id = 0xDEADBEEF
                            random_data = b'INJECT\x00\x01\x02\x03' + random.randbytes(8)
                            
                        elif attack_type == 'BRUTE':
                            # Brute force attempt - sequential IDs
                            packet_type = 'BRUTE_FORCE'
                            random_id = random.randint(1, 100)
                            random_data = b'BRUTE' + random_id.to_bytes(4, 'big')
                            
                        else:  # REPLAY_OLD
                            # Old timestamp replay
                            packet_type = 'OLD_REPLAY'
                            random_id = random.randint(1000, 9999)
                            random_data = b'OLD_' + str(int(time.time()) - 3600).encode()  # 1 hour old
                    else:
                        # Generate normal packet
                        packet_types = ['KEYFOB', 'TIRE_SENSOR', 'REMOTE', 'BEACON', 'TEST']
                        packet_type = random.choice(packet_types)
                        random_id = random.randint(1000, 9999)
                        random_data = random.randbytes(random.randint(4, 16))
                    
                    # Create test packet with random components
                    test_data = (
                        f"{packet_type}-{counter}-{random_id}-".encode() + random_data
                    )
                    
                    success = await self.rf.send_packet(test_data)
                    if success:
                        print(f"Sent packet: {test_data!r}")
                    else:
                        print(f"Failed to send packet: {test_data!r}")
                    
                    # Get signal metrics
                    metrics = self.rf.get_signal_metrics()
                    
                    # Generate random RSSI and frequency for more realistic testing
                    random_rssi = random.uniform(-90.0, -30.0)  # Typical RSSI range
                    # Common automotive frequencies: 315 MHz, 433.92 MHz, 868 MHz
                    random_freq = random.choice([315.0, 433.92, 868.0])
                    
                    # Create a proper Packet object with randomized signal data
                    from hardware.core.packet import Packet
                    packet = Packet(
                        rssi=random_rssi,
                        freq=random_freq,
                        payload=test_data
                    )
                    
                    analyzer = SecurityAnalyzer()
                    rssi = metrics['rssi']
                    rssi_color = Colors.GREEN if rssi >= -60 else Colors.YELLOW if rssi >= -80 else Colors.RED
        
                    print(color_text("Signal metrics: ", Colors.BOLD) +
                          f"RSSI={color_text(f"{rssi:.1f} dBm", rssi_color)}, "
                          f"SNR={metrics['snr']:.1f} dB, "
                          f"Freq={metrics['frequency']/1e6:.2f} MHz")
                    print(color_text("Analyzing packet...", Colors.YELLOW))
                    report = analyzer.analyze_packet(packet)
        
                    # Color code based on threat level
                    threat_level = report.threat_level.name
                    if threat_level == 'MALICIOUS':
                        threat_color = Colors.RED + Colors.BOLD
                    elif threat_level == 'SUSPICIOUS':
                        threat_color = Colors.YELLOW
                    else:
                        threat_color = Colors.GREEN
            
                    print(f"{color_text('Analyzed Packet:', Colors.BOLD)} {packet}")
                    print(f"{color_text('Threat Level:', Colors.BOLD)} {color_text(threat_level, threat_color)}")
                    print(f"{color_text('Reason:', Colors.BOLD)} {report.reason}")
                    
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