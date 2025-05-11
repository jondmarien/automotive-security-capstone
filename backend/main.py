"""
Main firmware loop for automotive security dongle.
Integrates RTL-SDR, PN532, detection, and alert system.
"""

from hardware.rtl_sdr import RTLSDR  # RTL-SDR radio interface for RF detection
from hardware.pn532 import PN532      # PN532 module interface for NFC detection
from detection.rf_detection import detect_rf_signals  # Detects RF signals using RTL-SDR
from detection.nfc_detection import detect_nfc        # Detects NFC events using PN532
from detection.anomaly import check_anomaly           # Checks for suspicious patterns
from detection.alert import classify_threat, format_alert, AlertQueue  # Alert system
import logging

# Setup logging for debugging and system status
logger = logging.getLogger("dongle")
logger.setLevel(logging.INFO)

# Initialize hardware interfaces
rtl = RTLSDR()   # RTL-SDR for 315/433 MHz RF detection
nfc = PN532()    # PN532 for 13.56 MHz NFC detection
alert_queue = AlertQueue()  # Queue for managing outgoing alerts

def main_loop():
    """
    Main firmware loop:
    - Continuously polls for RF and NFC events
    - Runs anomaly detection on gathered data
    - Classifies threat severity
    - Formats and queues alerts for transmission
    """
    logger.info("Starting security dongle main loop...")
    while True:
        # Poll RF signals (relay attack detection, etc.)
        rf_data = detect_rf_signals(rtl)
        # Poll NFC events (unauthorized tag detection, etc.)
        nfc_data = detect_nfc(nfc)
        # Analyze combined data for anomalies
        anomaly = check_anomaly(rf_data, nfc_data)
        # Classify the severity of the detected anomaly
        severity = classify_threat(anomaly)
        # Format the alert as encrypted JSON
        alert = format_alert(anomaly, severity)
        # Only queue alerts above 'info' severity
        if severity != 'info':
            alert_queue.add_alert(alert)
        # Process the alert queue (send via BLE/Wi-Fi)
        alert_queue.process_alerts()
        # TODO: Add sleep or power management for efficiency

if __name__ == "__main__":
    # Entry point when running as a script
    main_loop()