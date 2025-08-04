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
import copy
import asyncio
from datetime import datetime
from itertools import count

# Import signal constants
from utils.signal_constants import (
    KEY_FOB_FREQUENCIES,
    ModulationType,
    ScenarioType,
    AttackType,
    NFCTagType,
    NFCAuthStatus,
    MANUFACTURER_PARAMETERS,
    DEFAULT_MANUFACTURERS,
    TIMESTAMP_FORMAT,
    TIMESTAMP_FORMAT_SHORT
)

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
    frequency = random.choice(list(KEY_FOB_FREQUENCIES.values()))
    rssi = random.randint(-80, -30)
    snr = random.randint(8, 25)
    burst_count = random.randint(3, 12)
    
    # More varied modulation types for better visualization testing
    if forced_event_type in ["Jamming Attack", "Signal Interference"]:
        modulation_type = ModulationType.NOISE.value
    elif forced_event_type in ["Rolling Code", "Fixed Code"]:
        modulation_type = random.choice([ModulationType.OOK.value, ModulationType.ASK.value])
    elif "Brute Force" in forced_event_type:
        modulation_type = random.choice([ModulationType.FSK.value, ModulationType.GFSK.value, ModulationType.ASK.value])
    else:
        modulation_type = random.choice([mod.value for mod in ModulationType if mod != ModulationType.WIDEBAND])
    
    # Technical signal parameters
    frequency_deviation = random.randint(25000, 85000) if modulation_type in [ModulationType.FSK.value, ModulationType.GFSK.value] else 0
    bandwidth = random.randint(10000, 50000)
    symbol_rate = random.randint(1000, 20000)
    
    # NFC correlation parameters
    is_nfc_event = "NFC" in forced_event_type
    # Higher chance of correlation for certain attack types
    correlation_chance = 0.6 if "Brute Force" in forced_event_type or "Replay" in forced_event_type else 0.15
    nfc_correlated = random.random() < correlation_chance and not is_nfc_event
    nfc_tag_id = f"TAG_{random.randint(10000, 99999)}" if (nfc_correlated or is_nfc_event) else None
    nfc_proximity = round(random.uniform(0.5, 10.0), 1) if (nfc_correlated or is_nfc_event) else None
    nfc_timestamp = datetime.now().strftime(TIMESTAMP_FORMAT) if (nfc_correlated or is_nfc_event) else None
    
    # TECHNICAL EVIDENCE DATA
    evidence = {}
    
    # Common evidence fields for all security events
    if forced_event_type not in ["Fixed Code", "Rolling Code", ScenarioType.NORMAL_OPERATION.value]:
        evidence["detection_confidence"] = random.uniform(0.70, 0.98)
    
    # Event-specific evidence fields
    if ScenarioType.REPLAY_ATTACK.value in forced_event_type or AttackType.REPLAY.value in forced_event_type:
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
    
    elif ScenarioType.BRUTE_FORCE_ATTACK.value in forced_event_type or AttackType.BRUTE_FORCE.value in forced_event_type:
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
    
    elif ScenarioType.JAMMING_ATTACK.value in forced_event_type or AttackType.JAMMING.value in forced_event_type:
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
            "tag_type": random.choice([tag_type.value for tag_type in NFCTagType]),
            "scan_duration_ms": random.randint(100, 2000),
            "nfc_auth_status": random.choice([status.value for status in NFCAuthStatus]),
            "read_sectors": [random.randint(0, 15) for _ in range(random.randint(1, 8))]
        })
    
    # Mock a detection packet for unified analysis
    mock_packet = {
        "timestamp": datetime.now().strftime(TIMESTAMP_FORMAT),
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
        "time": event.get("timestamp", datetime.now().strftime(TIMESTAMP_FORMAT)),
        "source": random.choice(DEFAULT_MANUFACTURERS),
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


def generate_synthetic_key_fob_event(event_type="benign"):
    """
    Generate a synthetic key fob signal event with realistic characteristics.
    
    Args:
        event_type (str): Type of event to generate ("benign", "malicious", "suspicious")
        
    Returns:
        dict: A synthetic key fob event with realistic signal characteristics
    """
    # Select a manufacturer
    manufacturer = random.choice(DEFAULT_MANUFACTURERS)
    
    # Generate a realistic key fob ID (typically 24-40 bits)
    key_fob_id = f"{random.randint(0, 0xFFFFFF):06x}".upper()
    
    # Get manufacturer-specific parameters
    if manufacturer in MANUFACTURER_PARAMETERS:
        params = MANUFACTURER_PARAMETERS[manufacturer]
        frequency = params["frequency"]
        modulation = params["modulation"]
        rolling_code_bits = params["rolling_code_bits"]
    else:
        # Fallback for unknown manufacturers
        frequency = random.choice(list(KEY_FOB_FREQUENCIES.values()))
        modulation = random.choice([m.value for m in ModulationType if m != ModulationType.NOISE and m != ModulationType.WIDEBAND])
        rolling_code_bits = 32
    
    # Generate a rolling code value
    rolling_code = random.randint(0, 2**rolling_code_bits - 1)
    
    # Calculate realistic signal parameters
    signal_strength = random.uniform(0.65, 0.95)  # Strong signal for legitimate key fob
    signal_quality = random.uniform(0.70, 0.98)  # Good quality for legitimate key fob
    snr = random.uniform(15, 30)  # Good SNR for legitimate key fob (dB)
    power_db = random.uniform(-60, -40)  # Typical power level for key fob (dBm)
    
    # Generate burst pattern based on modulation
    if modulation in [ModulationType.FSK.value, ModulationType.GFSK.value]:
        burst_pattern = f"2-FSK {int(frequency/1e6)} MHz"
    elif modulation == ModulationType.ASK.value:
        burst_pattern = f"ASK/OOK {int(frequency/1e6)} MHz"
    else:
        burst_pattern = f"{modulation} {int(frequency/1e6)} MHz"
    
    # Determine threat level based on event type
    if event_type == "benign":
        threat_level = "Normal"
        details = f"{manufacturer} Key Fob ({key_fob_id})"
    elif event_type == "suspicious":
        threat_level = "Suspicious"
        details = f"Unusual {manufacturer} Key Fob Activity ({key_fob_id})"
    elif event_type == "malicious":
        threat_level = "Malicious"
        details = f"Potential {manufacturer} Key Fob Clone ({key_fob_id})"
    else:
        threat_level = "Unknown"
        details = f"Unidentified Key Fob Signal ({key_fob_id})"
    
    # Create the synthetic event
    event = {
        "timestamp": datetime.now().strftime(TIMESTAMP_FORMAT),
        "type": "RF Key Fob",
        "threat": threat_level,
        "details": details,
        "source": "Synthetic",
        "frequency": frequency,
        "modulation_type": modulation,
        "signal_strength": signal_strength,
        "signal_quality": signal_quality,
        "snr_db": snr,
        "power_db": power_db,
        "burst_pattern": burst_pattern,
        "peak_count": random.randint(3, 8),
        "key_fob_id": key_fob_id,
        "manufacturer": manufacturer,
        "rolling_code": f"{rolling_code:x}",
        "rolling_code_bits": rolling_code_bits,
        "evidence": {
            "detection_confidence": signal_quality,
            "signal_analysis": {
                "frequency_mhz": f"{frequency/1e6:.2f}",
                "modulation": modulation,
                "signal_strength": f"{signal_strength:.2f}",
                "signal_quality": f"{signal_quality:.2f}",
                "snr_db": f"{snr:.1f}",
                "power_dbm": f"{power_db:.1f}"
            },
            "key_fob_details": {
                "key_fob_id": key_fob_id,
                "manufacturer": manufacturer,
                "rolling_code": f"0x{rolling_code:x}",
                "code_bits": str(rolling_code_bits)
            }
        }
    }
    
    return event


def generate_synthetic_replay_attack(original_event):
    """
    Generate a synthetic replay attack event based on a previously recorded event.
    
    Args:
        original_event (dict): The original event to replay
        
    Returns:
        dict: A synthetic replay attack event
    """
    # Create a deep copy of the original event
    replay_event = copy.deepcopy(original_event)
    
    # Update timestamp
    replay_event["timestamp"] = datetime.now().strftime(TIMESTAMP_FORMAT)
    
    # Mark as replay attack
    replay_event["type"] = "Replay Attack"
    replay_event["threat"] = "Malicious"
    replay_event["details"] = f"Replay Attack: {original_event.get('manufacturer', 'Unknown')} Key Fob ({original_event.get('key_fob_id', 'Unknown')})"
    
    # Slightly modify signal characteristics to simulate replay device
    replay_event["signal_strength"] = min(1.0, original_event.get("signal_strength", 0.8) * random.uniform(0.9, 1.1))
    replay_event["signal_quality"] = min(1.0, original_event.get("signal_quality", 0.7) * random.uniform(0.8, 1.0))
    replay_event["snr_db"] = original_event.get("snr_db", 20) * random.uniform(0.85, 1.05)
    replay_event["power_db"] = original_event.get("power_db", -50) * random.uniform(0.95, 1.05)
    
    # Add replay attack specific evidence
    replay_event["evidence"] = {
        "detection_confidence": random.uniform(0.85, 0.98),
        "signal_match_score": random.uniform(0.75, 0.98),
        "burst_pattern": "".join(random.choice(["#", "-"]) for _ in range(8)),
        "timing_analysis": {
            "replay_delay_ms": random.randint(50, 2000),
            "original_detection_time": (datetime.now().timestamp() - random.uniform(1, 60)),
        },
        "signal_analysis": {
            "frequency_mhz": f"{original_event.get('frequency', 433.92e6)/1e6:.2f}",
            "modulation": original_event.get('modulation_type', 'Unknown'),
            "signal_strength": f"{replay_event['signal_strength']:.2f}",
            "signal_quality": f"{replay_event['signal_quality']:.2f}",
            "snr_db": f"{replay_event['snr_db']:.1f}",
            "power_dbm": f"{replay_event['power_db']:.1f}"
        },
        "attack_indicators": {
            "duplicate_code": "Detected",
            "timing_anomaly": "Detected",
            "envelope_inconsistency": "Detected",
            "key_fob_id": original_event.get('key_fob_id', 'Unknown'),
            "manufacturer": original_event.get('manufacturer', 'Unknown'),
            "rolling_code": f"{original_event.get('rolling_code', 'Unknown')} (Duplicated)",
            "time_since_original": f"{random.randint(30, 300)} seconds"
        }
    }
    
    # Add attack metadata
    replay_event["attack_metadata"] = {
        "attack_type": AttackType.REPLAY.value,
        "original_timestamp": original_event.get("timestamp", "Unknown"),
        "time_delta": random.randint(5, 60),  # seconds since original transmission
        "confidence": random.uniform(0.85, 0.98)
    }
    
    return replay_event


def generate_synthetic_jamming_attack(step):
    """
    Generate a synthetic jamming attack event.
    
    Args:
        step (int): The step in the jamming attack sequence
        
    Returns:
        dict: A synthetic jamming attack event
    """
    # Jamming characteristics based on step
    if step == 0:
        # Initial detection of potential jamming
        threat_level = "Suspicious"
        details = "Unusual RF noise detected"
        signal_strength = random.uniform(0.6, 0.8)
        signal_quality = random.uniform(0.3, 0.5)  # Poor quality due to noise
        confidence = random.uniform(0.5, 0.7)
        evidence = [
            {
                "type": "Signal Analysis",
                "details": {
                    "frequency_range": "433-435 MHz",
                    "signal_strength": f"{signal_strength:.2f}",
                    "signal_quality": f"{signal_quality:.2f}",
                    "noise_floor": "Elevated"
                }
            },
            {
                "type": "Jamming Indicators",
                "details": {
                    "confidence": f"{confidence:.2f}",
                    "pattern": "Continuous",
                    "bandwidth": "2 MHz"
                }
            }
        ]
    elif step < 3:
        # Increasing jamming signal
        threat_level = "Suspicious"
        details = "Persistent RF interference detected"
        signal_strength = random.uniform(0.7, 0.9)
        signal_quality = random.uniform(0.2, 0.4)  # Decreasing quality
        confidence = random.uniform(0.6, 0.8)
        evidence = [
            {
                "type": "Signal Analysis",
                "details": {
                    "frequency_range": "430-440 MHz",
                    "signal_strength": f"{signal_strength:.2f}",
                    "signal_quality": f"{signal_quality:.2f}",
                    "noise_floor": "Highly Elevated"
                }
            },
            {
                "type": "Jamming Indicators",
                "details": {
                    "confidence": f"{confidence:.2f}",
                    "pattern": "Wideband Interference",
                    "duration": f"{step * 5} seconds",
                    "bandwidth": "10 MHz"
                }
            }
        ]
    else:
        # Confirmed jamming attack
        threat_level = "Malicious"
        details = "RF Jamming Attack Detected"
        signal_strength = random.uniform(0.8, 1.0)
        signal_quality = random.uniform(0.1, 0.3)  # Very poor quality
        confidence = random.uniform(0.85, 0.98)
        evidence = [
            {
                "type": "Signal Analysis",
                "details": {
                    "frequency_range": "425-445 MHz",
                    "signal_strength": f"{signal_strength:.2f}",
                    "signal_quality": f"{signal_quality:.2f}",
                    "noise_floor": "Critical"
                }
            },
            {
                "type": "Jamming Indicators",
                "details": {
                    "confidence": f"{confidence:.2f}",
                    "pattern": "Sustained Wideband Interference",
                    "duration": f"{step * 5} seconds",
                    "bandwidth": "20 MHz"
                }
            },
            {
                "type": "Attack Evidence",
                "details": {
                    "key_fob_blocked": "Yes",
                    "known_pattern_match": "Yes",
                    "attack_confidence": "High"
                }
            }
        ]
    
    # Create the jamming event
    event = {
        "timestamp": datetime.now().strftime(TIMESTAMP_FORMAT),
        "type": "Jamming",
        "threat": threat_level,
        "details": details,
        "source": "Synthetic",
        "frequency": KEY_FOB_FREQUENCIES["EU_STANDARD"],  # Center frequency being jammed
        "modulation_type": ModulationType.WIDEBAND.value,
        "signal_strength": signal_strength,
        "signal_quality": signal_quality,
        "snr_db": random.uniform(5, 15),  # Low SNR due to jamming
        "power_db": random.uniform(-40, -20),  # High power for jamming
        "burst_pattern": "Wideband Interference",
        "peak_count": random.randint(10, 20),  # Many peaks in jamming
        "evidence": {
            "detection_confidence": confidence,
            "noise_floor_elevation_db": random.randint(10, 25),
            "spectral_characteristics": {
                "bandwidth_affected_khz": random.randint(200, 2000),
                "center_frequency_mhz": round(KEY_FOB_FREQUENCIES["EU_STANDARD"] / 1e6, 3),
                "spectral_mask": random.choice(["Flat", "Gaussian", "Pulsed", "Swept"])
            },
            "legitimate_signal_loss": random.uniform(0.5, 1.0),
            "directionality": random.choice(["Omni", "Directional"]),
            "estimated_power_mw": random.randint(50, 500)
        },
        "attack_metadata": {
            "attack_type": AttackType.JAMMING.value,
            "duration": step * 5,  # seconds
            "bandwidth": random.uniform(5, 20),  # MHz
            "confidence": confidence
        }
    }
    
    return event


def generate_synthetic_brute_force_attack(step):
    """
    Generate a synthetic brute force attack event.
    
    Args:
        step (int): The step in the brute force attack sequence
        
    Returns:
        dict: A synthetic brute force attack event
    """
    # Select a manufacturer to target
    manufacturer = random.choice(DEFAULT_MANUFACTURERS)
    
    # Define the steps in a brute force attack
    steps = {
        0: {
            "type": "RF Scan",
            "details": "Suspicious RF scanning activity detected.",
            "threat": "Suspicious",
            "color": "yellow",
            "evidence": [
                "Multiple frequency scanning detected",
                "Sequential code pattern observed",
                "Rapid transmission bursts"
            ]
        },
        1: {
            "type": "Brute Force",
            "details": "Possible brute force attempt detected.",
            "threat": "Suspicious",
            "color": "yellow",
            "evidence": [
                "Sequential code patterns",
                "Rapid transmission rate",
                "Multiple frequency attempts"
            ]
        },
        2: {
            "type": "Brute Force",
            "details": "Brute force attack in progress!",
            "threat": "Malicious",
            "color": "red",
            "evidence": [
                "Systematic code sequence detected",
                "High-speed transmission pattern",
                "Multiple rolling code attempts",
                "Authentication bypass attempts"
            ]
        },
        3: {
            "type": "Brute Force",
            "details": "Brute force attack continuing!",
            "threat": "Malicious",
            "color": "red",
            "evidence": [
                "Continued systematic code attempts",
                "Accelerated transmission rate",
                "Pattern suggests automated tool",
                "Multiple authentication failures"
            ]
        },
        4: {
            "type": "Brute Force",
            "details": "Advanced brute force attack detected!",
            "threat": "Malicious",
            "color": "red",
            "evidence": [
                "Sophisticated brute force pattern",
                "Optimized code sequence detected",
                "Targeted manufacturer vulnerabilities",
                "Possible pre-computation attack"
            ]
        }
    }
    
    # Get the appropriate step data or default to the last step
    step_data = steps.get(step, steps[4])
    
    # Base event structure
    event = {
        "timestamp": datetime.now().strftime(TIMESTAMP_FORMAT),
        "id": random.randint(10000, 99999),
        "frequency": KEY_FOB_FREQUENCIES[random.choice(list(KEY_FOB_FREQUENCIES.keys()))],
        "modulation": ModulationType.FSK.value,  # Brute force often uses FSK for faster data rate
        "rssi": random.uniform(-70, -50),  # Moderate signal strength
        "snr": random.uniform(10, 20),     # Moderate SNR
        "burst_count": random.randint(10, 30),  # Many bursts in brute force
        "type": step_data["type"],
        "details": step_data["details"],
        "threat": step_data["threat"],
        "color": step_data["color"],
        "source": random.choice(list(MANUFACTURER_PARAMETERS.keys())),
        "nfc_correlated": False,  # Brute force typically doesn't involve NFC
        "evidence": step_data["evidence"]
    }
    
    # Get manufacturer-specific parameters
    manufacturer = event["source"]
    if manufacturer in MANUFACTURER_PARAMETERS:
        params = MANUFACTURER_PARAMETERS[manufacturer]
        frequency = params["frequency"]
        modulation = params["modulation"]
    else:
        # Fallback for unknown manufacturers
        frequency = KEY_FOB_FREQUENCIES["EU_STANDARD"]
        modulation = random.choice([ModulationType.FSK.value, ModulationType.ASK.value, ModulationType.OOK.value])
    
    # Generate a key fob ID for this attempt
    key_fob_id = f"{random.randint(0, 0xFFFFFF):06x}".upper()
    
    # Generate a rolling code value
    rolling_code = random.randint(0, 2**32 - 1)
    
    # Calculate realistic signal parameters for brute force device
    signal_strength = random.uniform(0.5, 0.8)  # Moderate signal for attack device
    signal_quality = random.uniform(0.4, 0.7)  # Moderate quality for attack device
    snr = random.uniform(10, 20)  # Moderate SNR for attack device
    power_db = random.uniform(-65, -45)  # Typical power level
    
    # Determine threat level based on step
    if step < 3:
        threat_level = "Suspicious"
        details = f"Unusual Key Fob Activity ({step+1} attempts)"
        confidence = random.uniform(0.6, 0.8)
    else:
        threat_level = "Malicious"
        details = f"Brute Force Attack Detected ({step+1} attempts)"
        confidence = random.uniform(0.8, 0.95)
    
    # Add technical evidence
    event["evidence"] = {
        "detection_confidence": confidence,
        "temporal_analysis": {
            "detection_count": event['burst_count'],
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
    }
    
    return event


def generate_synthetic_signal_cloning_attack(step):
    """
    Generate a synthetic signal cloning attack event.
    
    Signal cloning is an attack where the attacker captures a legitimate signal,
    analyzes its characteristics, and then creates a clone with identical properties.
    Unlike replay attacks that simply record and replay, cloning recreates the signal.
    
    Args:
        step (int): The step in the signal cloning attack sequence
        
    Returns:
        dict: A synthetic signal cloning attack event
    """
    # Define the steps in a signal cloning attack
    steps = {
        0: {
            "type": "RF Scan",
            "details": "Suspicious RF scanning activity detected.",
            "threat": "Suspicious",
            "color": "yellow",
            "evidence": [
                "Signal analyzer detected",
                "Frequency hopping pattern observed",
                "Multiple manufacturer frequencies scanned"
            ]
        },
        1: {
            "type": "RF Capture",
            "details": "Key fob signal capture attempt detected.",
            "threat": "Suspicious",
            "color": "yellow",
            "evidence": [
                "Targeted frequency monitoring",
                "Signal recording pattern detected",
                "Unusual RF activity near vehicle"
            ]
        },
        2: {
            "type": "Signal Analysis",
            "details": "Signal analysis activity detected.",
            "threat": "Suspicious",
            "color": "yellow",
            "evidence": [
                "Repeated signal pattern analysis",
                "Demodulation attempt detected",
                "Signal parameter extraction observed"
            ]
        },
        3: {
            "type": "Signal Cloning",
            "details": "Signal cloning attack detected!",
            "threat": "Malicious",
            "color": "red",
            "evidence": [
                "Artificially generated signal detected",
                "Signal matches authorized key fob pattern",
                "Non-standard signal generation hardware detected",
                "Signal lacks proper rolling code progression"
            ]
        },
        4: {
            "type": "Signal Cloning",
            "details": "Signal cloning attack in progress!",
            "threat": "Malicious",
            "color": "red",
            "evidence": [
                "Multiple cloned signals detected",
                "Cloned signal attempting authentication",
                "Authentication bypass attempt detected",
                "Signal characteristics match known cloning attack pattern"
            ]
        }
    }
    
    # Get the appropriate step data or default to the last step
    step_data = steps.get(step, steps[4])
    
    # Base event structure
    event = {
        "timestamp": datetime.now().strftime(TIMESTAMP_FORMAT),
        "id": random.randint(10000, 99999),
        "frequency": KEY_FOB_FREQUENCIES[random.choice(list(KEY_FOB_FREQUENCIES.keys()))],
        "modulation": ModulationType.ASK.value,  # Signal cloning often uses ASK for simplicity
        "rssi": random.uniform(-60, -40),  # Strong signal for cloning device
        "snr": random.uniform(15, 25),     # Good SNR for a cloning device
        "burst_count": random.randint(3, 8),
        "type": step_data["type"],
        "details": step_data["details"],
        "threat": step_data["threat"],
        "color": step_data["color"],
        "source": random.choice(list(MANUFACTURER_PARAMETERS.keys())),
        "nfc_correlated": False,  # Signal cloning typically doesn't involve NFC
        "evidence": step_data["evidence"]
    }
    
    # Add technical evidence
    event["evidence"] = {
        "detection_confidence": random.uniform(0.85, 0.98),
        "signal_match_score": random.uniform(0.75, 0.98),
        "burst_pattern": "".join(random.choice(["#", "-"]) for _ in range(8)),
        "peak_frequencies": [event['frequency'] + random.uniform(-0.05e6, 0.05e6) for _ in range(2)],
        "spectral_similarity": random.uniform(0.80, 0.95),
        "timing_analysis": {
            "clone_delay_ms": random.randint(50, 2000),
            "original_detection_time": (datetime.now().timestamp() - random.uniform(1, 60)),
        },
        "demodulated_data_similarity": random.uniform(0.85, 0.99)
    }
    
    return event


def generate_synthetic_relay_attack(step):
    """
    Generate a synthetic relay attack event.
    
    A relay attack is where attackers use signal amplifiers to extend the range of a legitimate key fob,
    making the car think the key is nearby when it's actually far away.
    
    Args:
        step (int): The step in the relay attack sequence
        
    Returns:
        dict: A synthetic relay attack event
    """
    # Define the steps in a relay attack
    steps = {
        0: {
            "type": "RF Anomaly",
            "details": "Unusual RF signal pattern detected.",
            "threat": "Suspicious",
            "color": "yellow",
            "evidence": [
                "Signal amplification detected",
                "Unusual signal propagation pattern",
                "Non-standard signal strength fluctuation"
            ]
        },
        1: {
            "type": "Range Extension",
            "details": "Possible signal range extension detected.",
            "threat": "Suspicious",
            "color": "yellow",
            "evidence": [
                "Signal strength inconsistent with distance",
                "Multiple signal paths detected",
                "Signal relay characteristics observed"
            ]
        },
        2: {
            "type": "Relay Attack",
            "details": "Relay attack detected!",
            "threat": "Malicious",
            "color": "red",
            "evidence": [
                "Signal amplification confirmed",
                "Key presence verification failed",
                "Multiple signal relay points detected",
                "Signal latency indicates relay"
            ]
        },
        3: {
            "type": "Relay Attack",
            "details": "Relay attack in progress!",
            "threat": "Malicious",
            "color": "red",
            "evidence": [
                "Active signal relay detected",
                "Authentication bypass attempt",
                "Signal characteristics match relay attack",
                "Proximity verification failed"
            ]
        },
        4: {
            "type": "Relay Attack",
            "details": "Advanced relay attack detected!",
            "threat": "Malicious",
            "color": "red",
            "evidence": [
                "Sophisticated relay equipment detected",
                "Multiple relay stages identified",
                "Signal amplification with minimal latency",
                "Attempting to bypass distance-bounding protocols"
            ]
        }
    }
    
    # Get the appropriate step data or default to the last step
    step_data = steps.get(step, steps[4])
    
    # Base event structure
    event = {
        "timestamp": datetime.now().strftime(TIMESTAMP_FORMAT),
        "id": random.randint(10000, 99999),
        "frequency": KEY_FOB_FREQUENCIES[random.choice(list(KEY_FOB_FREQUENCIES.keys()))],
        "modulation": random.choice([m.value for m in ModulationType]),
        "rssi": random.uniform(-50, -30),  # Very strong signal due to amplification
        "snr": random.uniform(10, 20),     # Moderate SNR due to relay noise
        "burst_count": random.randint(2, 5),
        "type": step_data["type"],
        "details": step_data["details"],
        "threat": step_data["threat"],
        "color": step_data["color"],
        "source": random.choice(list(MANUFACTURER_PARAMETERS.keys())),
        "nfc_correlated": False,  # Relay attacks typically don't involve NFC
        "evidence": step_data["evidence"]
    }
    
    # Add technical evidence
    event["evidence"] = {
        "detection_confidence": random.uniform(0.80, 0.95),
        "signal_match_score": random.uniform(0.75, 0.98),
        "burst_pattern": "".join(random.choice(["#", "-"]) for _ in range(8)),
        "timing_analysis": {
            "relay_delay_ms": random.randint(50, 2000),
            "propagation_delay": f"{random.uniform(1.5, 4.5):.2f} ms (abnormal)",
            "time_of_flight": "Extended (suspicious)"
        },
        "signal_analysis": {
            "signal_strength": f"{event['rssi']:.1f} dBm (abnormally high)",
            "signal_path": "Multiple paths detected",
            "proximity_check": "Failed",
            "signal_origin": "Inconsistent"
        }
    }
    
    return event


async def generate_synthetic_event():
    """
    Async generator that yields advanced synthetic signal events for testing and demonstration.
    This generator creates realistic key fob signals, replay attacks, jamming scenarios, and
    brute force attacks with detailed technical evidence for validation.
    
    Only used when both --mock and --synthetic flags are enabled.
    
    Yields:
        dict: Synthetic event with realistic signal characteristics and evidence.
        
    Example:
        async for event in generate_synthetic_event():
            print(event)
    """
    # Track previously generated events for replay attack simulation
    event_history = []
    attack_history = {}
    
    # Define demonstration scenarios using the enum
    scenarios = [
        ScenarioType.NORMAL_OPERATION.value,
        ScenarioType.REPLAY_ATTACK.value,
        ScenarioType.JAMMING_ATTACK.value,
        ScenarioType.BRUTE_FORCE_ATTACK.value,
        ScenarioType.SIGNAL_CLONING_ATTACK.value,
        ScenarioType.RELAY_ATTACK.value
    ]
    
    # Scenario state tracking
    scenario_states = {
        ScenarioType.NORMAL_OPERATION.value: {"step": 0, "last_time": datetime.now()},
        ScenarioType.REPLAY_ATTACK.value: {"step": 0, "last_time": datetime.now(), "in_progress": False},
        ScenarioType.JAMMING_ATTACK.value: {"step": 0, "last_time": datetime.now(), "in_progress": False},
        ScenarioType.BRUTE_FORCE_ATTACK.value: {"step": 0, "last_time": datetime.now(), "in_progress": False},
        ScenarioType.SIGNAL_CLONING_ATTACK.value: {"step": 0, "last_time": datetime.now(), "in_progress": False},
        ScenarioType.RELAY_ATTACK.value: {"step": 0, "last_time": datetime.now(), "in_progress": False}
    }
    
    # Probability weights for different scenarios
    # Normal operation should be most common, followed by occasional attacks
    scenario_weights = {
        ScenarioType.NORMAL_OPERATION.value: 0.5,  # 50% chance for normal events
        ScenarioType.REPLAY_ATTACK.value: 0.1,     # 10% chance for replay attacks
        ScenarioType.JAMMING_ATTACK.value: 0.1,    # 10% chance for jamming attacks
        ScenarioType.BRUTE_FORCE_ATTACK.value: 0.1,# 10% chance for brute force attacks
        ScenarioType.SIGNAL_CLONING_ATTACK.value: 0.1, # 10% chance for signal cloning attacks
        ScenarioType.RELAY_ATTACK.value: 0.1       # 10% chance for relay attacks
    }
    
    while True:
        # Determine which scenario to generate next based on weights and state
        # If an attack sequence is in progress, continue it
        active_attack = None
        for scenario, state in scenario_states.items():
            if scenario != ScenarioType.NORMAL_OPERATION.value and state.get("in_progress", False):
                active_attack = scenario
                break
        
        if active_attack:
            # Continue the active attack sequence
            current_scenario = active_attack
        else:
            # Choose a new scenario based on weighted probabilities
            scenarios_list = list(scenario_weights.keys())
            weights_list = list(scenario_weights.values())
            current_scenario = random.choices(scenarios_list, weights=weights_list, k=1)[0]
            
            # Mark the chosen attack as in progress if it's an attack
            if current_scenario != ScenarioType.NORMAL_OPERATION.value:
                scenario_states[current_scenario]["in_progress"] = True
                scenario_states[current_scenario]["step"] = 0
                logging.info(f"Starting new scenario: {current_scenario}")
        
        # Get the current step for this scenario
        scenario_step = scenario_states[current_scenario]["step"]
        
        # Generate appropriate event based on current scenario
        if current_scenario == ScenarioType.NORMAL_OPERATION.value:
            # Normal key fob operation (benign events)
            # Occasionally generate suspicious but benign events
            event_type = random.choices(["benign", "suspicious"], weights=[0.9, 0.1], k=1)[0]
            event = generate_synthetic_key_fob_event(event_type)
            await asyncio.sleep(random.uniform(2.0, 4.0))  # Normal key fob timing
            
            # Store event for later replay
            if len(event_history) < 5:  # Keep last 5 events for replay
                event_history.append(event)
            else:
                event_history.pop(0)
                event_history.append(event)
                
        elif current_scenario == ScenarioType.REPLAY_ATTACK.value:
            if scenario_step == 0:
                # First show a normal key fob event
                event = generate_synthetic_key_fob_event("benign")
                scenario_states[current_scenario]["step"] += 1
                await asyncio.sleep(2.0)
            else:
                # Then show the replay attack using a previously recorded event
                if event_history:
                    original_event = random.choice(event_history)
                    event = generate_synthetic_replay_attack(original_event)
                    scenario_states[current_scenario]["step"] += 1
                    await asyncio.sleep(1.0)  # Faster replay timing
                    
                    # End the replay attack sequence after a few attempts
                    if scenario_step >= random.randint(2, 4):
                        scenario_states[current_scenario]["in_progress"] = False
                        logging.info("Replay attack sequence completed")
                else:
                    # Fallback if no history available
                    event = generate_synthetic_key_fob_event("suspicious")
                    scenario_states[current_scenario]["in_progress"] = False
                    await asyncio.sleep(2.0)
                    
        elif current_scenario == ScenarioType.JAMMING_ATTACK.value:
            event = generate_synthetic_jamming_attack(scenario_step)
            scenario_states[current_scenario]["step"] += 1
            await asyncio.sleep(0.8)  # Jamming happens more frequently
            
            # End the jamming attack sequence after several steps
            if scenario_step >= random.randint(3, 6):
                scenario_states[current_scenario]["in_progress"] = False
                logging.info("Jamming attack sequence completed")
            
        elif current_scenario == ScenarioType.BRUTE_FORCE_ATTACK.value:
            event = generate_synthetic_brute_force_attack(scenario_step)
            scenario_states[current_scenario]["step"] += 1
            await asyncio.sleep(0.5)  # Brute force attempts happen rapidly
            
            # End the brute force attack sequence after several attempts
            if scenario_step >= random.randint(4, 8):
                scenario_states[current_scenario]["in_progress"] = False
                logging.info("Brute force attack sequence completed")
                
        elif current_scenario == ScenarioType.SIGNAL_CLONING_ATTACK.value:
            event = generate_synthetic_signal_cloning_attack(scenario_step)
            scenario_states[current_scenario]["step"] += 1
            await asyncio.sleep(0.7)  # Signal cloning happens at moderate pace
            
            # End the signal cloning attack sequence after several steps
            if scenario_step >= random.randint(3, 5):
                scenario_states[current_scenario]["in_progress"] = False
                logging.info("Signal cloning attack sequence completed")
                
        elif current_scenario == ScenarioType.RELAY_ATTACK.value:
            event = generate_synthetic_relay_attack(scenario_step)
            scenario_states[current_scenario]["step"] += 1
            await asyncio.sleep(0.6)  # Relay attacks happen relatively quickly
            
            # End the relay attack sequence after several steps
            if scenario_step >= random.randint(3, 6):
                scenario_states[current_scenario]["in_progress"] = False
                logging.info("Relay attack sequence completed")
        
        # Update the last time this scenario was used
        scenario_states[current_scenario]["last_time"] = datetime.now()
        
        yield event


