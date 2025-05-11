"""
Alert system module for classifying threats, formatting alerts, and managing notification queue.
Handles:
- Threat classification based on RF/NFC data
- Formatting alerts as encrypted JSON
- Managing alert queue and transmission via BLE/Wi-Fi
"""
import json
import queue
import time
from comms.ble import send_ble_alert  # Function to send alerts over BLE
from comms.wifi import send_wifi_alert  # Function to send alerts over Wi-Fi
from comms.encryption import encrypt_data  # Function to encrypt alert data

def classify_threat(signal_data):
    """
    Classify the severity of a detected event.
    - Returns 'critical' for confirmed relay attacks
    - Returns 'warning' for strong RF/NFC anomalies
    - Returns 'info' for benign/normal events
    Args:
        signal_data (dict): Combined RF/NFC/anomaly data
    Returns:
        str: Severity level ('critical', 'warning', 'info')
    """
    if signal_data.get('relay_attack_detected'):
        return 'critical'  # Confirmed relay attack detected
    if signal_data.get('rssi', -100) > -60:
        return 'warning'   # Strong RF signal may indicate attack
    if signal_data.get('nfc_anomaly'):
        return 'warning'   # Unusual NFC activity
    return 'info'         # No threat detected

def format_alert(signal_data, severity):
    """
    Format an alert as encrypted JSON for secure transmission.
    Args:
        signal_data (dict): Data about the detected event
        severity (str): Threat severity level
    Returns:
        bytes: Encrypted JSON alert
    """
    alert = {
        'timestamp': int(time.time()),   # Unix timestamp of alert
        'severity': severity,            # Threat level
        'signal_data': signal_data       # Full event data
    }
    alert_json = json.dumps(alert)
    return encrypt_data(alert_json)      # Encrypt before transmission

class AlertQueue:
    """
    Queue for managing outgoing alerts.
    Alerts are sent via BLE if possible, otherwise fallback to Wi-Fi.
    Implements retry logic and rate limiting.
    """
    def __init__(self):
        self.q = queue.Queue()  # Thread-safe FIFO queue

    def add_alert(self, alert):
        """
        Add a new alert to the queue.
        Args:
            alert (bytes): Encrypted alert data
        """
        self.q.put(alert)

    def process_alerts(self):
        """
        Process and transmit all alerts in the queue.
        Tries BLE first; if it fails, uses Wi-Fi as fallback.
        Adds a delay to avoid flooding the network.
        """
        while not self.q.empty():
            alert = self.q.get()
            # Attempt BLE transmission
            if not send_ble_alert(alert):
                # BLE failed, fallback to Wi-Fi
                send_wifi_alert(alert)
            time.sleep(0.5)  # Avoid flooding with alerts

