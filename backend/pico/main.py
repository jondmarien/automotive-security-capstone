"""
main.py (Pico Client)

MicroPython code for Raspberry Pi Pico W.
Connects to WiFi and a backend TCP event server to receive automotive security detection events.
Handles event parsing, status LEDs, and NFC detection via PN532.
Sends NFC and security events back to the backend server.

Designed for use in the Automotive Security Capstone POC project.

Example usage:
    Copy this file to your Pico, set config.py with your network settings, and run main().
"""
import network
import socket
import json
import time
import uasyncio as asyncio
from machine import Pin, SPI, Timer
import NFC_PN532 as nfc

# Import configuration
try:
    import config
    print("Configuration loaded successfully")
except ImportError:
    print("ERROR: config.py not found! Please create config.py with your settings.")
    print("See config.py template for required settings.")
    import sys
    sys.exit()

class AutomotiveSecurityPico:
    def __init__(self):
        self.wifi_connected = False
        self.server_socket = None
        self.signal_buffer = []
        self.pn532 = None
        self.detection_count = 0
        
        # Status LEDs using config
        self.led_red = Pin(config.LED_PIN_RED, Pin.OUT)      # Malicious threats
        self.led_yellow = Pin(config.LED_PIN_YELLOW, Pin.OUT) # Suspicious activity
        self.led_green = Pin(config.LED_PIN_GREEN, Pin.OUT)   # Normal operation
        
        # NFC correlation system
        self.nfc_correlation_mode = False
        self.active_rf_threat = None
        self.correlation_timeout = 30  # seconds
        self.correlation_timer = None
        
        # Initialize systems
        if config.NFC_ENABLED:
            self.init_nfc()
        self.init_status_display()

    def init_nfc(self):
        """Initialize PN532 NFC module using config settings"""
        try:
            # Use config pins for NFC SPI connection
            spi_dev = SPI(0, baudrate=1000000, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
            cs = Pin(17, Pin.OUT)
            cs.on()
            
            # Initialize PN532 with reset pin if available
            reset_pin = Pin(config.NFC_SDA_PIN, Pin.OUT) if hasattr(config, 'NFC_RESET_PIN') else None
            pn532 = nfc.PN532(spi_dev, cs, reset=reset_pin)
            
            ic, ver, rev, support = pn532.get_firmware_version()
            print("PN532 initialized: v{}.{}".format(ver, rev))
            pn532.SAM_configuration()
            self.pn532 = pn532
            
            # NFC ready indicator
            self.led_green.on()
            print("NFC module ready for automotive security monitoring")
            
        except Exception as e:
            print("NFC initialization failed: {}".format(e))
            # Error indication with red LED
            for _ in range(5):
                self.led_red.on()
                time.sleep(0.1)
                self.led_red.off()
                time.sleep(0.1)

    def init_status_display(self):
        """Initialize status display sequence"""
        print("Automotive Security Pico W - Initializing...")
        
        # Startup LED sequence
        leds = [self.led_green, self.led_yellow, self.led_red]
        for led in leds:
            led.on()
            time.sleep(0.3)
            led.off()
        
        # Green LED indicates system ready
        self.led_green.on()
        print("Status LEDs initialized")

    def connect_wifi(self):
        """Connect to WiFi using config settings"""
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        
        print("Connecting to WiFi: {}".format(config.WIFI_SSID))
        wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        
        # Wait for connection with timeout
        timeout = getattr(config, 'WIFI_TIMEOUT', 30)
        for i in range(timeout):
            if wlan.isconnected():
                break
            print(".", end="")
            time.sleep(1)
            
            # Blink yellow LED while connecting
            if i % 2 == 0:
                self.led_yellow.on()
            else:
                self.led_yellow.off()
        
        if wlan.isconnected():
            self.wifi_connected = True
            ip_info = wlan.ifconfig()
            print("\nWiFi Connected!")
            print("IP Address: {}".format(ip_info[0]))
            print("Subnet Mask: {}".format(ip_info[1]))
            print("Gateway: {}".format(ip_info[2]))
            
            # Green LED indicates successful connection
            self.led_yellow.off()
            self.led_green.on()
            return True
        else:
            print("\nWiFi connection failed!")
            # Red LED indicates connection failure
            self.led_yellow.off()
            self.led_red.on()
            return False

    async def connect_to_server(self, server_ip=None, server_port=None):
        """Connect to computer's signal processing server using config"""
        # Use config values if not provided
        if server_ip is None:
            server_ip = config.TCP_HOST
        if server_port is None:
            server_port = config.TCP_PORT
            
        max_attempts = 5
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            try:
                print('Connecting to server {}:{} (attempt {})'.format(server_ip, server_port, attempt))
                
                # Blink yellow LED during connection attempts
                self.led_yellow.on()
                
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                timeout = getattr(config, 'TCP_TIMEOUT', 10)
                self.server_socket.settimeout(timeout)
                self.server_socket.connect((server_ip, server_port))
                
                print("Connected to automotive security server!")
                
                # Send handshake with device capabilities
                handshake = {
                    'type': 'handshake',
                    'device_id': 'automotive_pico_w_001',
                    'capabilities': ['nfc_detection', 'rf_correlation', 'alert_generation', 'multi_modal_detection'],
                    'firmware_version': '2.0.0',
                    'nfc_enabled': config.NFC_ENABLED,
                    'debug_mode': getattr(config, 'DEBUG_MODE', False)
                }
                await self.send_to_server(handshake)
                
                # Green LED indicates successful connection
                self.led_yellow.off()
                self.led_green.on()
                return True
                
            except Exception as e:
                print("Server connection attempt {} failed: {}".format(attempt, e))
                if self.server_socket:
                    self.server_socket.close()
                    self.server_socket = None
                
                # Red LED blink for connection failure
                self.led_yellow.off()
                self.led_red.on()
                await asyncio.sleep(0.5)
                self.led_red.off()
                
                # Exponential backoff
                reconnect_interval = getattr(config, 'RECONNECT_INTERVAL', 5)
                await asyncio.sleep(min(reconnect_interval * attempt, 30))
        
        print("Failed to connect to server after {} attempts".format(max_attempts))
        self.led_red.on()  # Solid red for complete failure
        return False

    async def send_to_server(self, data):
        """Send JSON data to server with proper formatting"""
        try:
            if self.server_socket:
                # Add timestamp if not present
                if 'timestamp' not in data:
                    data['timestamp'] = time.time()
                
                # Convert to JSON with newline delimiter
                json_data = json.dumps(data) + '\n'
                self.server_socket.send(json_data.encode('utf-8'))
                
                if getattr(config, 'DEBUG_MODE', False):
                    print("Sent to server: {}".format(data.get('type', 'unknown')))
                    
        except Exception as e:
            print("Failed to send to server: {}".format(e))
            self.server_socket = None
            # Red LED indicates communication failure
            self.led_red.on()
            await asyncio.sleep(0.2)
            self.led_red.off()

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
        """Process signal detection from RTL-SDR with enhanced LED indicators"""
        self.detection_count += 1
        
        # Yellow LED indicates RF signal processing
        self.led_yellow.on()
        
        detections = detection_data.get('detections', [])
        high_threat_count = 0
        
        for detection in detections:
            threat_level = detection.get('threat_level', 0)
            signal_type = detection.get('event_type', 'unknown')
            
            # Debug output if enabled
            if getattr(config, 'DEBUG_MODE', False):
                print("Detection {}: {} (threat: {})".format(self.detection_count, signal_type, threat_level))
            
            # Check for high threat levels
            is_high_threat = False
            if isinstance(threat_level, (float, int)) and threat_level > 0.7:
                is_high_threat = True
            elif isinstance(threat_level, str) and threat_level.lower() in ("high", "critical", "suspicious", "malicious"):
                is_high_threat = True
            
            if is_high_threat:
                high_threat_count += 1
                await self.generate_security_alert(detection, detection_data)
        
        # Visual threat indication
        if high_threat_count > 0:
            # Red LED flashing for high threats
            for _ in range(high_threat_count * 2):
                self.led_red.on()
                await asyncio.sleep(0.1)
                self.led_red.off()
                await asyncio.sleep(0.1)
            
            # Activate NFC correlation for high-threat events
            if config.NFC_ENABLED:
                await self.activate_nfc_correlation(detections)
        
        # Return to normal state
        await asyncio.sleep(0.3)
        self.led_yellow.off()
        self.led_green.on()  # Back to normal operation

    async def activate_nfc_correlation(self, detections):
        """Activate NFC scanning when high-threat RF events detected"""
        if not config.NFC_ENABLED or not self.pn532:
            return
            
        print("[NFC CORRELATION] Activating NFC scanning for {} high-threat events".format(len(detections)))
        
        # Set correlation mode active
        self.nfc_correlation_mode = True
        self.active_rf_threat = detections[0] if detections else None  # Store first high-threat detection
        
        # Visual indication of active NFC correlation mode (alternating yellow/red)
        for _ in range(3):
            self.led_yellow.on()
            self.led_red.on()
            await asyncio.sleep(0.2)
            self.led_yellow.off()
            self.led_red.off()
            await asyncio.sleep(0.2)
        
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
            'threat_types': [d.get('event_type', 'unknown') for d in detections],
            'device_id': 'automotive_pico_w_001'
        }
        await self.send_to_server(correlation_event)
    
    async def nfc_correlation_timeout(self):
        """Timeout NFC correlation mode"""
        await asyncio.sleep(self.correlation_timeout)
        
        if self.nfc_correlation_mode:
            print("[NFC CORRELATION] Timeout - deactivating NFC correlation")
            self.nfc_correlation_mode = False
            self.active_rf_threat = None
            
            # Return to normal green LED
            self.led_red.off()
            self.led_yellow.off()
            self.led_green.on()
            
            # Send correlation timeout event to server
            timeout_event = {
                'type': 'nfc_correlation_timeout',
                'timestamp': time.time(),
                'reason': 'timeout',
                'device_id': 'automotive_pico_w_001'
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
        print("NFC detected: UID = {}".format(uid_str))
        
        # Visual feedback for NFC detection (quick yellow flash)
        self.led_yellow.on()
        await asyncio.sleep(0.2)
        self.led_yellow.off()
        
        # Prepare basic NFC data
        nfc_data = {
            'type': 'nfc_detection',
            'timestamp': time.time(),
            'uid': uid_hex,
            'uid_length': len(uid),
            'uid_string': uid_str,
            'detection_context': 'automotive_monitoring',
            'device_id': 'automotive_pico_w_001'
        }
        
        # Check for RF threat correlation
        if self.nfc_correlation_mode and self.active_rf_threat:
            print("[CORRELATION] NFC detection during RF threat: {}".format(
                self.active_rf_threat.get('event_type', 'unknown')))
            
            # Generate enhanced correlated security event
            correlated_event = self.create_correlated_security_event(self.active_rf_threat, nfc_data)
            await self.send_to_server(correlated_event)
            
            # Visual indication of correlation - rapid red/yellow alternating
            for _ in range(8):
                self.led_red.on()
                self.led_yellow.on()
                await asyncio.sleep(0.1)
                self.led_red.off()
                self.led_yellow.off()
                await asyncio.sleep(0.1)
            
            # Deactivate correlation mode after successful correlation
            self.nfc_correlation_mode = False
            self.active_rf_threat = None
            if self.correlation_timer:
                self.correlation_timer.cancel()
                self.correlation_timer = None
            
            print("[CORRELATION] Multi-modal attack detected and reported!")
            
        else:
            # Send regular NFC detection event
            await self.send_to_server(nfc_data)
        
        # Return to normal state
        self.led_green.on()
    
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
    print("=" * 50)
    print("AUTOMOTIVE SECURITY PICO W - CAPSTONE PROJECT")
    print("Real-time RF/NFC Correlation System")
    print("=" * 50)
    
    # Initialize Pico system
    pico = AutomotiveSecurityPico()
    
    # Connect to WiFi
    print("Step 1: Connecting to WiFi...")
    if not pico.connect_wifi():
        print("[FAIL] WiFi connection failed - cannot proceed")
        print("Check config.py for correct WIFI_SSID and WIFI_PASSWORD")
        return
    print("[OK] WiFi connected successfully")
    
    # Connect to signal server
    print("Step 2: Connecting to automotive security server...")
    if not await pico.connect_to_server():
        print("[FAIL] Server connection failed - cannot proceed")
        print("Check config.py for correct TCP_HOST and TCP_PORT")
        print("Ensure the real_hardware_launcher.py is running on your computer")
        return
    print("[OK] Connected to automotive security server")
    
    # Start monitoring tasks
    print("Step 3: Starting monitoring systems...")
    tasks = []
    
    # Always start server message processing and heartbeat
    tasks.append(asyncio.create_task(pico.process_server_messages()))
    tasks.append(asyncio.create_task(pico.heartbeat_monitor()))
    
    # Only start NFC monitoring if enabled
    if config.NFC_ENABLED and pico.pn532:
        tasks.append(asyncio.create_task(pico.monitor_nfc()))
        print("[OK] NFC monitoring enabled")
    else:
        print("[INFO] NFC monitoring disabled or unavailable")
    
    print("=" * 50)
    print("[ACTIVE] Automotive Security Pico W is now monitoring!")
    print("Waiting for RF signals and NFC activity...")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("\n[STOP] Shutting down Automotive Security Pico...")
    except Exception as e:
        print("[FAIL] Critical error: {}".format(e))
        # Red LED for critical error
        pico.led_red.on()
    finally:
        # Cleanup
        if pico.server_socket:
            pico.server_socket.close()
        
        # Turn off all LEDs
        pico.led_red.off()
        pico.led_yellow.off()
        pico.led_green.off()
        
        print("[OK] Automotive Security Pico shutdown complete")

# Only run main if this file is executed directly (not imported)
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except AttributeError:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())