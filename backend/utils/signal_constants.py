"""
signal_constants.py

Centralized constants for automotive RF signal parameters and attack scenarios.
Used by both the synthetic signal generation and detection modules.
"""

from enum import Enum

# Common key fob frequencies (Hz)
KEY_FOB_FREQUENCIES = {
    "EU_STANDARD": 433.92e6,  # European standard
    "US_STANDARD": 315.0e6,  # US standard
    "EU_ALTERNATIVE": 868.0e6,  # Alternative European frequency
    "US_ALTERNATIVE": 915.0e6,  # Alternative US frequency
    "BLUETOOTH": 2.4e9,  # Bluetooth frequency (newer key fobs)
}


# Common modulation types used in automotive RF
class ModulationType(Enum):
    FSK = "FSK"  # Frequency Shift Keying
    GFSK = "GFSK"  # Gaussian Frequency Shift Keying
    ASK = "ASK"  # Amplitude Shift Keying
    OOK = "OOK"  # On-Off Keying (special case of ASK)
    PSK = "PSK"  # Phase Shift Keying
    QPSK = "QPSK"  # Quadrature Phase Shift Keying
    NOISE = "Noise"  # Noise/Interference (for jamming)
    WIDEBAND = "Wideband"  # Wideband interference


# Manufacturer-specific parameters
MANUFACTURER_PARAMETERS = {
    "Toyota": {
        "frequency": KEY_FOB_FREQUENCIES["EU_STANDARD"],
        "modulation": ModulationType.FSK.value,
        "rolling_code_bits": 24,
    },
    "Lexus": {
        "frequency": KEY_FOB_FREQUENCIES["EU_STANDARD"],
        "modulation": ModulationType.FSK.value,
        "rolling_code_bits": 24,
    },
    "Honda": {
        "frequency": KEY_FOB_FREQUENCIES["EU_STANDARD"],
        "modulation": ModulationType.GFSK.value,
        "rolling_code_bits": 32,
    },
    "Acura": {
        "frequency": KEY_FOB_FREQUENCIES["EU_STANDARD"],
        "modulation": ModulationType.GFSK.value,
        "rolling_code_bits": 32,
    },
    "Ford": {
        "frequency": KEY_FOB_FREQUENCIES["US_STANDARD"],
        "modulation": ModulationType.ASK.value,
        "rolling_code_bits": 40,
    },
    "Lincoln": {
        "frequency": KEY_FOB_FREQUENCIES["US_STANDARD"],
        "modulation": ModulationType.ASK.value,
        "rolling_code_bits": 40,
    },
    "BMW": {
        "frequency": KEY_FOB_FREQUENCIES["EU_STANDARD"],
        "modulation": ModulationType.FSK.value,
        "rolling_code_bits": 48,
    },
    "Mini": {
        "frequency": KEY_FOB_FREQUENCIES["EU_STANDARD"],
        "modulation": ModulationType.FSK.value,
        "rolling_code_bits": 48,
    },
    "Mercedes": {
        "frequency": KEY_FOB_FREQUENCIES["EU_STANDARD"],
        "modulation": ModulationType.ASK.value,
        "rolling_code_bits": 64,
    },
    "Smart": {
        "frequency": KEY_FOB_FREQUENCIES["EU_STANDARD"],
        "modulation": ModulationType.ASK.value,
        "rolling_code_bits": 64,
    },
    "Audi": {
        "frequency": KEY_FOB_FREQUENCIES["EU_STANDARD"],
        "modulation": ModulationType.FSK.value,
        "rolling_code_bits": 32,
    },
    "Volkswagen": {
        "frequency": KEY_FOB_FREQUENCIES["EU_STANDARD"],
        "modulation": ModulationType.FSK.value,
        "rolling_code_bits": 32,
    },
    "Porsche": {
        "frequency": KEY_FOB_FREQUENCIES["EU_STANDARD"],
        "modulation": ModulationType.FSK.value,
        "rolling_code_bits": 32,
    },
}


# Demonstration scenario types
class ScenarioType(Enum):
    NORMAL_OPERATION = "normal_operation"
    REPLAY_ATTACK = "replay_attack"
    JAMMING_ATTACK = "jamming_attack"
    BRUTE_FORCE_ATTACK = "brute_force_attack"
    SIGNAL_CLONING_ATTACK = "signal_cloning_attack"
    RELAY_ATTACK = "relay_attack"
    # Critical attack scenarios
    CRITICAL_VULNERABILITY_EXPLOIT = "critical_vulnerability_exploit"
    MULTI_MODAL_ATTACK = "multi_modal_attack"
    ADVANCED_PERSISTENT_THREAT = "advanced_persistent_threat"
    ZERO_DAY_EXPLOIT = "zero_day_exploit"


# Attack types
class AttackType(Enum):
    REPLAY = "replay"
    JAMMING = "jamming"
    BRUTE_FORCE = "brute_force"
    SIGNAL_CLONING = "signal_cloning"
    RELAY = "relay"
    # Critical attack types
    CRITICAL_EXPLOIT = "critical_exploit"
    MULTI_MODAL = "multi_modal"
    PERSISTENT_THREAT = "persistent_threat"
    ZERO_DAY = "zero_day"


# NFC tag types commonly used in automotive security
class NFCTagType(Enum):
    ISO14443A = "ISO14443A"  # Most common NFC tag type (MIFARE, etc.)
    ISO14443B = "ISO14443B"  # Less common but used in some access systems
    FELICA = "FeliCa"  # Sony's NFC technology
    ISO15693 = "ISO15693"  # Vicinity cards with longer read range


# NFC authentication status types
class NFCAuthStatus(Enum):
    SUCCESS = "Success"  # Authentication completed successfully
    FAILED = "Failed"  # Authentication failed
    PARTIAL = "Partial"  # Partial authentication (some sectors accessible)


# Standardized timestamp format for consistent display across all modules
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"  # Full date and time (YYYY-MM-DD HH:MM:SS)
TIMESTAMP_FORMAT_SHORT = "%H:%M:%S"  # Time only (HH:MM:SS)

# Default manufacturers list
DEFAULT_MANUFACTURERS = [
    "Toyota",
    "Honda",
    "Ford",
    "BMW",
    "Mercedes",
    "Audi",
    "Volkswagen",
    "Porsche",
    "Lexus",
    "Acura",
]
