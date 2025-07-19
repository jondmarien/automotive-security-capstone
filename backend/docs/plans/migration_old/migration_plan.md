Perfect! This POC approach is much more practical for your cybersecurity capstone project and aligns well with your web security and penetration testing background[1]. Let me redesign the architecture for a computer-intermediated system with TCP communication.

## **Revised POC Architecture**

Your new system topology:
```
RTL-SDR V4 → Computer (rtl_tcp server) → TCP/IP → Raspberry Pi Pico → PN532 NFC
                                                        ↓
                                              Alert Processing & Logging
```

## **Computer-Side Implementation**

### **RTL-TCP Server Setup**

Building on your successful RTL-SDR testing, here's the server configuration:

```python
# rtl_tcp_manager.py
import subprocess
import socket
import threading
import json
import time

class RTLTCPManager:
    def __init__(self, frequency=434000000, sample_rate=2048000, gain=25):
        self.frequency = frequency
        self.sample_rate = sample_rate
        self.gain = gain
        self.rtl_process = None
        self.tcp_port = 1234
        
    def start_rtl_tcp_server(self):
        """Start rtl_tcp server with your RTL-SDR V4"""
        cmd = [
            'rtl_tcp',
            '-a', '0.0.0.0',  # Listen on all interfaces
            '-p', str(self.tcp_port),
            '-f', str(self.frequency),
            '-s', str(self.sample_rate),
            '-g', str(self.gain)
        ]
        
        print(f"Starting rtl_tcp server: {' '.join(cmd)}")
        self.rtl_process = subprocess.Popen(cmd)
        time.sleep(2)  # Allow server to start
        
    def send_frequency_change(self, new_frequency):
        """Send frequency change command to rtl_tcp"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('localhost', self.tcp_port))
            
            # rtl_tcp frequency command: 0x01 + 4 bytes frequency
            freq_bytes = new_frequency.to_bytes(4, byteorder='big')
            command = b'\x01' + freq_bytes
            sock.send(command)
            sock.close()
            
            print(f"Frequency changed to {new_frequency} Hz")
            
        except Exception as e:
            print(f"Failed to change frequency: {e}")
```

### **Signal Processing Bridge**

Since you're doing web development work[2], you might appreciate this API-style approach:

```python
# signal_processor.py
import socket
import struct
import numpy as np
import asyncio
import json
from datetime import datetime

class SignalProcessor:
    def __init__(self, rtl_tcp_host='localhost', rtl_tcp_port=1234):
        self.rtl_tcp_host = rtl_tcp_host
        self.rtl_tcp_port = rtl_tcp_port
        self.pico_connections = []
        self.processing_active = False
        
    async def start_processing(self):
        """Main processing loop that bridges RTL-SDR to Pico"""
        self.processing_active = True
        
        while self.processing_active:
            try:
                # Connect to rtl_tcp server
                reader, writer = await asyncio.open_connection(
                    self.rtl_tcp_host, self.rtl_tcp_port
                )
                
                print("Connected to rtl_tcp server")
                
                # Read IQ samples continuously
                while self.processing_active:
                    # Read 8192 samples (16384 bytes for I/Q pairs)
                    raw_data = await reader.read(16384)
                    if not raw_data:
                        break
                        
                    # Process the samples
                    processed_data = await self.process_iq_samples(raw_data)
                    
                    # Send to connected Picos
                    if processed_data:
                        await self.broadcast_to_picos(processed_data)
                        
                writer.close()
                await writer.wait_closed()
                
            except Exception as e:
                print(f"Processing error: {e}")
                await asyncio.sleep(1)
    
    async def process_iq_samples(self, raw_data):
        """Process raw IQ samples and detect signals"""
        # Convert bytes to I/Q samples
        samples = np.frombuffer(raw_data, dtype=np.uint8)
        
        # Convert to complex numbers (I + jQ)
        i_samples = (samples[0::2] - 127.5) / 127.5
        q_samples = (samples[1::2] - 127.5) / 127.5
        complex_samples = i_samples + 1j * q_samples
        
        # Calculate power spectrum
        power_spectrum = np.abs(complex_samples) ** 2
        
        # Simple peak detection
        mean_power = np.mean(power_spectrum)
        std_power = np.std(power_spectrum)
        threshold = mean_power + 3 * std_power
        
        peaks = np.where(power_spectrum > threshold)[0]
        
        if len(peaks) > 0:
            return {
                'timestamp': datetime.now().isoformat(),
                'peak_count': len(peaks),
                'max_power': float(np.max(power_spectrum[peaks])),
                'mean_power': float(mean_power),
                'frequency_bins': peaks.tolist()[:10],  # Limit to first 10 peaks
                'sample_rate': 2048000
            }
        
        return None
    
    async def broadcast_to_picos(self, signal_data):
        """Send processed signal data to all connected Picos"""
        json_data = json.dumps(signal_data) + '\n'
        
        for pico_writer in self.pico_connections[:]:  # Copy list to avoid modification during iteration
            try:
                pico_writer.write(json_data.encode())
                await pico_writer.drain()
            except Exception as e:
                print(f"Failed to send to Pico: {e}")
                self.pico_connections.remove(pico_writer)
```

## **Raspberry Pi Pico Implementation**

### **TCP Client for Signal Reception**

```python
# main.py for Raspberry Pi Pico
import network
import socket
import json
import time
import asyncio
from machine import Pin, SPI
import NFC_PN532 as nfc

class AutomotiveSecurityPico:
    def __init__(self):
        self.wifi_connected = False
        self.tcp_socket = None
        self.signal_buffer = []
        self.pn532 = None
        
        # Initialize status LEDs
        self.led_power = Pin(22, Pin.OUT)
        self.led_rf = Pin(26, Pin.OUT)
        self.led_nfc = Pin(27, Pin.OUT)
        
        # Initialize PN532
        self.init_nfc()
        
    def init_nfc(self):
        """Initialize PN532 NFC module"""
        try:
            spi_dev = SPI(0, baudrate=1000000, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
            cs = Pin(17, Pin.OUT)
            cs.on()
            
            self.pn532 = nfc.PN532(spi_dev, cs)
            ic, ver, rev, support = self.pn532.get_firmware_version()
            print(f'PN532 Firmware: {ver}.{rev}')
            self.pn532.SAM_configuration()
            
            self.led_nfc.on()  # Indicate NFC ready
            
        except Exception as e:
            print(f"NFC initialization failed: {e}")
    
    async def connect_wifi(self, ssid, password):
        """Connect to WiFi network"""
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        
        if not wlan.isconnected():
            print(f'Connecting to {ssid}...')
            wlan.connect(ssid, password)
            
            # Wait for connection
            timeout = 10
            while not wlan.isconnected() and timeout > 0:
                await asyncio.sleep(1)
                timeout -= 1
            
        if wlan.isconnected():
            self.wifi_connected = True
            self.led_power.on()
            print(f'Connected: {wlan.ifconfig()}')
            return True
        else:
            print('WiFi connection failed')
            return False
    
    async def connect_to_signal_server(self, server_ip, server_port=8888):
        """Connect to computer's signal processing server"""
        try:
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_socket.connect((server_ip, server_port))
            print(f"Connected to signal server at {server_ip}:{server_port}")
            return True
            
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            return False
    
    async def process_incoming_signals(self):
        """Process incoming signal data from computer"""
        buffer = ""
        
        while True:
            try:
                if self.tcp_socket:
                    # Receive data
                    data = self.tcp_socket.recv(1024).decode()
                    if not data:
                        break
                        
                    buffer += data
                    
                    # Process complete JSON messages
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        if line.strip():
                            await self.handle_signal_data(json.loads(line))
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"Signal processing error: {e}")
                await asyncio.sleep(1)
    
    async def handle_signal_data(self, signal_data):
        """Process received signal data and determine threat level"""
        print(f"Received signal: {signal_data['peak_count']} peaks, max power: {signal_data['max_power']:.2f}")
        
        # Flash RF LED to indicate signal reception
        self.led_rf.on()
        await asyncio.sleep(0.1)
        self.led_rf.off()
        
        # Analyze signal characteristics
        threat_level = self.analyze_threat_level(signal_data)
        
        if threat_level > 0.5:  # Threshold for alert
            await self.generate_security_alert(signal_data, threat_level)
    
    def analyze_threat_level(self, signal_data):
        """Analyze signal data to determine threat level"""
        threat_score = 0.0
        
        # Multiple peaks might indicate replay attack
        if signal_data['peak_count'] > 3:
            threat_score += 0.3
        
        # Strong signal relative to background
        power_ratio = signal_data['max_power'] / signal_data['mean_power']
        if power_ratio > 10:
            threat_score += 0.4
        
        # Frequency bin analysis (simplified)
        if len(signal_data['frequency_bins']) > 1:
            # Multiple frequency components
            threat_score += 0.2
        
        return min(1.0, threat_score)
    
    async def generate_security_alert(self, signal_data, threat_level):
        """Generate and log security alert"""
        alert = {
            'alert_id': f"alert_{int(time.time())}",
            'timestamp': signal_data['timestamp'],
            'threat_level': threat_level,
            'signal_characteristics': {
                'peak_count': signal_data['peak_count'],
                'max_power': signal_data['max_power'],
                'frequency_bins': signal_data['frequency_bins'][:5]  # First 5 bins
            },
            'device_info': {
                'device_type': 'automotive_security_pico',
                'location': 'poc_lab'
            }
        }
        
        print(f"SECURITY ALERT: Threat level {threat_level:.2f}")
        print(json.dumps(alert, indent=2))
        
        # Flash all LEDs for high-threat alerts
        if threat_level > 0.8:
            for _ in range(5):
                self.led_power.off()
                self.led_rf.off()
                self.led_nfc.off()
                await asyncio.sleep(0.2)
                self.led_power.on()
                self.led_rf.on()
                self.led_nfc.on()
                await asyncio.sleep(0.2)
```

### **Main Execution Loop**

```python
async def main():
    """Main execution function"""
    pico = AutomotiveSecurityPico()
    
    # Connect to WiFi
    wifi_success = await pico.connect_wifi('your_wifi_ssid', 'your_wifi_password')
    if not wifi_success:
        print("WiFi connection failed, cannot proceed")
        return
    
    # Connect to signal processing server
    server_connected = await pico.connect_to_signal_server('192.168.1.100')  # Your computer's IP
    if not server_connected:
        print("Cannot connect to signal server")
        return
    
    # Start concurrent tasks
    tasks = [
        asyncio.create_task(pico.process_incoming_signals()),
        asyncio.create_task(pico.monitor_nfc()),
        asyncio.create_task(pico.heartbeat_monitor())
    ]
    
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        if pico.tcp_socket:
            pico.tcp_socket.close()

# Run the main function
asyncio.run(main())
```

## **Computer-Side Signal Server**

```python
# signal_server.py
import asyncio
import json
from signal_processor import SignalProcessor

class PicoSignalServer:
    def __init__(self, port=8888):
        self.port = port
        self.processor = SignalProcessor()
        self.clients = []
        
    async def handle_pico_connection(self, reader, writer):
        """Handle incoming Pico connections"""
        addr = writer.get_extra_info('peername')
        print(f"Pico connected from {addr}")
        
        self.clients.append(writer)
        self.processor.pico_connections.append(writer)
        
        try:
            # Keep connection alive and handle any incoming data from Pico
            while True:
                data = await reader.read(1024)
                if not data:
                    break
                    
                # Process any commands from Pico
                try:
                    command = json.loads(data.decode())
                    await self.handle_pico_command(command, writer)
                except:
                    pass  # Ignore malformed data
                    
        except Exception as e:
            print(f"Pico connection error: {e}")
        finally:
            print(f"Pico {addr} disconnected")
            if writer in self.clients:
                self.clients.remove(writer)
            if writer in self.processor.pico_connections:
                self.processor.pico_connections.remove(writer)
            writer.close()
    
    async def handle_pico_command(self, command, writer):
        """Handle commands from Pico"""
        if command.get('type') == 'frequency_change':
            new_freq = command.get('frequency', 434000000)
            # Send frequency change to RTL-SDR
            # Implementation depends on your RTL-TCP setup
            
    async def start_server(self):
        """Start the TCP server for Pico connections"""
        server = await asyncio.start_server(
            self.handle_pico_connection, 
            '0.0.0.0', 
            self.port
        )
        
        print(f"Signal server listening on port {self.port}")
        
        # Start signal processing
        asyncio.create_task(self.processor.start_processing())
        
        async with server:
            await server.serve_forever()

if __name__ == "__main__":
    server = PicoSignalServer()
    asyncio.run(server.start_server())
```

This POC architecture gives you a clean separation of concerns: your computer handles the heavy RTL-SDR processing while the Pico focuses on real-time response and NFC monitoring. The TCP communication allows for easy debugging and monitoring, which aligns well with your penetration testing experience[1].

The modular design also makes it easy to add web-based monitoring interfaces later, leveraging your web development skills[2].

Citations:
[1] [Education](education.cybersecurity)  
[2] [Programming](programming.web_development)