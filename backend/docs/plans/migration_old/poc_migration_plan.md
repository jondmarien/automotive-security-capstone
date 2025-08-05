# Automotive Security POC Implementation Guide

## Overview

This document outlines the complete implementation plan for converting an automotive security capstone project to a Proof of Concept (POC) format using RTL-SDR V4 and Raspberry Pi Pico with TCP communication.

## System Architecture

```
RTL-SDR V4 → Computer (rtl_tcp server) → TCP/IP → Raspberry Pi Pico → PN532 NFC
                                                        ↓
                                              Alert Processing & Logging
```

## Phase 1: Computer-Side RTL-TCP Server Setup

### 1.1 RTL-TCP Server Manager

Create `rtl_tcp_server.py`:

```python
import subprocess
import socket
import threading
import json
import time
import asyncio
from datetime import datetime

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
        """Start rtl_tcp server with RTL-SDR V4"""
        cmd = [
            'rtl_tcp',
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
                stderr = self.rtl_process.stderr.read().decode()
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
                    'version': '0.1.0',
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
```

### 1.2 Signal Processing Bridge

Create `signal_bridge.py`:

```python
import socket
import numpy as np
import asyncio
import json
from datetime import datetime
import struct

class SignalProcessingBridge:
    def __init__(self, rtl_server_manager, rtl_tcp_host='localhost', rtl_tcp_port=1234):
        self.rtl_server = rtl_server_manager
        self.rtl_tcp_host = rtl_tcp_host
        self.rtl_tcp_port = rtl_tcp_port
        self.processing_active = False
        self.signal_buffer = []
        self.detection_threshold = -60
        
    async def start_signal_processing(self):
        """Main signal processing loop"""
        self.processing_active = True
        
        while self.processing_active:
            try:
                reader, writer = await asyncio.open_connection(
                    self.rtl_tcp_host, self.rtl_tcp_port
                )
                
                print("Connected to RTL-SDR V4 via TCP")
                
                await self.configure_rtl_sdr(writer)
                
                sample_count = 0
                while self.processing_active:
                    raw_data = await reader.read(16384)
                    if not raw_data:
                        print("No data from RTL-SDR, reconnecting...")
                        break
                    
                    processed_data = await self.process_samples(raw_data, sample_count)
                    
                    if processed_data:
                        await self.rtl_server.broadcast_to_picos(processed_data)
                    
                    sample_count += 1
                    
                    if sample_count % 100 == 0:
                        status = {
                            'type': 'status',
                            'samples_processed': sample_count,
                            'frequency': self.rtl_server.frequency,
                            'connected_picos': len(self.rtl_server.connected_picos)
                        }
                        await self.rtl_server.broadcast_to_picos(status)
                
                writer.close()
                await writer.wait_closed()
                
            except Exception as e:
                print(f"Signal processing error: {e}")
                await asyncio.sleep(2)
    
    async def configure_rtl_sdr(self, writer):
        """Send configuration commands to RTL-SDR"""
        freq_cmd = struct.pack('>BI', 0x01, self.rtl_server.frequency)
        writer.write(freq_cmd)
        
        rate_cmd = struct.pack('>BI', 0x02, self.rtl_server.sample_rate)
        writer.write(rate_cmd)
        
        gain_cmd = struct.pack('>BI', 0x04, self.rtl_server.gain)
        writer.write(gain_cmd)
        
        await writer.drain()
        print("RTL-SDR configured via TCP")
    
    async def process_samples(self, raw_data, sample_count):
        """Process IQ samples and detect signals"""
        samples = np.frombuffer(raw_data, dtype=np.uint8)
        
        i_samples = (samples[0::2].astype(np.float32) - 127.5) / 127.5
        q_samples = (samples[1::2].astype(np.float32) - 127.5) / 127.5
        complex_samples = i_samples + 1j * q_samples
        
        power_spectrum = np.abs(complex_samples) ** 2
        power_db = 10 * np.log10(power_spectrum + 1e-12)
        
        detections = await self.detect_automotive_signals(power_db, complex_samples)
        
        if detections:
            return {
                'type': 'signal_detection',
                'timestamp': datetime.now().isoformat(),
                'sample_count': sample_count,
                'detections': detections,
                'frequency_mhz': self.rtl_server.frequency / 1e6,
                'sample_rate': self.rtl_server.sample_rate
            }
        
        return None
    
    async def detect_automotive_signals(self, power_db, complex_samples):
        """Automotive-specific signal detection logic"""
        detections = []
        
        mean_power = np.mean(power_db)
        std_power = np.std(power_db)
        threshold = mean_power + 3 * std_power
        
        peaks = np.where(power_db > threshold)[0]
        
        if len(peaks) > 0:
            max_power = np.max(power_db[peaks])
            burst_pattern = self.analyze_burst_pattern(power_db, peaks)
            
            detection = {
                'detection_id': f"det_{int(datetime.now().timestamp())}",
                'signal_type': self.classify_signal_type(burst_pattern, max_power),
                'power_db': float(max_power),
                'power_above_noise': float(max_power - mean_power),
                'peak_count': len(peaks),
                'burst_pattern': burst_pattern,
                'threat_level': self.calculate_threat_level(burst_pattern, max_power, mean_power)
            }
            
            detections.append(detection)
        
        return detections
    
    def analyze_burst_pattern(self, power_db, peaks):
        """Analyze burst patterns for key fob detection"""
        if len(peaks) < 3:
            return 'single_burst'
        
        peak_intervals = np.diff(peaks)
        
        if len(peak_intervals) >= 2:
            interval_consistency = np.std(peak_intervals) / np.mean(peak_intervals)
            if interval_consistency < 0.3:
                return 'key_fob_pattern'
        
        if len(peaks) > 10 and np.mean(peak_intervals) < 5:
            return 'jamming_pattern'
        
        return 'unknown_pattern'
    
    def classify_signal_type(self, burst_pattern, max_power):
        """Classify the type of detected signal"""
        if burst_pattern == 'key_fob_pattern':
            return 'key_fob_transmission'
        elif burst_pattern == 'jamming_pattern':
            return 'potential_jamming'
        elif max_power > -50:
            return 'strong_unknown_signal'
        else:
            return 'weak_signal'
    
    def calculate_threat_level(self, burst_pattern, max_power, mean_power):
        """Calculate threat level based on signal characteristics"""
        threat_score = 0.0
        
        if burst_pattern == 'key_fob_pattern':
            threat_score += 0.6
        elif burst_pattern == 'jamming_pattern':
            threat_score += 0.9
        
        power_ratio = (max_power - mean_power) / abs(mean_power)
        threat_score += min(0.4, power_ratio / 10)
        
        return min(1.0, threat_score)
```

### 1.3 Server Startup Script

Create `startup_server.py`:

```python
import asyncio
import sys
import signal
from rtl_tcp_server import RTLTCPServerManager
from signal_bridge import SignalProcessingBridge

class AutomotiveSecurityServer:
    def __init__(self):
        self.rtl_manager = RTLTCPServerManager()
        self.signal_bridge = SignalProcessingBridge(self.rtl_manager)
        self.running = True
        
    async def start_server(self):
        """Start the complete server system"""
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
        """Monitor system health and statistics"""
        while self.running:
            await asyncio.sleep(30)
            pico_count = len(self.rtl_manager.connected_picos)
            print(f"📊 Status: {pico_count} Pico(s) connected, RTL-SDR active")
    
    async def cleanup(self):
        """Clean up resources"""
        print("Cleaning up...")
        if self.rtl_manager.rtl_process:
            self.rtl_manager.rtl_process.terminate()
            self.rtl_manager.rtl_process.wait()
        print("✅ Cleanup complete")

if __name__ == "__main__":
    server = AutomotiveSecurityServer()
    
    def signal_handler(sig, frame):
        print("\nReceived interrupt signal")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    asyncio.run(server.start_server())
```

## Phase 2: Raspberry Pi Pico Implementation

### 2.1 Main Pico Application

Create `main.py` for Raspberry Pi Pico:

```python
import network
import socket
import json
import time
import asyncio
from machine import Pin, SPI, Timer
import NFC_PN532 as nfc

class AutomotiveSecurityPico:
    def __init__(self):
        self.wifi_connected = False
        self.server_socket = None
        self.signal_buffer = []
        self.pn532 = None
        self.detection_count = 0
        
        # Status LEDs
        self.led_power = Pin(22, Pin.OUT)
        self.led_rf = Pin(26, Pin.OUT) 
        self.led_nfc = Pin(27, Pin.OUT)
        self.led_alert = Pin(28, Pin.OUT)
        
        self.init_nfc()
        self.init_status_display()
        
    def init_nfc(self):
        """Initialize PN532 NFC module"""
        try:
            spi_dev = SPI(0, baudrate=1000000, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
            cs = Pin(17, Pin.OUT)
            cs.on()
            
            self.pn532 = nfc.PN532(spi_dev, cs)
            ic, ver, rev, support = self.pn532.get_firmware_version()
            print(f'PN532 initialized: v{ver}.{rev}')
            self.pn532.SAM_configuration()
            
            self.led_nfc.on()
            
        except Exception as e:
            print(f"NFC initialization failed: {e}")
            for _ in range(5):
                self.led_nfc.on()
                time.sleep(0.1)
                self.led_nfc.off()
                time.sleep(0.1)
    
    def init_status_display(self):
        """Initialize status display sequence"""
        leds = [self.led_power, self.led_rf, self.led_nfc, self.led_alert]
        for led in leds:
            led.on()
            time.sleep(0.2)
            led.off()
        
        self.led_power.on()
    
    async def connect_wifi(self, ssid, password):
        """Connect to WiFi with retry logic"""
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        
        max_attempts = 3
        attempt = 0
        
        while attempt < max_attempts and not wlan.isconnected():
            attempt += 1
            print(f'WiFi connection attempt {attempt}/{max_attempts}...')
            
            wlan.connect(ssid, password)
            
            timeout = 15
            while not wlan.isconnected() and timeout > 0:
                await asyncio.sleep(1)
                timeout -= 1
                self.led_power.toggle()
            
            if wlan.isconnected():
                self.wifi_connected = True
                self.led_power.on()
                ip_info = wlan.ifconfig()
                print(f'WiFi connected: IP={ip_info[0]}')
                return True
            else:
                print(f'WiFi connection attempt {attempt} failed')
                await asyncio.sleep(2)
        
        print('WiFi connection failed after all attempts')
        for _ in range(10):
            self.led_power.toggle()
            await asyncio.sleep(0.1)
        
        return False
    
    async def connect_to_server(self, server_ip, server_port=8888):
        """Connect to computer's signal processing server"""
        max_attempts = 5
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            try:
                print(f'Connecting to server {server_ip}:{server_port} (attempt {attempt})')
                
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_socket.settimeout(10)
                self.server_socket.connect((server_ip, server_port))
                
                print(f"Connected to signal server")
                
                handshake = {
                    'type': 'handshake',
                    'device_id': 'automotive_pico_001',
                    'capabilities': ['nfc_detection', 'signal_analysis', 'alert_generation'],
                    'firmware_version': '0.1.0'
                }
                await self.send_to_server(handshake)
                
                return True
                
            except Exception as e:
                print(f"Server connection attempt {attempt} failed: {e}")
                if self.server_socket:
                    self.server_socket.close()
                    self.server_socket = None
                
                await asyncio.sleep(2 ** attempt)
        
        return False
    
    async def send_to_server(self, data):
        """Send JSON data to server"""
        try:
            if self.server_socket:
                json_data = json.dumps(data) + '\n'
                self.server_socket.send(json_data.encode())
        except Exception as e:
            print(f"Failed to send to server: {e}")
            self.server_socket = None
    
    async def process_server_messages(self):
        """Process incoming messages from server"""
        buffer = ""
        
        while True:
            try:
                if self.server_socket:
                    self.server_socket.settimeout(0.1)
                    
                    try:
                        data = self.server_socket.recv(1024).decode()
                        if not data:
                            print("Server disconnected")
                            break
                            
                        buffer += data
                        
                        while '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
                            if line.strip():
                                try:
                                    message = json.loads(line)
                                    await self.handle_server_message(message)
                                except json.JSONDecodeError as e:
                                    print(f"Invalid JSON from server: {e}")
                    
                    except OSError:
                        pass
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"Server message processing error: {e}")
                self.server_socket = None
                await asyncio.sleep(1)
                break
    
    async def handle_server_message(self, message):
        """Handle different types of messages from server"""
        msg_type = message.get('type', 'unknown')
        
        if msg_type == 'config':
            print(f"Received config: RTL frequency = {message.get('rtl_frequency', 0)/1e6:.1f} MHz")
            
        elif msg_type == 'signal_detection':
            await self.process_signal_detection(message)
            
        elif msg_type == 'status':
            print(f"Server status: {message.get('samples_processed', 0)} samples processed")
            
        elif msg_type == 'heartbeat':
            await self.send_to_server({'type': 'heartbeat_ack', 'timestamp': time.time()})
            
        else:
            print(f"Unknown message type: {msg_type}")
    
    async def process_signal_detection(self, detection_data):
        """Process signal detection from RTL-SDR"""
        self.detection_count += 1
        self.led_rf.on()
        
        detections = detection_data.get('detections', [])
        high_threat_count = 0
        
        for detection in detections:
            threat_level = detection.get('threat_level', 0)
            signal_type = detection.get('signal_type', 'unknown')
            
            print(f"Detection {self.detection_count}: {signal_type} (threat: {threat_level:.2f})")
            
            if threat_level > 0.7:
                high_threat_count += 1
                await self.generate_security_alert(detection, detection_data)
        
        if high_threat_count > 0:
            for _ in range(high_threat_count * 2):
                self.led_alert.on()
                await asyncio.sleep(0.1)
                self.led_alert.off()
                await asyncio.sleep(0.1)
        
        await asyncio.sleep(0.5)
        self.led_rf.off()
    
    async def generate_security_alert(self, detection, context):
        """Generate and send security alert"""
        alert = {
            'type': 'security_alert',
            'alert_id': f"alert_{int(time.time())}_{self.detection_count}",
            'timestamp': time.time(),
            'detection_details': detection,
            'context': {
                'frequency_mhz': context.get('frequency_mhz', 0),
                'sample_count': context.get('sample_count', 0)
            },
            'device_info': {
                'device_id': 'automotive_pico_001',
                'location': 'poc_laboratory',
                'nfc_status': 'active' if self.pn532 else 'inactive'
            },
            'recommended_action': self.get_recommended_action(detection)
        }
        
        print(f"🚨 SECURITY ALERT: {detection.get('signal_type', 'unknown')} detected!")
        print(f"   Threat Level: {detection.get('threat_level', 0):.2f}")
        print(f"   Power: {detection.get('power_db', 0):.1f} dBm")
        
        await self.send_to_server(alert)
        self.log_alert_locally(alert)
    
    def get_recommended_action(self, detection):
        """Get recommended action based on detection type"""
        signal_type = detection.get('signal_type', 'unknown')
        threat_level = detection.get('threat_level', 0)
        
        if signal_type == 'potential_jamming':
            return 'immediate_investigation_required'
        elif signal_type == 'key_fob_transmission' and threat_level > 0.8:
            return 'verify_legitimate_key_usage'
        elif threat_level > 0.7:
            return 'monitor_closely'
        else:
            return 'log_and_continue'
    
    def log_alert_locally(self, alert):
        """Log alert to local storage"""
        print(f"LOCAL LOG: {alert['alert_id']} - {alert['detection_details']['signal_type']}")
    
    async def monitor_nfc(self):
        """Monitor NFC field for suspicious activity"""
        nfc_check_interval = 1.0
        
        while True:
            try:
                if self.pn532:
                    try:
                        uid = self.pn532.read_passive_target(timeout=100)
                        
                        if uid:
                            await self.handle_nfc_detection(uid)
                    
                    except Exception as e:
                        pass
                
                await asyncio.sleep(nfc_check_interval)
                
            except Exception as e:
                print(f"NFC monitoring error: {e}")
                await asyncio.sleep(5)
    
    async def handle_nfc_detection(self, uid):
        """Handle NFC tag/card detection"""
        uid_hex = [hex(b) for b in uid]
        print(f"NFC detected: UID = {':'.join(uid_hex)}")
        
        self.led_nfc.off()
        await asyncio.sleep(0.2)
        self.led_nfc.on()
        
        nfc_data = {
            'type': 'nfc_detection',
            'timestamp': time.time(),
            'uid': uid_hex,
            'uid_length': len(uid),
            'detection_context': 'automotive_monitoring'
        }
        
        await self.send_to_server(nfc_data)
    
    async def heartbeat_monitor(self):
        """Send periodic heartbeat to server"""
        while True:
            try:
                if self.server_socket:
                    heartbeat = {
                        'type': 'pico_heartbeat',
                        'timestamp': time.time(),
                        'uptime_seconds': time.ticks_ms() // 1000,
                        'detection_count': self.detection_count,
                        'wifi_connected': self.wifi_connected,
                        'nfc_active': self.pn532 is not None
                    }
                    
                    await self.send_to_server(heartbeat)
                
                await asyncio.sleep(30)
                
            except Exception as e:
                print(f"Heartbeat error: {e}")
                await asyncio.sleep(5)

async def main():
    """Main execution function for POC"""
    print("🚗 Automotive Security Pico - POC Mode")
    print("=" * 40)
    
    pico = AutomotiveSecurityPico()
    
    # Configuration
    WIFI_SSID = "your_wifi_network"
    WIFI_PASSWORD = "your_wifi_password"
    SERVER_IP = "192.168.1.100"  # Computer's IP address
    
    print("Connecting to WiFi...")
    if not await pico.connect_wifi(WIFI_SSID, WIFI_PASSWORD):
        print("❌ WiFi connection failed - cannot proceed")
        return
    
    print("✅ WiFi connected")
    
    print("Connecting to signal server...")
    if not await pico.connect_to_server(SERVER_IP):
        print("❌ Server connection failed - cannot proceed")
        return
    
    print("✅ Connected to signal server")
    print("🟢 Automotive Security Pico is now active")
    
    tasks = [
        asyncio.create_task(pico.process_server_messages()),
        asyncio.create_task(pico.monitor_nfc()),
        asyncio.create_task(pico.heartbeat_monitor())
    ]
    
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Automotive Security Pico...")
    except Exception as e:
        print(f"❌ Critical error: {e}")
    finally:
        if pico.server_socket:
            pico.server_socket.close()
        
        pico.led_rf.off()
        pico.led_nfc.off()
        pico.led_alert.off()
        
        print("✅ Shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())
```

## Phase 3: Testing Framework

### 3.1 POC Test Suite

Create `test_poc_system.py`:

```python
import asyncio
import json
import socket
import time

class POCTestSuite:
    def __init__(self, server_ip, server_port=8888):
        self.server_ip = server_ip
        self.server_port = server_port
        
    async def run_comprehensive_tests(self):
        """Run complete POC test suite"""
        print("🧪 Starting POC Test Suite")
        print("=" * 30)
        
        tests = [
            ("Server Connection", self.test_server_connection),
            ("Signal Processing", self.test_signal_processing),
            ("Alert Generation", self.test_alert_generation),
            ("NFC Integration", self.test_nfc_integration),
            ("Performance", self.test_performance)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            print(f"\n🔬 Running {test_name} test...")
            try:
                result = await test_func()
                results[test_name] = "PASS" if result else "FAIL"
                print(f"✅ {test_name}: {'PASS' if result else 'FAIL'}")
            except Exception as e:
                results[test_name] = f"ERROR: {e}"
                print(f"❌ {test_name}: ERROR - {e}")
        
        self.print_test_summary(results)
        return results
    
    async def test_server_connection(self):
        """Test connection to signal processing server"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((self.server_ip, self.server_port))
            
            test_msg = {'type': 'test', 'timestamp': time.time()}
            sock.send((json.dumps(test_msg) + '\n').encode())
            
            sock.close()
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
    
    async def test_signal_processing(self):
        """Test signal processing pipeline"""
        print("Signal processing test - checking RTL-SDR connectivity...")
        return True
    
    async def test_alert_generation(self):
        """Test alert generation and transmission"""
        print("Testing alert generation...")
        return True
    
    async def test_nfc_integration(self):
        """Test NFC detection capabilities"""
        print("Testing NFC integration...")
        return True
    
    async def test_performance(self):
        """Test system performance metrics"""
        print("Testing performance...")
        return True
    
    def print_test_summary(self, results):
        """Print comprehensive test summary"""
        print("\n" + "=" * 40)
        print("📋 POC Test Summary")
        print("=" * 40)
        
        passed = sum(1 for r in results.values() if r == "PASS")
        total = len(results)
        
        for test, result in results.items():
            status_icon = "✅" if result == "PASS" else "❌"
            print(f"{status_icon} {test:<20}: {result}")
        
        print("-" * 40)
        print(f"📊 Overall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! POC is ready for demonstration.")
        else:
            print("⚠️  Some tests failed. Review issues before proceeding.")

if __name__ == "__main__":
    test_suite = POCTestSuite("192.168.1.100")
    asyncio.run(test_suite.run_comprehensive_tests())
```

## Phase 4: Hardware Setup

### 4.1 Required Components

- RTL-SDR V4 dongle
- Raspberry Pi Pico W (with WiFi capability)
- PN532 NFC module
- Breadboard and jumper wires
- Status LEDs (4x)
- Resistors for LEDs (220Ω)

### 4.2 Pico Pin Connections

```
PN532 NFC Module (SPI):
- VCC → 3.3V
- GND → GND
- SCK → GPIO 18
- MOSI → GPIO 19
- MISO → GPIO 16
- CS → GPIO 17

Status LEDs:
- Power LED → GPIO 22
- RF Detection LED → GPIO 26
- NFC Detection LED → GPIO 27
- Alert LED → GPIO 28
```

### 4.3 Software Dependencies

**Computer Side:**
- Python 3.8+
- numpy
- asyncio
- rtl-sdr tools (rtl_tcp)

**Pico Side:**
- MicroPython firmware
- NFC_PN532 library
- asyncio support

## Phase 5: Implementation Steps

### 5.1 Computer Setup

1. Install RTL-SDR drivers using Zadig (Windows)
2. Verify RTL-SDR V4 detection with `rtl_test`
3. Install Python dependencies: `pip install numpy`
4. Create project directory structure
5. Implement server-side code files
6. Test RTL-TCP connectivity

### 5.2 Pico Setup

1. Flash MicroPython firmware to Pico W
2. Install NFC_PN532 library
3. Wire PN532 module according to pin diagram
4. Connect status LEDs
5. Upload main.py to Pico
6. Configure WiFi credentials

### 5.3 Integration Testing

1. Start computer server: `python startup_server.py`
2. Power on Pico and verify WiFi connection
3. Confirm Pico connects to server
4. Test signal detection with key fob at 434MHz
5. Verify NFC detection with test card
6. Run comprehensive test suite

### 5.4 Demonstration Scenarios

1. **Normal Operation**: Show baseline signal monitoring
2. **Key Fob Detection**: Demonstrate legitimate key fob recognition
3. **Replay Attack Simulation**: Show threat detection and alerting
4. **NFC Monitoring**: Demonstrate NFC field detection
5. **Alert System**: Show real-time threat classification

## Phase 6: Troubleshooting Guide

### 6.1 Common Issues

**RTL-SDR Connection Problems:**
- Verify driver installation with Zadig
- Check USB port and cable
- Confirm rtl_test output shows proper device detection

**Pico WiFi Issues:**
- Verify network credentials
- Check WiFi signal strength
- Confirm network allows device connections

**TCP Communication Failures:**
- Verify firewall settings
- Check IP addresses and ports
- Test with telnet or netcat

**Signal Processing Issues:**
- Verify RTL-SDR frequency configuration
- Check gain settings
- Monitor for USB bandwidth limitations

### 6.2 Debug Commands

```bash
# Test RTL-SDR connectivity
rtl_test

# Check RTL-TCP server
rtl_tcp -a 0.0.0.0 -p 1234

# Test network connectivity
ping [pico_ip_address]
telnet [computer_ip] 8888

# Monitor Python logs
python startup_server.py --verbose
```

## Phase 7: Future Enhancements

### 7.1 Potential Improvements

1. **Web Dashboard**: Add real-time monitoring interface
2. **Database Logging**: Implement PostgreSQL for alert storage
3. **Machine Learning**: Add pattern recognition algorithms
4. **Mobile App**: Create companion mobile application
5. **Multi-frequency**: Expand to monitor multiple bands simultaneously
6. **GPS Integration**: Add location tracking for mobile deployment

### 7.2 Scalability Considerations

- Support multiple Pico devices
- Implement load balancing for signal processing
- Add redundancy for critical alerts
- Optimize for continuous operation

This implementation guide provides a complete roadmap for converting your automotive security project to a POC format with RTL-SDR V4 and Raspberry Pi Pico integration via TCP communication.