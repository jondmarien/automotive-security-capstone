"""Hardware data models and types."""
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class PowerState(Enum):
    """Device power states."""
    OFF = auto()
    LOW_POWER = auto()
    ACTIVE = auto()
    BOOTING = auto()
    SHUTTING_DOWN = auto()


@dataclass
class SignalMetrics:
    """RF signal metrics."""
    rssi: float  # Received Signal Strength Indicator in dBm
    snr: Optional[float] = None  # Signal-to-Noise Ratio in dB
    frequency: Optional[float] = None  # Frequency in Hz
    channel: Optional[int] = None  # Channel number if applicable


@dataclass
class MemoryUsage:
    """Memory usage statistics."""
    total: int  # Total memory in bytes
    used: int  # Used memory in bytes
    free: int  # Free memory in bytes
    usage_percent: float  # Usage percentage (0-100)


@dataclass
class RFConfig:
    """RF module configuration."""
    frequency: float  # Frequency in Hz
    power: int  # Transmit power in dBm
    data_rate: int  # Data rate in bps
    modulation: str  # Modulation type (e.g., '2-FSK', 'GFSK')
    bandwidth: float  # Bandwidth in Hz
    devitation: float  # Frequency deviation in Hz
    sync_word: Optional[bytes] = None  # Sync word for packet detection
    crc_enabled: bool = True  # Enable CRC checking
    auto_ack: bool = False  # Enable automatic acknowledgments
