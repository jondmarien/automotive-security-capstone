"""Packet class for RF signal capture and analysis."""
import time
from typing import Optional


class Packet:
    """Represents a captured RF packet with metadata.
    
    Args:
        rssi: Received Signal Strength Indicator in dBm
        freq: Frequency in MHz
        payload: Raw packet data as bytes
        timestamp: Optional Unix timestamp (defaults to current time)
    """
    def __init__(self, rssi: int, freq: float, payload: bytes, timestamp: Optional[float] = None):  # noqa: E501
        self.rssi = rssi
        self.freq = freq
        self.payload = payload
        self.timestamp = timestamp or time.time()
        self.signature = self._generate_signature()
    
    def _generate_signature(self) -> str:
        """Generate a unique signature for duplicate detection."""
        if not self.payload:
            raise ValueError("Payload cannot be empty")
        if self.freq is None:
            raise ValueError("Frequency cannot be None")
        if self.rssi is None:
            raise ValueError("RSSI cannot be None")
            
        # Include all relevant fields in signature for duplicate detection
        return f"{self.freq}:{self.rssi}:{self.payload.hex()}"
    
    def to_dict(self) -> dict:
        """Convert packet to dictionary for serialization."""
        return {
            'rssi': self.rssi,
            'freq': self.freq,
            'payload': self.payload.hex(),
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Packet':
        """Create Packet from dictionary."""
        return cls(
            rssi=data['rssi'],
            freq=data['freq'],
            payload=bytes.fromhex(data['payload']),
            timestamp=data['timestamp']
        )
