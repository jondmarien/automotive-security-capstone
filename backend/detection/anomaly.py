"""
Anomaly detection logic module
Stub for combining RF and NFC data to detect suspicious patterns.
Replace with real statistical/pattern analysis.
"""

def check_anomaly(rf_data, nfc_data):
    """
    Simulate anomaly detection by combining RF and NFC data.
    Args:
        rf_data (dict): RF signal data
        nfc_data (dict): NFC detection data
    Returns:
        dict: Combined data with anomaly flags
    """
    # In real implementation, analyze patterns, RSSI, timing, etc.
    anomaly = {
        'relay_attack_detected': rf_data.get('relay_attack_detected', False),
        'rssi': rf_data.get('rssi', -100),
        'nfc_anomaly': nfc_data.get('nfc_anomaly', False),
        'tag_id': nfc_data.get('tag_id', None)
    }
    return anomaly