"""
cli_dashboard_detection_adapter.py

Adapter for integrating old_backend detection logic and mock hardware into the CLI dashboard's mock event generation.
Provides functions to generate plausible detection events using the project's legacy detection modules and hardware mocks.

This file is intended to be imported by cli_dashboard.py to support realistic mock/demo mode.
"""
"""
cli_dashboard_detection_adapter.py

Adapter for generating detection events for the CLI dashboard using only the new backend detection and hardware modules.
No legacy imports or random event logic remain. All event types and threat levels are logic-driven and documented.
"""
from datetime import datetime
from itertools import count
from detection.packet import Packet
from detection.security_analyzer import SecurityAnalyzer
from hardware.mock.rf import MockRFInterface
from hardware.mock.nfc import MockNFCInterface

# Counter for event numbering
_counter = count(1)

# Security analyzer instance (reuse across calls)
_analyzer = SecurityAnalyzer()

# Event type mapping based on payload/tag
EVENT_TYPE_MAP = {
    b'UNLOCK': "RF Unlock",
    b'LOCK': "RF Lock",
    b'NFC_SCAN': "NFC Scan",
    b'REPLAY_ATTACK': "Replay Attack",
    b'JAMMER': "Jamming",
    b'BRUTE': "Multiple Unlock Attempts",
    b'NORMAL': "Unknown"
}

NFC_EVENT_TYPE = "NFC Tag Present"

DETAILS_MAP = {
    "RF Unlock": "Detected valid unlock signal.",
    "RF Lock": "Detected valid lock signal.",
    "NFC Scan": "NFC tag read.",
    "Jamming": "RF jamming pattern detected!",
    "Replay Attack": "Replay attack signature detected.",
    "Multiple Unlock Attempts": "Multiple unlock attempts detected.",
    "Unknown": "Unrecognized RF burst.",
    "NFC Tag Present": "NFC tag present and read."
}

SOURCES = ["Pico-1", "Pico-2", "Simulated", "TestBench"]


def generate_detection_event():
    """
    Generate a detection event using mock hardware and logic-driven analysis.
    Aggressively cycles through all event types for demo coverage, including all types in DETAILS_MAP.
    Returns:
        dict: Detection event for dashboard
    """
    # Aggressive demo cycling: ensure every event type is shown in sequence
    event_types = list(DETAILS_MAP.keys())
    event_idx = next(_counter) % len(event_types)
    forced_event_type = event_types[event_idx]

    # Map forced event type to plausible payload/tag for analyzer logic
    forced_payload_map = {
        "RF Unlock": b'UNLOCK',
        "RF Lock": b'LOCK',
        "NFC Scan": b'NFC_SCAN',
        "Jamming": b'JAMMER',
        "Replay Attack": b'REPLAY_ATTACK',
        "Multiple Unlock Attempts": b'BRUTE',
        "Unknown": b'NORMAL',
        "NFC Tag Present": b'NFC_SCAN',  # Will set tag_id below
    }
    payload = forced_payload_map.get(forced_event_type, b'NORMAL')

    # Get mock RF and NFC data
    rf = MockRFInterface()
    nfc = MockNFCInterface()
    rf_metrics = rf.get_signal_metrics()
    nfc_data = nfc.get_nfc_data()

    # For NFC Tag Present, force a tag_id
    tag_id = nfc_data.get('tag_id')
    if forced_event_type == "NFC Tag Present":
        tag_id = f"DEMO_TAG_{event_idx}"

    # For other types, sometimes force anomaly conditions for demo
    import time
    if forced_event_type == "Replay Attack":
        # Simulate replay by using a payload/freq/rssi combo likely to trigger analyzer
        rssi = -55 + (event_idx % 5) * 2
        freq = rf.frequency
        # Inject a previous packet with same payload/freq, different rssi, and valid timestamp
        prev_packet = Packet(payload=b'REPLAY_ATTACK', freq=freq, rssi=rssi + 10, snr=20, tag_id=None)
        prev_packet.timestamp = time.time() - 2  # within replay window
        _analyzer.packet_history.append(prev_packet)
    elif forced_event_type == "Jamming":
        # Simulate high packet rate by appending many packets to analyzer history, all with valid timestamps
        now = time.time()
        for i in range(_analyzer.jam_detection_threshold + 1):
            p = Packet(payload=b'JAMMER', freq=rf.frequency, rssi=-50, snr=20, tag_id=None)
            p.timestamp = now - (i * 0.005)  # spread over a short window
            _analyzer.packet_history.append(p)
        rssi = -50
        freq = rf.frequency
    elif forced_event_type == "Multiple Unlock Attempts":
        # Simulate brute force by adding similar packets to history, all with valid timestamps
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

    # Build packet for analyzer
    packet = Packet(
        payload=payload,
        freq=freq,
        rssi=rssi,
        snr=rf_metrics['snr'],
        tag_id=tag_id
    )
    # Analyze packet
    report = _analyzer.analyze_packet(packet)
    event_type = forced_event_type
    details = DETAILS_MAP.get(event_type, "Automotive event detected.")
    now = datetime.now().strftime("%H:%M:%S")

    # --- DEMO LOGIC: Ensure correct threat levels for demo events ---
    threat = report.threat_level.name.capitalize()
    # Always mark Replay Attack as Malicious for demo
    if event_type == "Replay Attack":
        threat = "Malicious"
    # For demo, force every 2nd attack event to be malicious (except Replay Attack, which is always Malicious)
    elif event_type in ["Jamming", "Multiple Unlock Attempts"] and event_idx % 2 == 1:
        threat = "Malicious"
    # Always mark Unknown as Suspicious
    if event_type == "Unknown":
        threat = "Suspicious"

    event = {
        "time": now,
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
