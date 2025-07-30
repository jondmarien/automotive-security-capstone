"""
main.py (Pico Client)

MicroPython code for Raspberry Pi Pico W.
Connects to WiFi and a backend TCP event server to receive automotive security detection events.
Handles event parsing, status LEDs, and NFC detection via PN532.
Sends NFC and security events back to the backend server.

Designed for use in the Automotive Security Capstone POC project.

Example usage:
    Copy this file to your Pico, set WIFI_SSID/WIFI_PASSWORD/SERVER_IP, and run main().
"""
import network
import socket
import json
import time
import uasyncio as asyncio
from machine import Pin, SPI, Timer
import NFC_PN532 as nfc

# ==== CONFIGURATION ====
SSID = "Office 2"   # WiFi SSID
PASSWORD = "CJutHW3vt@"        # WiFi password
SERVER_IP = "192.168.2.250"   # <-- your computer's IP
SERVER_PORT = 8888           # TCP port for event server

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
        # NFC correlation system
        self.nfc_correlation_mode = False
        self.active_rf_threat = None
        self.correlation_timeout = 30  # seconds
        self.correlation_timer = None
        self.init_nfc()
        self.init_status_display()

    def init_nfc(self):
        """Initialize PN532 NFC module"""
        try:
            spi_dev = SPI(0, baudrate=1000000, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
            cs = Pin(17, Pin.OUT)
            cs.on()
            pn532 = nfc.PN532(spi_dev, cs)
            ic, ver, rev, support = pn532.get_firmware_version()
            print("PN532 initialized: v{}.{}".format(ver, rev))
            pn532.SAM_configuration()
            self.pn532 = pn532
            self.led_nfc.on()
        except Exception as e:
            print("NFC initialization failed: {}".format(e))
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

    def connect_wifi(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(SSID, PASSWORD)
        print("Connecting to WiFi...", end="")
        for _ in range(20):
            if wlan.isconnected():
                break
            print(".", end="")
            time.sleep(1)
        if wlan.isconnected():
            self.wifi_connected = True
            print("\nConnected! IP:", wlan.ifconfig()[0])
            return True
        else:
            print("\nFailed to connect.")
            return False

    async def connect_to_server(self, server_ip, server_port=8888):
        """Connect to computer's signal processing server"""
        max_attempts = 5
        attempt = 0
        while attempt < max_attempts:
            attempt += 1
            try:
                print('Connecting to server {}:{} (attempt {})'.format(server_ip, server_port, attempt))
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_socket.settimeout(10)
                self.server_socket.connect((server_ip, server_port))
                print("Connected to signal server")
                handshake = {
                    'type': 'handshake',
                    'device_id': 'automotive_pico_001',
                    'capabilities': ['nfc_detection', 'signal_analysis', 'alert_generation'],
                    'firmware_version': '1.0.0'
                }
                await self.send_to_server(handshake)
                return True
            except Exception as e:
                print("Server connection attempt {} failed: {}".format(attempt, e))
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
                self.server_socket.send((json.dumps(data) + '\\n').encode())
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
                                # Separate JSON parsing from event handling
                                try:
                                    message = json.loads(line)
                                except Exception as e:
                                    print("Invalid JSON from server:", e)
                                    print("Raw line:", line)
                                    print("Disconnecting due to JSON error.")
                                    break
                                try:
                                    await self.handle_server_message(message)
                                except Exception as e:
                                    print("Error handling server message:", e)
                                    print("Message was:", message)
                    except OSError:
                        pass
                await asyncio.sleep(0.1)
            except Exception as e:
                print("Server message processing error: {}".format(e))
                self.server_socket = None
                await asyncio.sleep(1)
                break

    async def handle_server_message(self, message):
        """Handle different types of messages from server"""
        msg_type = message.get('type', 'unknown')
        if msg_type == 'config':
            freq = message.get('rtl_frequency', 0)
            if isinstance(freq, (float, int)):
                print("Received config: RTL frequency = {:.1f} MHz".format(freq / 1e6))
            else:
                print("Received config: RTL frequency = {}".format(freq))
        elif msg_type == 'signal_detection':
            await self.process_signal_detection(message)
        elif msg_type == 'status':
            samples = message.get('samples_processed', 0)
            print("Server status: {} samples processed".format(samples))
        elif msg_type == 'heartbeat':
            await self.send_to_server({'type': 'heartbeat_ack', 'timestamp': time.time()})
        else:
            print("Unknown message type: {}".format(msg_type))

    async def process_signal_detection(self, detection_data):
        """Process signal detection from RTL-SDR"""
        self.detection_count += 1
        self.led_rf.on()
        detections = detection_data.get('detections', [])
        high_threat_count = 0
        for detection in detections:
            threat_level = detection.get('threat_level', 0)
            signal_type = detection.get('event_type', 'unknown')
            # Debug print
            print("Detection {}: {} (threat: {})".format(self.detection_count, signal_type, threat_level))
            if not isinstance(threat_level, (float, int, str)):
                print("[DEBUG] Unexpected threat_level type:", type(threat_level), threat_level)
            if isinstance(threat_level, (float, int)) and threat_level > 0.7:
                high_threat_count += 1
                await self.generate_security_alert(detection, detection_data)
            elif isinstance(threat_level, str) and threat_level.lower() in ("high", "critical", "suspicious"):
                high_threat_count += 1
                await self.generate_security_alert(detection, detection_data)
        if high_threat_count > 0:
            for _ in range(high_threat_count * 2):
                self.led_alert.on()
                await asyncio.sleep(0.1)
                self.led_alert.off()
                await asyncio.sleep(0.1)
            # Activate NFC correlation for high-threat events
            await self.activate_nfc_correlation(detections)
        await asyncio.sleep(0.5)
        self.led_rf.off()

    async def activate_nfc_correlation(self, detections):
        """Activate NFC scanning when high-threat RF events detected"""
        print(f"[NFC CORRELATION] Activating NFC scanning for {len(detections)} high-threat events")
        
        # Set correlation mode active
        self.nfc_correlation_mode = True
        self.active_rf_threat = detections[0] if detections else None  # Store first high-threat detection
        
        # Visual indication of active NFC correlation mode
        self.led_nfc.on()
        
        # Cancel any existing correlation timer
        if self.correlation_timer:
            self.correlation_timer.cancel()
            self.correlation_timer = None
        
        # Set timeout to deactivate correlation mode
        self.correlation_timer = asyncio.create_task(self.nfc_correlation_timeout())
        
        # Send correlation activation event to server
        correlation_event = {
            'type': 'nfc_correlation_activated',
            'timestamp': time.time(),
            'detection_count': len(detections),
            'threat_types': [d.get('event_type', 'unknown') for d in detections]
        }
        await self.send_to_server(correlation_event)
    
    async def nfc_correlation_timeout(self):
        """Timeout NFC correlation mode"""
        await asyncio.sleep(self.correlation_timeout)
        
        if self.nfc_correlation_mode:
            print("[NFC CORRELATION] Timeout - deactivating NFC correlation")
            self.nfc_correlation_mode = False
            self.active_rf_threat = None
            self.led_nfc.off()
            
            # Send correlation timeout event to server
            timeout_event = {
                'type': 'nfc_correlation_timeout',
                'timestamp': time.time(),
                'reason': 'timeout'
            }
            await self.send_to_server(timeout_event)
    
    async def generate_security_alert(self, detection, context):
        """Generate and send security alert"""
        alert = {
            'type': 'security_alert',
            'alert_id': "alert_{}_{}".format(int(time.time()), self.detection_count),
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
        signal_type = detection.get('event_type', 'unknown')
        threat_level = detection.get('threat_level', 0)
        power_db = detection.get('power_db', 0)
        print("[ALERT] SECURITY ALERT: {} detected!".format(signal_type))
        if not isinstance(threat_level, (float, int, str)):
            print("[DEBUG] Unexpected threat_level type in alert:", type(threat_level), threat_level)
        if isinstance(threat_level, (float, int)):
            print("   Threat Level: {:.2f}".format(threat_level))
        else:
            print("   Threat Level: {}".format(threat_level))
        if not isinstance(power_db, (float, int)):
            print("[DEBUG] Unexpected power_db type in alert:", type(power_db), power_db)
        if isinstance(power_db, (float, int)):
            print("   Power: {:.1f} dBm".format(power_db))
        else:
            print("   Power: {}".format(power_db))
        await self.send_to_server(alert)
        self.log_alert_locally(alert)

    def get_recommended_action(self, detection):
        """Get recommended action based on detection type"""
        signal_type = detection.get('event_type', 'unknown')
        threat_level = detection.get('threat_level', 0)
        if signal_type == 'potential_jamming':
            return 'immediate_investigation_required'
        elif signal_type == 'key_fob_transmission' and isinstance(threat_level, (float, int)) and threat_level > 0.8:
            return 'verify_legitimate_key_usage'
        elif isinstance(threat_level, (float, int)) and threat_level > 0.7:
            return 'monitor_closely'
        else:
            return 'log_and_continue'

    def log_alert_locally(self, alert):
        """Log alert to local storage"""
        print("LOCAL LOG: {} - {}".format(alert['alert_id'], alert['detection_details']['event_type']))

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
        """Handle NFC tag/card detection with RF correlation support"""
        uid_hex = [hex(b) for b in uid]
        uid_str = ':'.join(uid_hex)
        print("NFC detected: UID = " + uid_str)
        
        # Visual feedback for NFC detection
        self.led_nfc.off()
        await asyncio.sleep(0.2)
        self.led_nfc.on()
        
        # Prepare basic NFC data
        nfc_data = {
            'type': 'nfc_detection',
            'timestamp': time.time(),
            'uid': uid_hex,
            'uid_length': len(uid),
            'detection_context': 'automotive_monitoring'
        }
        
        # Check for RF threat correlation
        if self.nfc_correlation_mode and self.active_rf_threat:
            print(f"[CORRELATION] NFC detection during RF threat: {self.active_rf_threat.get('event_type', 'unknown')}")
            
            # Generate enhanced correlated security event with combined RF-NFC threat structures
            correlated_event = self.create_correlated_security_event(self.active_rf_threat, nfc_data)
            
            await self.send_to_server(correlated_event)
            
            # Visual indication of correlation
            for _ in range(5):
                self.led_alert.on()
                self.led_nfc.on()
                await asyncio.sleep(0.1)
                self.led_alert.off()
                self.led_nfc.off()
                await asyncio.sleep(0.1)
            self.led_nfc.on()  # Restore NFC LED state
        else:
            # Send regular NFC detection event
            await self.send_to_server(nfc_data)
    
    def create_correlated_security_event(self, rf_threat, nfc_detection):
        """Create combined RF-NFC threat event structures with technical evidence and threat escalation"""
        # Calculate threat escalation based on both RF and NFC characteristics
        rf_threat_level = rf_threat.get('threat_level', 0)
        if isinstance(rf_threat_level, str):
            # Convert string threat levels to numeric values
            threat_mapping = {'benign': 0.1, 'suspicious': 0.5, 'malicious': 0.9}
            rf_threat_level = threat_mapping.get(rf_threat_level.lower(), 0.5)
        
        # Enhanced threat escalation for correlated events (higher than either individual threat)
        base_threat_level = max(rf_threat_level, 0.6)  # Minimum 0.6 for any correlation
        escalated_threat_level = min(1.0, base_threat_level + 0.3)  # Escalate by 0.3 (capped at 1.0)
        
        # Collect technical evidence for multi-modal attacks
        technical_evidence = self.collect_technical_evidence(rf_threat, nfc_detection)
        
        # Generate recommended action for correlated threats
        recommended_action = self.get_correlated_recommended_action(rf_threat, nfc_detection)
        
        # Create combined RF-NFC threat event structure
        correlated_event = {
            'type': 'correlated_security_event',
            'event_id': "correlated_{}_{}".format(int(time.time()), self.detection_count),
            'timestamp': time.time(),
            'rf_threat': rf_threat,
            'nfc_detection': nfc_detection,
            'correlation_type': 'rf_nfc_proximity_attack',
            'threat_level': escalated_threat_level,
            'threat_category': 'multi_modal_attack',
            'technical_evidence': technical_evidence,
            'recommended_action': recommended_action,
            'confidence_score': self.calculate_correlation_confidence(rf_threat, nfc_detection)
        }
        
        return correlated_event
    
    def collect_technical_evidence(self, rf_threat, nfc_detection):
        """Collect technical evidence for multi-modal attacks"""
        evidence = {
            'rf_evidence': {
                'signal_type': rf_threat.get('event_type', 'unknown'),
                'frequency_mhz': rf_threat.get('frequency_mhz', 0),
                'power_db': rf_threat.get('power_db', 0),
                'timing_characteristics': rf_threat.get('timing_analysis', {}),
                'modulation_type': rf_threat.get('modulation', 'unknown')
            },
            'nfc_evidence': {
                'uid': nfc_detection.get('uid', []),
                'uid_length': nfc_detection.get('uid_length', 0),
                'detection_timestamp': nfc_detection.get('timestamp', 0)
            },
            'correlation_evidence': {
                'time_delta_seconds': time.time() - rf_threat.get('timestamp', time.time()),
                'proximity_indicators': ['rf_nfc_temporal_correlation', 'multi_modal_attack_pattern']
            }
        }
        
        return evidence
    
    def get_correlated_recommended_action(self, rf_threat, nfc_detection):
        """Generate recommended action for correlated threats"""
        rf_threat_type = rf_threat.get('event_type', 'unknown')
        rf_threat_level = rf_threat.get('threat_level', 0)
        
        if isinstance(rf_threat_level, str):
            threat_mapping = {'benign': 0.1, 'suspicious': 0.5, 'malicious': 0.9}
            rf_threat_level = threat_mapping.get(rf_threat_level.lower(), 0.5)
        
        # High confidence multi-modal attack
        if rf_threat_level > 0.8:
            return 'immediate_security_investigation_required'
        elif rf_threat_type in ['replay_attack', 'brute_force']:
            return 'enhanced_monitoring_and_alert_security_team'
        else:
            return 'log_correlated_event_and_continue_monitoring'
    
    def calculate_correlation_confidence(self, rf_threat, nfc_detection):
        """Calculate confidence score for the correlation"""
        # Base confidence on temporal proximity (NFC detected during correlation window)
        temporal_confidence = 0.8  # High confidence since NFC was detected during correlation mode
        
        # Adjust based on RF threat level
        rf_threat_level = rf_threat.get('threat_level', 0)
        if isinstance(rf_threat_level, str):
            threat_mapping = {'benign': 0.1, 'suspicious': 0.5, 'malicious': 0.9}
            rf_threat_level = threat_mapping.get(rf_threat_level.lower(), 0.5)
        
        threat_confidence = min(1.0, rf_threat_level + 0.2)  # Boost confidence based on RF threat
        
        # Combined confidence score
        combined_confidence = (temporal_confidence + threat_confidence) / 2.0
        return round(combined_confidence, 2)

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
    """Main execution function for Automotive Security Pico POC"""
    print("[SECURITY PICO] - Automotive Security Pico - POC Mode")
    print("=" * 40)
    pico = AutomotiveSecurityPico()
    print("Connecting to WiFi...")
    if not pico.connect_wifi():
        print("[FAIL] WiFi connection failed - cannot proceed")
        return
    print("[OK] WiFi connected")
    print("Connecting to signal server...")
    if not await pico.connect_to_server(SERVER_IP, SERVER_PORT):
        print("[FAIL] Server connection failed - cannot proceed")
        return
    print("[OK] Connected to signal server")
    print("[ACTIVE] Automotive Security Pico is now active")
    tasks = [
        asyncio.create_task(pico.process_server_messages()),
        asyncio.create_task(pico.monitor_nfc()),
        asyncio.create_task(pico.heartbeat_monitor())
    ]
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("\n[STOP] Shutting down Automotive Security Pico...")
    except Exception as e:
        print("[FAIL] Critical error: {}".format(e))
    finally:
        if pico.server_socket:
            pico.server_socket.close()
        pico.led_rf.off()
        pico.led_nfc.off()
        pico.led_alert.off()
        print("[OK] Shutdown complete")

# Only run main if this file is executed directly (not imported)
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except AttributeError:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())