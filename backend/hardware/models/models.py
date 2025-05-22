"""Hardware data models and types.

This module defines data structures used throughout the hardware abstraction layer.
All models include validation and serialization capabilities.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Dict, Optional, Union

# Type alias for JSON-serializable data
JSONType = Union[Dict[str, Any], list, str, int, float, bool, None]  # noqa: F841


class PowerState(Enum):
    """Device power states.
    
    Attributes:
        OFF: Device is powered off
        LOW_POWER: Device is in low-power mode
        ACTIVE: Device is fully operational
        BOOTING: Device is starting up
        SHUTTING_DOWN: Device is shutting down
    """
    OFF = auto()
    LOW_POWER = auto()
    ACTIVE = auto()
    BOOTING = auto()
    SHUTTING_DOWN = auto()
    
    def __str__(self) -> str:
        """Return string representation of the power state."""
        return self.name.replace('_', ' ').title()
    
    @classmethod
    def from_string(cls, value: str) -> 'PowerState':
        """Convert string to PowerState enum.
        
        Args:
            value: String representation of power state
                (case-insensitive, underscores or spaces)
                
        Returns:
            PowerState: Corresponding enum value
            
        Raises:
            ValueError: If the string doesn't match any power state
        """
        try:
            return cls[value.upper().replace(' ', '_')]
        except KeyError as e:
            valid_states = ', '.join(f"'{state.name.lower().replace('_', ' ')}'" 
                                  for state in PowerState)
            raise ValueError(
                f"Invalid power state: {value}. "
                f"Must be one of: {valid_states}"
            ) from e


@dataclass
class SignalMetrics:
    """RF signal metrics.
    
    Attributes:
        rssi: Received Signal Strength Indicator in dBm (typically -120 to 0)
        snr: Signal-to-Noise Ratio in dB (higher is better)
        frequency: Operating frequency in Hz
        channel: Channel number if applicable
        timestamp: When these metrics were recorded (auto-generated)
    """
    rssi: float
    snr: Optional[float] = None
    frequency: Optional[float] = None
    channel: Optional[int] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self) -> None:
        """Validate signal metrics."""
        if not -150 <= self.rssi <= 0:
            raise ValueError(f"RSSI must be between -150 and 0 dBm, got {self.rssi}")
        if self.snr is not None and (self.snr < 0 or self.snr > 30):
            raise ValueError(f"SNR must be between 0 and 30 dB, got {self.snr}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'rssi': self.rssi,
            'snr': self.snr,
            'frequency': self.frequency,
            'channel': self.channel,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SignalMetrics':
        """Create from dictionary."""
        timestamp = (
            datetime.fromisoformat(data['timestamp']).replace(tzinfo=timezone.utc)
            if 'timestamp' in data
            else datetime.now(timezone.utc)
        )
        return cls(
            rssi=data['rssi'],
            snr=data.get('snr'),
            frequency=data.get('frequency'),
            channel=data.get('channel'),
            timestamp=timestamp
        )


@dataclass
class MemoryUsage:
    """Memory usage statistics.
    
    Attributes:
        total: Total memory in bytes
        used: Used memory in bytes
        free: Free memory in bytes
        usage_percent: Usage percentage (0-100)
        timestamp: When the memory usage was recorded (auto-generated)
    """
    total: int
    used: int
    free: int
    usage_percent: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self) -> None:
        """Validate memory usage values."""
        if self.total <= 0:
            raise ValueError(f"Total memory must be positive, got {self.total}")
        if not 0 <= self.usage_percent <= 100:
            raise ValueError(f"Usage percent must be between 0 and 100, got {self.usage_percent}")
        if self.used + self.free > self.total:
            raise ValueError("Sum of used and free memory cannot exceed total memory")
    
    @classmethod
    def from_usage(cls, total: int, used: int) -> 'MemoryUsage':
        """Create from total and used memory.
        
        Args:
            total: Total memory in bytes
            used: Used memory in bytes
            
        Returns:
            MemoryUsage: New instance with calculated free memory and usage percentage
        """
        free = max(0, total - used)
        usage_percent = (used / total) * 100 if total > 0 else 0
        return cls(total=total, used=used, free=free, usage_percent=usage_percent)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'total': self.total,
            'used': self.used,
            'free': self.free,
            'usage_percent': round(self.usage_percent, 2),
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryUsage':
        """Create from dictionary."""
        timestamp = (
            datetime.fromisoformat(data['timestamp']).replace(tzinfo=timezone.utc)
            if 'timestamp' in data
            else datetime.now(timezone.utc)
        )
        return cls(
            total=data['total'],
            used=data['used'],
            free=data['free'],
            usage_percent=data['usage_percent'],
            timestamp=timestamp
        )


@dataclass
class RFConfig:
    """RF module configuration.
    
    Attributes:
        frequency: Operating frequency in Hz (e.g., 868e6 for 868MHz)
        power: Transmit power in dBm (device-specific range)
        data_rate: Data rate in bits per second
        modulation: Modulation type (e.g., '2-FSK', 'GFSK', 'LoRa')
        bandwidth: Channel bandwidth in Hz
        devitation: Frequency deviation in Hz (for FSK)
        sync_word: Sync word for packet detection (1-8 bytes)
        crc_enabled: Enable CRC checking for error detection
        auto_ack: Enable automatic acknowledgments
        node_id: Optional node identifier
        network_id: Optional network identifier
    """
    frequency: float
    power: int
    data_rate: int
    modulation: str
    bandwidth: float
    devitation: float
    sync_word: Optional[bytes] = None
    crc_enabled: bool = True
    auto_ack: bool = False
    node_id: Optional[int] = None
    network_id: Optional[int] = None
    
    # Common modulation types
    MODULATION_FSK = 'FSK'
    MODULATION_GFSK = 'GFSK'
    MODULATION_LORA = 'LoRa'
    
    def __post_init__(self) -> None:
        """Validate RF configuration."""
        if self.frequency < 1e6 or self.frequency > 10e9:  # 1MHz to 10GHz
            raise ValueError(f"Frequency {self.frequency}Hz is outside valid range (1MHz-10GHz)")
        if not -20 <= self.power <= 30:  # Typical range for RF modules
            raise ValueError(f"Power {self.power}dBm is outside valid range (-20 to 30 dBm)")
        if self.data_rate < 100 or self.data_rate > 1_000_000:  # 100bps to 1Mbps
            raise ValueError(f"Data rate {self.data_rate}bps is outside valid range (100-1,000,000 bps)")
        if self.sync_word and len(self.sync_word) > 8:  # Max 8 bytes for sync word
            raise ValueError(f"Sync word too long (max 8 bytes, got {len(self.sync_word)})")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'frequency': self.frequency,
            'power': self.power,
            'data_rate': self.data_rate,
            'modulation': self.modulation,
            'bandwidth': self.bandwidth,
            'devitation': self.devitation,
            'sync_word': self.sync_word.hex() if self.sync_word else None,
            'crc_enabled': self.crc_enabled,
            'auto_ack': self.auto_ack,
            'node_id': self.node_id,
            'network_id': self.network_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RFConfig':
        """Create from dictionary."""
        sync_word = bytes.fromhex(data['sync_word']) if data.get('sync_word') else None
        return cls(
            frequency=data['frequency'],
            power=data['power'],
            data_rate=data['data_rate'],
            modulation=data['modulation'],
            bandwidth=data['bandwidth'],
            devitation=data['devitation'],
            sync_word=sync_word,
            crc_enabled=data.get('crc_enabled', True),
            auto_ack=data.get('auto_ack', False),
            node_id=data.get('node_id'),
            network_id=data.get('network_id')
        )
    
    def clone(self, **updates: Any) -> 'RFConfig':
        """Create a copy with updated fields.
        
        Args:
            **updates: Fields to update
            
        Returns:
            RFConfig: New instance with updated fields
        """
        data = self.to_dict()
        data.update(updates)
        return self.from_dict(data)


@dataclass
class DeviceStatus:
    """Device status information.
    
    This class provides a comprehensive view of the device's current state,
    including power management, connectivity, and system health metrics.
    """
    power_state: PowerState
    uptime: float
    signal_metrics: Optional[SignalMetrics] = None
    memory: Optional[MemoryUsage] = None
    temperature: Optional[float] = None
    voltage: Optional[float] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'power_state': self.power_state.name,
            'uptime': round(self.uptime, 2),
            'signal_metrics': self.signal_metrics.to_dict() if self.signal_metrics else None,
            'memory': self.memory.to_dict() if self.memory else None,
            'temperature': round(self.temperature, 1) if self.temperature is not None else None,
            'voltage': round(self.voltage, 2) if self.voltage is not None else None,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DeviceStatus':
        """Create from dictionary."""
        signal_metrics = SignalMetrics.from_dict(data['signal_metrics']) if data.get('signal_metrics') else None
        memory = MemoryUsage.from_dict(data['memory']) if data.get('memory') else None
        
        timestamp = (
            datetime.fromisoformat(data['timestamp']).replace(tzinfo=timezone.utc)
            if 'timestamp' in data
            else datetime.now(timezone.utc)
        )
        
        return cls(
            power_state=PowerState[data['power_state']],
            uptime=data['uptime'],
            signal_metrics=signal_metrics,
            memory=memory,
            temperature=data.get('temperature'),
            voltage=data.get('voltage'),
            timestamp=timestamp
        )
    
    def is_healthy(self) -> bool:
        """Check if the device is in a healthy state."""
        if self.power_state not in (PowerState.ACTIVE, PowerState.LOW_POWER):
            return False
            
        if self.memory and self.memory.usage_percent > 90:  # 90% memory usage
            return False
            
        if self.temperature is not None and self.temperature > 85:  # 85°C
            return False
            
        if self.voltage is not None and self.voltage < 3.0:  # 3.0V
            return False
            
        return True
