"""
event_logic.py

Unified detection/event assignment logic for both real SDR packets and mock/demo event generation.
Handles event type assignment, threat level/color mapping, and replay/attack logic.
Demo-specific behaviors (aggressive attack simulation, forced replay attack marking, etc.) are toggleable via the demo_mode flag.

# TODO: Design logic and dependencies to be compatible with a future Micropython port for Raspberry Pi Pico deployment.
"""
from datetime import datetime
import random

# DETAILS_MAP (should be imported from a shared config if possible)
DETAILS_MAP = {
    "RF Unlock": {"desc": "RF unlock signal detected", "example": "Key fob unlock"},
    "RF Lock": {"desc": "RF lock signal detected", "example": "Key fob lock"},
    "Replay Attack": {"desc": "Replay attack detected", "example": "Captured unlock replayed"},
    "Jamming Attack": {"desc": "RF jamming detected", "example": "Jammer device active"},
    "Brute Force": {"desc": "Brute force attempt detected", "example": "Repeated unlock attempts"},
    "Unknown": {"desc": "Unknown RF signal", "example": "Unclassified burst"},
    # Add all other event types as needed
}

THREAT_COLOR_MAP = {
    "Benign": "green",
    "Malicious": "red",
    "Suspicious": "orange"
}

ALL_EVENT_TYPES = list(DETAILS_MAP.keys())


def analyze_event(packet, *, demo_mode=False, event_types=None, details_map=None):
    """
    Analyze an input packet (real or mock) and return a detection event dict
    with assigned event type, threat level, and all required fields.

    Args:
        packet (dict): The input packet, either from SDR hardware or a mock generator.
        demo_mode (bool): If True, applies demo-specific logic (aggressive attack simulation, always-malicious replay, etc).
        event_types (list): Optional. List of all event types to support (defaults to DETAILS_MAP keys).
        details_map (dict): Optional. Event details mapping for UI (defaults to DETAILS_MAP).

    Returns:
        dict: Detection event with all required fields (event_type, threat_level, color, timestamp, etc).
    """
    if event_types is None:
        event_types = ALL_EVENT_TYPES
    if details_map is None:
        details_map = DETAILS_MAP

    # --- DEMO MODE: Aggressive cycling and forced malicious logic ---
    # Define ambiguous event types for demo randomization
    AMBIGUOUS_EVENT_TYPES = ("Other",)

    if demo_mode:
        event_type = packet.get("event_type")
        if not event_type or event_type not in event_types:
            event_type = random.choice(event_types)
        if event_type == "Replay Attack":
            threat_level = "Malicious"
        elif event_type == "Unknown":
            threat_level = "Suspicious"
        elif event_type in ("Jamming Attack", "Brute Force"):
            threat_level = "Malicious"
        elif event_type in ("RF Unlock", "RF Lock", "NFC Scan", "NFC Tag Present"):
            threat_level = "Benign"
        elif event_type in AMBIGUOUS_EVENT_TYPES:
            threat_level = random.choices(
                ["Benign", "Suspicious", "Malicious"],
                weights=[1, 2, 4],
                k=1
            )[0]
        else:
            threat_level = "Benign"
        # Color mapping
        color = THREAT_COLOR_MAP.get(threat_level, "white")
        # Timestamp
        timestamp = packet.get("timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Compose event dict
        event = {
            "event_type": event_type,
            "threat_level": threat_level,
            "color": color,
            "timestamp": timestamp,
            "details": details_map.get(event_type, {}),
            # Pass through other fields
            **{k: v for k, v in packet.items() if k not in ["event_type", "threat_level", "color", "timestamp", "details"]}
        }
        return event

    else:
        # --- REAL PACKET ANALYSIS LOGIC ---
        # TODO: replace with real SDR analysis logic
        event_type = packet.get("event_type")
        if not event_type or event_type not in event_types:
            # TODO: classify based on packet features
            # (Replace with real logic, e.g., burst pattern, freq, etc.)
            if packet.get("is_replay"):
                event_type = "Replay Attack"
            elif packet.get("is_jamming"):
                event_type = "Jamming Attack"
            elif packet.get("is_brute"):
                event_type = "Brute Force"
            elif packet.get("is_unlock"):
                event_type = "RF Unlock"
            elif packet.get("is_lock"):
                event_type = "RF Lock"
            else:
                event_type = "Unknown"
        # Threat logic
        if event_type == "Replay Attack":
            threat_level = "Malicious"
        elif event_type == "Unknown":
            threat_level = "Suspicious"
        elif event_type in ("Jamming Attack", "Brute Force"):
            threat_level = "Malicious"
        else:
            # TODO: Assign based on packet metrics (RSSI, freq, etc.)
            rssi = packet.get("rssi", -60)
            threat_level = "Benign" if rssi > -50 else "Suspicious"

        # Color mapping
        color = THREAT_COLOR_MAP.get(threat_level, "white")
        # Timestamp
        timestamp = packet.get("timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Compose event dict
        event = {
            "event_type": event_type,
            "threat_level": threat_level,
            "color": color,
            "timestamp": timestamp,
            "details": details_map.get(event_type, {}),
            # Pass through other fields
            **{k: v for k, v in packet.items() if k not in ["event_type", "threat_level", "color", "timestamp", "details"]}
        }
        return event

# TODO: Add more sophisticated analysis logic as needed for real SDR packets.
#       Ensure all event types in DETAILS_MAP are covered.
#       Keep legacy detection code in repo, but do not use in main pipeline.
