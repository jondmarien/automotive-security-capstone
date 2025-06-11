"""
cli_dashboard_detection_adapter.py

Adapter for generating detection events for the CLI dashboard using only the new backend detection logic.
All event types and threat levels are logic-driven and demo logic is unified with real detection logic.
"""
from datetime import datetime
from itertools import count
import random
from detection.event_logic import analyze_event

# Counter for event numbering
_counter = count(1)

DETAILS_MAP = {
    "RF Unlock": "Detected valid unlock signal.",
    "RF Lock": "Detected valid lock signal.",
    "NFC Scan": "NFC tag read.",
    "Jamming Attack": "RF jamming pattern detected!",
    "Replay Attack": "Replay attack signature detected.",
    "Brute Force": "Multiple unlock attempts detected.",
    "Unknown": "Unrecognized RF burst.",
    "NFC Tag Present": "NFC tag present and read."
}

SOURCES = ["Pico-1", "Pico-2", "Simulated", "TestBench"]


def generate_detection_event():
    """
    Generate a detection event using mock hardware and unified logic-driven analysis.
    Uses analyze_event() from detection.event_logic with demo_mode=True.
    Returns:
        dict: Detection event for dashboard (with keys: type, threat, time, source, details)
    """
    # Generate a mock packet with plausible fields (simulate SDR or NFC payload)
    event_types = list(DETAILS_MAP.keys())
    event_idx = next(_counter) % len(event_types)
    forced_event_type = event_types[event_idx]
    mock_packet = {
        "event_type": forced_event_type,
        "rssi": random.randint(-80, -30),
        "freq": random.choice([433.92, 315.0, 868.0]),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "is_replay": forced_event_type == "Replay Attack",
        "is_jamming": forced_event_type == "Jamming Attack",
        "is_brute": forced_event_type == "Brute Force",
        "is_unlock": forced_event_type == "RF Unlock",
        "is_lock": forced_event_type == "RF Lock",
    }
    event = analyze_event(mock_packet, demo_mode=True)
    # Map to dashboard keys: type, threat, time, source, details
    return {
        "type": event.get("event_type", "Unknown"),
        "threat": event.get("threat_level", "Suspicious"),
        "time": event.get("timestamp"),
        "source": SOURCES[event_idx % len(SOURCES)],
        "details": DETAILS_MAP.get(event.get("event_type", "Unknown"), "Automotive event detected."),
        # Optionally include any other fields for debugging/demo
        **{k: v for k, v in event.items() if k not in ["event_type", "threat_level", "timestamp", "details"]}
    }

# -----------------------------------------------------------------------------
# Legacy Detection Logic and Mock Hardware (DEPRECATED/UNUSED)
# This section is preserved for reference and possible future use.
# -----------------------------------------------------------------------------

try:
    from detection.packet import Packet
    from detection.security_analyzer import SecurityAnalyzer
    from hardware.mock.rf import MockRFInterface
    from hardware.mock.nfc import MockNFCInterface
except ImportError:
    Packet = SecurityAnalyzer = MockRFInterface = MockNFCInterface = None

# Example legacy event generator (NOT USED):
def legacy_generate_detection_event():
    """
    Legacy event generator using SecurityAnalyzer and mock hardware. Deprecated.
    """
    import time
    if not (Packet and SecurityAnalyzer and MockRFInterface and MockNFCInterface):
        return None
    _analyzer = SecurityAnalyzer()
    # Cycle through event types for demo
    event_types = [
        "RF Unlock", "RF Lock", "NFC Scan", "Jamming Attack",
        "Replay Attack", "Brute Force", "Unknown", "NFC Tag Present"
    ]
    event_idx = next(_counter) % len(event_types)
    forced_event_type = event_types[event_idx]
    forced_payload_map = {
        "RF Unlock": b'UNLOCK',
        "RF Lock": b'LOCK',
        "NFC Scan": b'NFC_SCAN',
        "Jamming Attack": b'JAMMER',
        "Replay Attack": b'REPLAY_ATTACK',
        "Brute Force": b'BRUTE',
        "Unknown": b'NORMAL',
        "NFC Tag Present": b'NFC_SCAN',
    }
    payload = forced_payload_map.get(forced_event_type, b'NORMAL')
    rf = MockRFInterface()
    nfc = MockNFCInterface()
    rf_metrics = rf.get_signal_metrics()
    nfc_data = nfc.get_nfc_data()
    tag_id = nfc_data.get('tag_id')
    if forced_event_type == "NFC Tag Present":
        tag_id = f"DEMO_TAG_{event_idx}"
    # Simulate analyzer state for demo attacks
    if forced_event_type == "Replay Attack":
        rssi = -55 + (event_idx % 5) * 2
        freq = rf.frequency
        prev_packet = Packet(payload=b'REPLAY_ATTACK', freq=freq, rssi=rssi + 10, snr=20, tag_id=None)
        prev_packet.timestamp = time.time() - 2
        _analyzer.packet_history.append(prev_packet)
    elif forced_event_type == "Jamming Attack":
        now = time.time()
        for i in range(_analyzer.jam_detection_threshold + 1):
            p = Packet(payload=b'JAMMER', freq=rf.frequency, rssi=-50, snr=20, tag_id=None)
            p.timestamp = now - (i * 0.005)
            _analyzer.packet_history.append(p)
        rssi = -50
        freq = rf.frequency
    elif forced_event_type == "Brute Force":
        now = time.time()
        for i in range(_analyzer.brute_force_threshold + 1):
            p = Packet(payload=b'BRUTE', freq=rf.frequency, rssi=-58, snr=18, tag_id=None)
            p.timestamp = now - (i * 0.5)
            _analyzer.packet_history.append(p)
        rssi = -58
        freq = rf.frequency
    else:
        rssi = rf_metrics['rssi']
        freq = rf_metrics['frequency']
    packet = Packet(
        payload=payload,
        freq=freq,
        rssi=rssi,
        snr=rf_metrics['snr'],
        tag_id=tag_id
    )
    report = _analyzer.analyze_packet(packet)
    event_type = forced_event_type
    details = DETAILS_MAP.get(event_type, "Automotive event detected.")
    now_str = datetime.now().strftime("%H:%M:%S")
    threat = report.threat_level.name.capitalize()
    if event_type == "Replay Attack":
        threat = "Malicious"
    elif event_type in ["Jamming Attack", "Brute Force"] and event_idx % 2 == 1:
        threat = "Malicious"
    if event_type == "Unknown":
        threat = "Suspicious"
    event = {
        "time": now_str,
        "type": event_type,
        "threat": threat,
        "source": SOURCES[event_idx % len(SOURCES)],
        "details": f"{details} (event #{event_idx + 1})",
        "rssi": packet.rssi,
        "snr": packet.snr,
        "frequency": packet.freq,
        "nfc_tag": packet.tag_id,
        "reason": report.reason
    }
    return event
