"""
cli_dashboard_detection_adapter.py

Adapter for generating detection events for the CLI dashboard using only the new backend detection logic.
All event types and threat levels are logic-driven and demo logic is unified with real detection logic.

ENHANCED VERSION: Now includes detailed signal analysis features, modulation types, and RF metrics
to support the technical evidence presentation in the enhanced CLI dashboard.
"""
import random
import time
import logging
import json
from datetime import datetime
from itertools import count

from detection.event_logic import analyze_event

# Import performance monitoring
from utils.simple_performance_monitor import get_performance_monitor

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
    Generate a mock detection event for the CLI dashboard.
    Uses unified detection logic for consistency with actual events.
    Enhanced for refactored event enrichment for signal details.
    
    Returns:
        dict: An enhanced detection event with detailed signal features and evidence.
    """
    event_types = list(DETAILS_MAP.keys())
    event_idx = next(_counter) % len(event_types)
    forced_event_type = event_types[event_idx]
    
    # Signal characteristics - enhanced for more detailed visualization
    frequency = random.choice([433.92e6, 315.0e6, 868.0e6, 915.0e6, 2.4e9])
    rssi = random.randint(-80, -30)
    snr = random.randint(8, 25)
    burst_count = random.randint(3, 12)
    
    # More varied modulation types for better visualization testing
    if forced_event_type in ["Jamming Attack", "Signal Interference"]:
        modulation_type = "Noise"
    elif forced_event_type in ["Rolling Code", "Fixed Code"]:
        modulation_type = random.choice(["OOK", "ASK"]) 
    elif "Brute Force" in forced_event_type:
        modulation_type = random.choice(["FSK", "GFSK", "ASK"])
    else:
        modulation_type = random.choice(["FSK", "GFSK", "ASK", "OOK", "PSK", "QPSK"])
    
    # Technical signal parameters
    frequency_deviation = random.randint(25000, 85000) if modulation_type in ["FSK", "GFSK"] else 0
    bandwidth = random.randint(10000, 50000)
    symbol_rate = random.randint(1000, 20000)
    
    # NFC correlation parameters
    is_nfc_event = "NFC" in forced_event_type
    # Higher chance of correlation for certain attack types
    correlation_chance = 0.6 if "Brute Force" in forced_event_type or "Replay" in forced_event_type else 0.15
    nfc_correlated = random.random() < correlation_chance and not is_nfc_event
    nfc_tag_id = f"TAG_{random.randint(10000, 99999)}" if (nfc_correlated or is_nfc_event) else None
    nfc_proximity = round(random.uniform(0.5, 10.0), 1) if (nfc_correlated or is_nfc_event) else None
    nfc_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] if (nfc_correlated or is_nfc_event) else None
    
    # TECHNICAL EVIDENCE DATA
    evidence = {}
    
    # Common evidence fields for all security events
    if forced_event_type not in ["Fixed Code", "Rolling Code", "Normal Operation"]:
        evidence["detection_confidence"] = random.uniform(0.70, 0.98)
    
    # Event-specific evidence fields
    if "Replay Attack" in forced_event_type:
        evidence.update({
            "signal_match_score": random.uniform(0.75, 0.98),
            "burst_pattern": "".join(random.choice(["#", "-"]) for _ in range(8)),
            "peak_frequencies": [frequency + random.uniform(-0.05e6, 0.05e6) for _ in range(2)],
            "spectral_similarity": random.uniform(0.80, 0.95),
            "timing_analysis": {
                "replay_delay_ms": random.randint(50, 2000),
                "original_detection_time": (datetime.now().timestamp() - random.uniform(1, 60)),
            },
            "demodulated_data_similarity": random.uniform(0.85, 0.99)
        })
    
    elif "Brute Force" in forced_event_type:
        evidence.update({
            "temporal_analysis": {
                "detection_count": burst_count,
                "time_window_seconds": random.randint(10, 60),
                "burst_interval_ms": random.randint(200, 500),
                "pattern_regularity": random.uniform(0.7, 0.95)
            },
            "burst_pattern": "".join(random.choice(["#", "-"]) for _ in range(8)),
            "key_space_coverage": {
                "estimated_percent": random.uniform(1, 15),
                "key_entropy_bits": random.randint(24, 32)
            },
            "escalation": {
                "consecutive_attempts": random.randint(1, 20),
                "threat_escalation_level": random.randint(1, 5)
            }
        })
    
    elif "Jamming Attack" in forced_event_type:
        evidence.update({
            "affected_bands": random.randint(1, 3),
            "noise_floor_elevation_db": random.randint(10, 25),
            "spectral_characteristics": {
                "bandwidth_affected_khz": random.randint(200, 2000),
                "center_frequency_mhz": round(frequency / 1e6, 3),
                "spectral_mask": random.choice(["Flat", "Gaussian", "Pulsed", "Swept"])
            },
            "legitimate_signal_loss": random.uniform(0.5, 1.0),
            "directionality": random.choice(["Omni", "Directional"]),
            "estimated_power_mw": random.randint(50, 500)
        })
    
    elif is_nfc_event:
        evidence.update({
            "tag_type": random.choice(["ISO14443A", "ISO14443B", "FeliCa", "ISO15693"]),
            "scan_duration_ms": random.randint(100, 2000),
            "authentication_status": random.choice(["Success", "Failed", "Partial"]),
            "read_sectors": [random.randint(0, 15) for _ in range(random.randint(1, 8))]
        })
    
    # Mock a detection packet for unified analysis
    mock_packet = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "frequency": frequency,
        "rssi": rssi,
        "snr": snr,
        "modulation": modulation_type,
        "event_type": forced_event_type,
        "burst_count": burst_count,
        "frequency_deviation": frequency_deviation,
        "bandwidth": bandwidth,
        "symbol_rate": symbol_rate,
        "nfc_correlated": nfc_correlated,
        "nfc_tag_id": nfc_tag_id,
        "nfc_proximity": nfc_proximity,
        "nfc_timestamp": nfc_timestamp,
        "evidence": evidence
    }
    
    # Unified analysis through detection logic
    event = analyze_event(mock_packet, demo_mode=True)
    
    # Build the comprehensive result with all signal details
    result = {
        "type": event.get("event_type", forced_event_type),
        "threat": event.get("threat_level", "Suspicious"),
        "time": event.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "source": SOURCES[event_idx % len(SOURCES)],
        "details": DETAILS_MAP.get(event.get("event_type", forced_event_type), "Automotive event detected."),
        # Signal characteristics
        "modulation_type": modulation_type,
        "frequency": frequency,
        "rssi": rssi,
        "snr": snr,
        "burst_count": burst_count,
        "bandwidth": bandwidth,
        "frequency_deviation": frequency_deviation,
        "symbol_rate": symbol_rate,
        # NFC correlation data
        "nfc_correlated": nfc_correlated,
        "nfc_tag_id": nfc_tag_id,
        "nfc_proximity": nfc_proximity,
        "nfc_timestamp": nfc_timestamp,
        # Technical evidence
        "evidence": evidence
    }
    
    # Handle special case for critical multi-modal attacks (combined RF + NFC)
    if nfc_correlated and event.get("threat_level", "") in ["Malicious", "Suspicious"]:
        result["threat"] = "Critical"
        result["details"] = f"Multi-modal attack detected: {result['details']}"

    # Record event generation for performance monitoring
    performance_monitor = get_performance_monitor()
    
    # Simulate processing time (realistic for mock events)
    processing_time = random.uniform(35.0, 85.0)  # 35-85ms processing time
    performance_monitor.record_signal_processed(processing_time)
    performance_monitor.record_event_generated(result["type"])
    
    # Update system health occasionally
    if random.random() < 0.1:  # 10% chance
        performance_monitor.update_system_health(
            rtl_sdr_connected=True,  # Mock mode assumes connected
            pico_w_connected=random.random() > 0.1,  # 90% uptime
            memory_usage_mb=random.uniform(80.0, 150.0)
        )
    
    # Log the generated event for debugging and evidence collection
    logging.debug(f"Generated event: {json.dumps(result, default=str)}")
    
    return result
